import datetime
import os

from flask import Flask, flash, request, redirect, render_template, jsonify
from werkzeug.utils import secure_filename

from src import NDVI_Calc, ProccessShape,ClipImage

# initialize the web app
app = Flask(__name__)

uploadPath = 'Static\\Uploaded Images'
app.config["UPLOAD_FOLDER"] = uploadPath

# home page for the website
global ndviIMG


@app.route("/")
def index():
    return render_template("index.html")


# displays upload form page then uploads images to server
@app.route("/upload-img", methods=["GET", "POST"])
def uploadImg():
    if request.method == "POST":

        global blueImgFilename
        global greenImgFilename
        global redImgFilename
        global red_edgeImgFilename
        global niImgFilename

        # check to see if all of the required files were uploaded
        if 'blueImg' not in request.files or 'greenImg' not in request.files or 'redImg' not in request.files \
                or 'red-edgeImg' not in request.files or 'near-InfraredImg' not in request.files:
            flash('No file part')
            return redirect(request.url)

        redImg = request.files['redImg']
        blueImg = request.files['blueImg']
        greenImg = request.files['greenImg']
        red_edgeImg = request.files['red-edgeImg']
        niImg = request.files['near-InfraredImg']

        if redImg.filename == '' or blueImg.filename == '' or greenImg.filename == '' or red_edgeImg.filename == '' or niImg.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # add the current date and time to the filenames to avoid overwriting files with the same names
        blueImgFilename = str(datetime.datetime.now().time()).replace(":", ".") + secure_filename(blueImg.filename)
        greenImgFilename = str(datetime.datetime.now().time()).replace(":", ".") + secure_filename(greenImg.filename)
        redImgFilename = str(datetime.datetime.now().time()).replace(":", ".") + secure_filename(redImg.filename)
        red_edgeImgFilename = str(datetime.datetime.now().time()).replace(":", ".") + secure_filename(red_edgeImg.filename)
        niImgFilename = str(datetime.datetime.now().time()).replace(":", ".") + secure_filename(niImg.filename)

        # save the images to the specified folder in the server
        blueImg.save(os.path.join(app.config['UPLOAD_FOLDER'], blueImgFilename))
        redImg.save(os.path.join(app.config['UPLOAD_FOLDER'], redImgFilename))
        greenImg.save(os.path.join(app.config['UPLOAD_FOLDER'], greenImgFilename))
        red_edgeImg.save(os.path.join(app.config['UPLOAD_FOLDER'], red_edgeImgFilename))
        niImg.save(os.path.join(app.config['UPLOAD_FOLDER'], niImgFilename))

        return render_template("ImageUploaded.html")

    return render_template("UploadForm.html")


# calls the ndvi function on the uploaded images and then displays the result
@app.route("/display-Img")
def proccessNDVI():
    ndvi = NDVI_Calc.NDVI_Calc()
    ndviIMG = ndvi.run(uploadPath + os.sep + redImgFilename, uploadPath + os.sep + niImgFilename)
    print(ndviIMG + '.png')
    return render_template("DisplayImage.html", imageType="NDVI Image", fileName="NDVI_Images/" + ndviIMG + ".png")


# map web page with drawing tools
@app.route("/maps")
def loadMaps():
    return render_template("maps.html")


# retrieves polygon coordinates from maps page and then calls function to save it as a shape file
@app.route("/saveshape", methods=['POST'])
def saveShape():
    print("shape saved...")
    shapeLat = request.form.getlist('shapeLatitude[]', type=float)
    shapeLng = request.form.getlist('shapeLong[]', type=float)

    if shapeLat and shapeLng:
        coords = []
        for i in range(len(shapeLat)):
            point = [shapeLat[i], shapeLng[i]]
            coords.append(point)

        poly = ProccessShape.createPolygon(coords)
        shpFilename = str(datetime.datetime.now().date()) + str(datetime.datetime.now().time()).replace(':', '.') + "-shape"
        ProccessShape.writeShapefile(poly, shpFilename)
        ClipImage.clip(shpFilename)
        return jsonify({'success': 'File Saved'})

    return jsonify({'error': 'Error: No Shape Selected'})


# getShapeImage(shape)


if __name__ == '__main__':
    app.run()
