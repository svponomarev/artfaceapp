#!/usr/bin/env python
# # -*- coding: utf-8 -*-
""" === main.py: main script for Flask server functionality=== """
import os
import sys
import uuid
import requests
import rfc6266
import json
import csv

from PIL import Image
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from werkzeug import secure_filename
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from StringIO import StringIO

from app.detection.detection import detect_faces
from app.matching.matching import match_faces
from app.detection.prediction.prediction import params_prediction
from app.stylization.colorization.colorization import colorize_image
from app.stylization.equalization.equalization import equalize_image
from app.stylization.art_style_transfer import apply_art_style
from app.stylization.photo_style_transfer import apply_photo_style

UPLOAD_FOLDER = 'app/static/uploads' # path to the folder with processed images
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg']) # allowed extensions for uploading image files on server
SMALLEST_SIDE = 384 # all images on the final stylization step will be resized in such way that this size will be for its smallest side
STYLES_DB = 'app/static/db/db_styles.csv' # path to the csv file with articles about art and photo styles

# initializing Flask server
app = Flask(__name__, static_url_path='/app/static')
app.secret_key = os.urandom(20)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMPLATES_AUTO_RELOAD'] = True

# creating Faces database structure for sqlite engine
engine = create_engine('sqlite:///app/static/db/faces.db', echo=False)
Base = declarative_base(engine) 
########################################################################
class Faces(Base):
    """database for descriptions of famous people of XX century"""
    __tablename__ = 'faces'
    __table_args__ = {'autoload':True}
    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'         : self.id,
            'decade'    : self.decade,
            'gender'    : self.gender,
            'name'      : self.name,
            'birth'     : self.birth,
            'death'     : self.death,
            'quote'     : self.quote,
            'descr'     : self.descr,
            'path'      : self.path,
            'wiki'      : self.wiki,
            'info'      : self.info,
            'source'    : self.source
       }
