import os
from application import app, ai_model, db
from flask import render_template, request, flash, jsonify, redirect, url_for, send_from_directory
from application.forms import LoginForm, RegisterForm
from application.models import Entry, UserData
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from PIL import Image
from matplotlib import image
from flask_cors import CORS, cross_origin
import re
import base64
import numpy as np
import json
import requests

# create the database if not exist
db.create_all()

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

#server URL
url = 'https://dl-model-devyn.herokuapp.com/v1/models/img_classifier:predict'


# add a new entry
def add_entry(new_entry):
    try:
        db.session.add(new_entry)
        db.session.commit()
        return new_entry.id

    except Exception as error:
        db.session.rollback()
        flash(error,"danger")
        return 'Not added.'

# get all entries of a particular user id
def get_all_entries(id):
    try:
        entries = Entry.query.filter(Entry.userid == id).all()
        return entries
    except Exception as error:
        db.session.rollback()
        flash(error,"danger") 
        return 0

# get a single entry by id
def get_entry(id):
    try:
        entries = Entry.query.filter(Entry.id == id)
        result = entries[0]
        return result
    except Exception as error:
        db.session.rollback()
        flash(error, "danger")
        return 0

# remove an entry
def remove_entry(id):
    try:
        entry = Entry.query.get(id)
        db.session.delete(entry)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        flash(error,"danger")

# remove an entry
def remove_all_entries(userid):
    try:
        entries = Entry.query.filter(Entry.userid == userid).all()
        for entry in entries:
            db.session.delete(entry)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        flash(error,"danger")

# parse the image and save it to a specified folder
def parseImage(imgData):
    # parse canvas bytes and save as output.png
    imgstr = re.search(b'base64,(.*)', imgData).group(1)

    # counter to ensure images filenames are unique
    i=0
    while os.path.exists("./application/static/images/sample%s.png" % i):
        i+=1

    with open('./application/static/images/sample%s.png' % i,'wb') as output:
        output.write(base64.decodebytes(imgstr))
    im = Image.open('./application/static/images/sample%s.png' % i).convert('RGB')
    im.save('./application/static/images/sample%s.png' % i)
    return 'sample%s.png' % i

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def make_prediction(instances):
    data = json.dumps({"signature_name": "serving_default", "instances": instances.tolist()})
    headers = {"content-type": "application/json"}
    json_response = requests.post(url, data=data, headers=headers)
    predictions = json.loads(json_response.text)['predictions']
    return predictions


# homepage
@app.route('/') 
@app.route('/index') 
@app.route('/home')
def index(): 
    return render_template("index.html", title="Home")

# homepage when logged in
@app.route('/') 
@app.route('/index2') 
@app.route('/home2')
@login_required
def index2(): 
    return render_template("index2.html", title="Home logged in", name=current_user.username)

# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    loginform = LoginForm()
    if request.method == 'POST' and loginform.validate_on_submit(): #check if the request is made using POST and form.validate_on_submit() will return False if at least one validator was not satisfied
        # find the user based on his/her email in the db
        user = UserData.query.filter_by(email=loginform.login_email.data).first()
        if user:
            if check_password_hash(user.password, loginform.login_password.data):
                # login user
                login_user(user)
                flash('Login successful')
                # redirect the user to the logged-in page
                return redirect(url_for('index2'))
            else:
                flash('Invalid password')
                return redirect(url_for('login'))
        # EDIT THIS!!
        else:
            flash('User not found.')
            return redirect(url_for('login'))

    else:
        print("Not logged in!")

    registerform = RegisterForm()
    
    if request.method == 'POST' and registerform.validate_on_submit():
        # get data from form
        username = registerform.register_username.data
        email = registerform.register_email.data
        password = registerform.register_password.data

        # generate password hash (80 characters long)
        hashed_password = generate_password_hash(password, method='sha256')

        # add user to db
        new_user = UserData(username = username, email = email, password = hashed_password)
        result = add_entry(new_user)

        # redirect user to login page
        return redirect(url_for('login'))
    else:
        print("Not added!")
    return render_template("login.html", title="Login or register", loginform=loginform, registerform=registerform, index=True)

# logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# Prediction form (We need to make use of this get_entries() function to populate the UI later, so we need it in the default and predict route)
@app.route('/dashboard',  methods=['GET','POST'])
@login_required
def predict_page():
    return render_template("dashboard.html", title="Dashboard", name=current_user.username)


