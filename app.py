from tensorflow.keras.applications.imagenet_utils import preprocess_input, decode_predictions
# coding=utf-8
import sys
import os
import glob
import re
import numpy as np

# Keras
from keras.applications.imagenet_utils import preprocess_input, decode_predictions
from keras.models import load_model
from keras.preprocessing import image

# Flask utils
import argparse
import io
import os
from PIL import Image
import cv2
import numpy as np
from torchvision.models import detection
import sqlite3
import torch
from torchvision import models
from ultralytics import YOLO

from flask import Flask, render_template, request, redirect, Response
from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
import sqlite3
import pandas as pd
import numpy as np
import pickle
import sqlite3
import random

import smtplib 
from email.message import EmailMessage
from datetime import datetime

import pathlib
temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath



app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'static/output'
app.config['MODEL_PATH1'] = 'best.pt'

model1 = YOLO(app.config['MODEL_PATH1'])

UPLOAD_FOLDER = 'static/uploads/'

# allow files of a specific type
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# function to check the file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

model_path1 = 'ensemble.h5'

CTS1 = load_model(model_path1,  compile=False)


from tensorflow.keras.preprocessing.image import load_img, img_to_array

def model_predict1(image_path,model):
    print("Predicted")
    image = load_img(image_path,target_size=(128,128))
    image = img_to_array(image)
    image = image/255
    image = np.expand_dims(image,axis=0)
    
    result = np.argmax(model.predict(image))
    print(result)
    #prediction = classes2[result]  
    
    if result == 0:
        return "WASTE TYPE IS CARDBOARD!","result.html"        
    elif result == 1:
        return "WASTE TYPE IS GLASS!","result.html"
    elif result == 2:
        return "WASTE TYPE IS METAL!","result.html"
    elif result == 3:
        return "WASTE TYPE IS PAPER!","result.html"
    elif result == 4:
        return "WASTE TYPE IS PLASTIC","result.html"
    elif result == 5:
        return "WASTE TYPE IS TRASH!","result.html"
    
    

@app.route("/about")
def about():
    return render_template("about.html")


@app.route('/')
@app.route('/home')
def home():
	return render_template('home.html')


@app.route('/logon')
def logon():
	return render_template('signup.html')

@app.route('/login')
def login():
	return render_template('signin.html')


@app.route('/index1')
def index1():
	return render_template('index1.html')


@app.route('/index')
def index():
	return render_template('index.html')



@app.route('/predict1',methods=['GET','POST'])
def predict1():
    print("Entered")
    
    print("Entered here")
    file = request.files['file'] # fet input
    filename = file.filename        
    print("@@ Input posted = ", filename)
        
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    print("@@ Predicting class......")
    pred, output_page = model_predict1(file_path,CTS1)
              
    return render_template(output_page, pred_output = pred, img_src=UPLOAD_FOLDER + file.filename)


@app.route("/signup")
def signup():
    global otp, username, name, email, number, password
    username = request.args.get('user','')
    name = request.args.get('name','')
    email = request.args.get('email','')
    number = request.args.get('mobile','')
    password = request.args.get('password','')
    otp = random.randint(1000,5000)
    print(otp)
    msg = EmailMessage()
    msg.set_content("Your OTP is : "+str(otp))
    msg['Subject'] = 'OTP'
    msg['From'] = "vandhanatruprojects@gmail.com"
    msg['To'] = email
    
    
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("vandhanatruprojects@gmail.com", "pahksvxachlnoopc")
    s.send_message(msg)
    s.quit()
    return render_template("val.html")

@app.route('/predict_lo', methods=['POST'])
def predict_lo():
    global otp, username, name, email, number, password
    if request.method == 'POST':
        message = request.form['message']
        print(message)
        if int(message) == otp:
            print("TRUE")
            con = sqlite3.connect('signup.db')
            cur = con.cursor()
            cur.execute("insert into `info` (`user`,`email`, `password`,`mobile`,`name`) VALUES (?, ?, ?, ?, ?)",(username,email,password,number,name))
            con.commit()
            con.close()
            return render_template("signin.html")
    return render_template("signup.html")

@app.route("/signin")
def signin():

    mail1 = request.args.get('user','')
    password1 = request.args.get('password','')
    con = sqlite3.connect('signup.db')
    cur = con.cursor()
    cur.execute("select `user`, `password` from info where `user` = ? AND `password` = ?",(mail1,password1,))
    data = cur.fetchone()

    if data == None:
        return render_template("signin.html")    

    elif mail1 == str(data[0]) and password1 == str(data[1]):
        return render_template("index.html")
    else:
        return render_template("signin.html")

@app.route("/notebook1")
def notebook1():
    return render_template("Classification.html")

@app.route("/notebook2")
def notebook2():
    return render_template("Detection.html")
   
def process_image1(image_path, output_path):
    img = cv2.imread(image_path)
    results = model1.predict(source=img)

    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].int().tolist()
            confidence = box.conf[0]
            class_id = box.cls[0]
            label = f"{model1.names[int(class_id)]} {confidence:.2f}"
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    cv2.imwrite(output_path, img)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return redirect(url_for('static', filename=f'output/{filename}'))


@app.route('/predict2', methods=['GET', 'POST'])
def predict2():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return redirect(request.url)
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                output_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
                if file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    process_image1(file_path, output_path)
                
                return redirect(url_for('uploaded_file', filename=filename))
    return render_template('index1.html')



if __name__ == '__main__':
    app.run(debug=False)