#----------------------------------------------------------------------
def loadSession():
    """loading session for sqlite engine"""
    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def allowed_file(filename):
    """checks if uploaded file has allowed image extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_smallest(img, smallest_side):
    """resize image keeping aspect ratio to smallest side"""
    width, height = img.size
    scale = float(smallest_side) / width if height > width else float(smallest_side) / height
    new_height = int(height * scale)
    new_width = int(width * scale)
    return img.resize([new_width,new_height], Image.ANTIALIAS) 

@app.route('/')
def index():
    """render index page"""
    return render_template("index.html")

@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    """process image file uploading"""
    if request.method == 'POST':
        image_url = request.form.get('image-url')
        file = None
        filename = ""
        if image_url is not None: # if user sending url for file to upload
            r = requests.get(image_url)
            file = StringIO(r.content)
            if 'content-disposition' in r.headers: # check if image file has standard headers
                d = r.headers['content-disposition']
                filename = rfc6266.parse_headers(d).filename_unsafe
            else:
                filename = image_url.rsplit('/', 1)[1]
            if file is None:
                flash('Failed to download image from url')
                return redirect(url_for('index'))
        # check if the post request has the file part
        elif 'file' in request.files:
            file = request.files['file'].stream
            filename = request.files['file'].filename
        elif request.form.get('image-path') is not None:
            file = request.form.get('image-path')
            filename = file.rsplit('/', 1)[1]
        else:
            flash('No file part')
            return redirect(url_for('index'))         
        # if user does not select file, browser also
        # submit an empty part without filename
        if filename == '':
            flash('No selected file!')
            return redirect(url_for('index'))
        if file:
            if allowed_file(filename):
                filename = str(uuid.uuid4()) + ".jpg" # generate new filename using uuid
                secure_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                try:
                    im = Image.open(file)
                    im.save(secure_path, "JPEG") # store image inside upload folder with new name
                    session["img_path"] = secure_path # save img_path in current session variables
                    return redirect(url_for('detection'))
                except IOError:
                    flash("cannot open this image")
                    return redirect(url_for('index'))
            else:
                flash('Only image files are allowed!')
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/detection', methods = ['GET', 'POST'])
def detection():
    """process uploaded image and detect faces"""
    if "img_path" in session:
        img_path = session["img_path"] # load img_path from current session variables
        faces_num, img_crop_path, img_rect_path, img_mask_path, ratio = detect_faces(img_path) # get founded number of faces and 3 processed images
        session["img_crop_path"] = img_crop_path # save path to the image with cropped face rectangle in current session
        if faces_num == -1:
            flash("Cannot find any face on this image, try another image.")
            return redirect(url_for('index'))
        return render_template("detection.html", img=img_path, img_rect=img_rect_path, img_mask=img_mask_path, ratio=ratio)
    else:
        return redirect(url_for('index'))
    

@app.route('/matching', methods = ['GET', 'POST'])
def matching():
    """process uploaded image and find matching faces"""  
    img_path = request.form.get('image-path')
    gender = request.form.get('gender')
    if img_path is None or gender is None:
        if "img_path" not in session:
            flash("Failed to process parameters, please try again")
            return redirect(url_for('index'))
        else: # fix for 502 bad gateway redirect
            flash("Minor server problems, loading matching page with default parameters")
            img_path = session["img_path"]
            gender = "all"
    top_faces, ratio = match_faces(img_path, gender) # find top-3 matched faces
    if top_faces == -1:
        flash("Cannot recognize face on this image, try again.")
        return redirect(url_for('index'))
    faces_id = [int(i[0]) for i in top_faces]
    faces_dist = [float(i[1]) for i in top_faces]

    s = loadSession()
    face_info = s.query(Faces).filter(Faces.id.in_(faces_id)).all() # get info about top-3 faces from database
    s.close()
    if len(face_info) < 3:
        flash("Cannot match face on this image, try again.")
        return redirect(url_for('index'))

    # calculate ratios for top-3 images
    ratios = list()
    ratios.append(ratio)
    for face in face_info:
        orig_image = Image.open(face.path)
        width, height = orig_image.size
        ratio = float(height)/width
        ratios.append(ratio)

    return render_template("matching.html", img=img_path, dist=faces_dist, info=face_info, ratios=ratios)

@app.route('/stylization', methods = ['GET', 'POST'])
def stylization():
    """process uploaded image, resize it and render initial page for stylization"""
    if request.method == 'POST': 
        img_path = request.form.get('image-path')
        decade = request.form.get('decade')
        if img_path is None or decade is None:
                flash("Cannot process POST parameters.")
                return redirect(url_for('index'))
        im = Image.open(img_path)
        im = resize_smallest(im, SMALLEST_SIDE) # resize input image for computational speed
        filename = str(uuid.uuid4()) + ".jpg"
        secure_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        im.save(secure_path, "JPEG")
        width, height = im.size
        ratio = float(height)/width
        return render_template("stylization.html", orig_img=img_path, img=secure_path, decade=decade, ratio=ratio)
    else:
        return redirect(url_for('index'))

@app.route('/art', methods = ['GET', 'POST'])
def art():
    """render initial page with articles about art and photo styles""" 
    form_data = request.form
    if form_data and 'decade' in form_data and 'form' in form_data:
        decade = int(form_data['decade'])
        form = form_data['form']
    else:
        decade = 1910
        form = "photo"
    return render_template("art.html", decade=decade, form=form)

@app.route('/people', methods = ['GET', 'POST'])
def people():
    """render initial page with information about famous people"""
    return render_template("people.html")

@app.route('/technology', methods = ['GET', 'POST'])
def technology():
    """render page with information about used technologies"""
    return render_template("technology.html")

@app.route('/about', methods = ['GET'])
def about():
    """render page with general information about project"""
    return render_template("about.html")

@app.route('/ajax_art', methods = ['POST'])
def ajax_art():
    """process ajax request to generate articles about art and photo styles from csv file"""
    json = request.get_json()
    if not json:
        return
    form = json['form']
    decade = int(json['decade']) 
    styles_num = 20 # 20 styles: 10 for art, 10 for photo
    style_info = ""
    with open(STYLES_DB, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader) # skip row with column names
        for i in range(styles_num):
            style_record = next(reader)
            cur_decade = int(style_record[0])
            cur_form = style_record[1]
            if cur_decade == decade and cur_form == form: # find info about chosen decade and art form
               style_info = unicode(style_record[2], errors="ignore") # ignore errors related with non-unicode symbols in articles
               break
    return jsonify(style_info=style_info)

@app.route('/ajax_people', methods = ['POST'])
def ajax_people():
    """process ajax request to generate information about famous people from database"""
    json = request.get_json()
    if not json:
        return
    gender = json['gender']
    decade = json['decade']
    s = loadSession()
    face_info = s.query(Faces).filter(Faces.decade == decade).filter(Faces.gender == gender).all() # find people for chosen decade and gender
    s.close()
    return jsonify(face=[i.serialize for i in face_info]) # serialize fields of record in Faces database before generating json response

@app.route('/ajax_prediction', methods = ['POST'])
def ajax_prediction():
    """process ajax request to predict age of person using cropped image with face rectangle"""
    json = request.get_json()
    if not json:
        return
    img_path = session["img_crop_path"]
    age, age_prob, gender, gender_prob = params_prediction(img_path)
    # convert certainty of prediction in percents
    age_prob = int(age_prob * 100)
    gender_prob = int(gender_prob * 100)
    return jsonify(age=str(age), age_prob=str(age_prob), gender=str(gender), gender_prob=str(gender_prob))

@app.route('/ajax_color', methods = ['POST'])
def ajax_color():
    """process ajax request to colorize input image using neural network or convert it to monochrome"""
    json = request.get_json()
    if not json:
        return
    img_path = json['path']
    decade = json['decade']
    clr_path = colorize_image(img_path, decade) # returns path to the colorized image in uploads folder
    return jsonify(clr_path=clr_path)

@app.route('/ajax_equal', methods = ['POST'])
def ajax_equal():
    """process ajax request to equalize input image"""
    json = request.get_json()
    if not json:
        return
    img_path = json['path']
    eql_path = equalize_image(img_path) # returns path to the equalized image in uploads folder
    return jsonify(eql_path=eql_path) 

@app.route('/ajax_photo_style', methods = ['POST'])
def ajax_photo_style():
    """process ajax request to stylize image in photographic style of selected decade"""
    json = request.get_json()
    if not json:
        return
    img_path = json['path']
    decade = int(json['decade'])
    processed_path = apply_photo_style(img_path, decade) # returns path to the stylized image in uploads folder

    im = Image.open(processed_path)
    width, height = im.size
    ratio = float(height)/width

    return jsonify(processed_path=processed_path, photo_ratio=ratio)

@app.route('/ajax_art_style', methods = ['POST'])
def ajax_art_style():
    """process ajax request to stylize image in art style of selected decade"""
    json = request.get_json()
    if not json:
        return
    orig_path = json['orig_path'] # orig_path is used in 1960s warhol style transfer for face detection on image with original size
    eql_path = json['eql_path']
    decade = int(json['decade'])
    style_num = int(json['style_num']) # style_num shows one of three available styles in each decade
    processed_path, style1, style2, style3 = apply_art_style(orig_path, eql_path, decade, style_num) # returns path to the stylized image and styles names

    im = Image.open(processed_path)
    width, height = im.size
    ratio = float(height)/width

    return jsonify(processed_path=processed_path, style1=style1, style2=style2, style3=style3, art_ratio=ratio)

@app.errorhandler(404)
def page_not_found(e):
    """process page not found error"""
    return render_template('error404.html'), 404

if __name__ == '__main__':
    """starts Flask server"""
    app.run(host='0.0.0.0', debug=True, port=80)  # Only for debugging while developing
    