# Display the predicted classification from webcam capture
@app.route("/predict", methods=['GET','POST'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
@login_required
def predict():
    if request.method == 'POST':
        # get the user id that is currently logged in
        userid = current_user.id

        # get data from drawing canvas and save as image
        filename = parseImage(request.get_data())

        # load the image with Pillow
        captured_image = Image.open(f'./application/static/images/{filename}')

        # convert the image to grayscale
        gs_image = captured_image.convert(mode='L')

        # save the grayscale image
        gs_image.save(f'./application/static/images/{filename}')
    
        # load image as pixel array
        data = image.imread(f'./application/static/images/{filename}')

        # reshape the array into a shape the model can predict
        data_reshaped = data.reshape(1, data.shape[0], data.shape[1], 1)

        # predict
        # result = ai_model.predict(data_reshaped)
        result = make_prediction(data_reshaped)

        print(result)

        # get the class with the highest probability prediction
        predicted_class = np.argmax(result, axis = 1)[0]

        # predicted_class is an index number, so we use class_names to get the actual alphabet
        class_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G',
               'H', 'I', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y' ]
        predicted_alphabet = class_names[predicted_class]

        # store the filepath of the image
        filepath = f'../static/images/{filename}'

        # add the prediction entry into db
        new_entry = Entry(  userid = userid, filename = filename, filepath = filepath, prediction=predicted_alphabet, predicted_on=datetime.now())
        add_entry(new_entry)

        resp = {'status': 'Uploaded',
        'prediction': predicted_alphabet}
        print('Captured!')

        return resp
    else:
        resp_err = {'status': 'Not Uploaded',
        'prediction': 'none'}
        print('Not captured.')
        return resp_err

# Display the predicted classification from upload image
@app.route("/upload", methods=['GET','POST'])
@login_required
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'photo' not in request.files:
            return redirect(request.url)
        photo = request.files['photo']
        # if user does not select file, browser also
        # submit an empty part without filename
        if photo.filename == '':
            flash('No selected file')
            print('No selected file')
            return redirect(request.url)
        if photo and allowed_file(photo.filename):
            # save the photo in the images folder
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # load the image
            uploaded_image = Image.open(f'./application/static/images/{filename}')

            # resize image and ignore original aspect ratio
            uploaded_image_resized = uploaded_image.resize((28,28))

            # convert the image to grayscale
            gs_image = uploaded_image_resized.convert(mode='L')

            # save the resized grayscale image
            gs_image.save(f'./application/static/images/{filename}')

            # load image as pixel array
            data = image.imread(f'./application/static/images/{filename}')

            # reshape the array into a shape the model can predict
            data_reshaped = data.reshape(1, data.shape[0], data.shape[1], 1)

            # predict
            # result = ai_model.predict(data_reshaped)
            result = make_prediction(data_reshaped)

            # get the class with the highest probability prediction
            predicted_class = np.argmax(result, axis = 1)[0]

            # predicted_class is an index number, so we use class_names to get the actual alphabet
            class_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G',
                'H', 'I', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y' ]
            predicted_alphabet = class_names[predicted_class]

            
            # get the user id that is currently logged in
            userid = current_user.id

            # store the filepath of the image
            filepath = f'../static/images/{filename}'
            
            # store the image to db
            new_entry = Entry(  userid = userid, filename = filename, filepath = filepath, prediction=predicted_alphabet, predicted_on=datetime.now())
            add_entry(new_entry)

            resp = {'status': 'Uploaded',
            'prediction': predicted_alphabet}
            return jsonify(resp)

    resp = {'status': 'Not Uploaded',
            'prediction': 'none'}
    return jsonify(resp)

# User prediction history
@app.route('/history',  methods=['GET','POST'])
@login_required
def history():
    return render_template("history.html", title="View your prediction history", entries=get_all_entries(current_user.id), name=current_user.username, userid=current_user.id)

# Remove a single entry
@app.route("/remove", methods=["POST"])
def remove():
    # remove that entry from the db
    req = request.form
    id = req["id"]
    remove_entry(id)

    # remove that entry from the image folder
    filename = req["filename"]
    try:
        os.remove(f'./application/static/images/{filename}')
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    except:
        print("Unexpected error.")

    return render_template(
        "history.html",
        title="View your prediction history",
        entries=get_all_entries(current_user.id),
        index=True,
        name=current_user.username,
        userid=current_user.id
    )

# Remove all entries
@app.route("/removeall", methods=["POST"])
def removeall():
    # remove all the images from the images folder
    req = request.form
    id = req["userid"]
    entries = get_all_entries(int(id))
    for entry in entries:
        print(entry.filename)
        print(type(entry.filename))
        try:
            os.remove(f'./application/static/images/{entry.filename}')
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))
        except:
            print("Unexpected error.")

    # remove all entries of that user from the db
    remove_all_entries(id)

    return render_template(
        "history.html",
        title="View your prediction history",
        entries=get_all_entries(current_user.id),
        index=True,
        name=current_user.username,
        userid=current_user.id
    )


# Add a single entry
@app.route("/api/add", methods=["POST"])
def api_add():
    # retrieve the json file posted from client
    data = request.get_json()

    # retrieve each field from the data
    userid = data["userid"]
    filename = data["filename"]
    filepath = data["filepath"]
    prediction = data["prediction"]
    predicted_on = datetime.now()

    # create an Entry object store all data for db action
    new_entry = Entry(  userid=userid, filename=filename, filepath=filepath, prediction=prediction, predicted_on=predicted_on)

    # invoke the add entry function to add entry
    result = add_entry(new_entry)

    # return the result of the db action
    return jsonify({"id": result})

# Get a single entry
@app.route("/api/get/<id>", methods=["GET"])
def api_get(id):
    # retrieve the entry using id from client
    entry = get_entry(int(id))
    # Prepare a dictionary for json conversion
    data = {
            'id': entry.id,
            'userid': entry.userid,
            'filename': entry.filename, 
            'filepath': entry.filepath,
            'prediction': entry.prediction,
            'predicted_on': entry.predicted_on
        }
    
    # Convert the data to json
    result = jsonify(data)
    return result  # response back

# Get all entries of a particular id
@app.route("/api/getall/<id>", methods=["GET"])
def api_getall(id):
    # retrieve all entries
    entries = get_all_entries(int(id))

    # create an empty list
    data = []
    for entry in entries:
        print(f'entry {entry}')
        entryDict = {
            'userid': entry.userid,
            'filename': entry.filename,
            'filepath': entry.filepath, 
            'prediction': entry.prediction,
            'predicted_on': entry.predicted_on
        }
        data.append(entryDict)
    
    # Convert the data to json
    result = jsonify(data)
    return result  # response back

# Remove a specific entry by id
@app.route("/api/delete/<id>", methods=['GET'])
def api_delete(id): 
    entry = remove_entry(int(id))
    return jsonify({'result':'ok'})

# Remove all entries by userid
@app.route("/api/delete_all/<userid>", methods=['GET', 'POST'])
def api_delete_all(userid): 
    remove_all_entries(int(userid))
    return jsonify({'result':'ok'})
