#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 YA-androidapp(https://github.com/YA-androidapp) All rights reserved.
#
# Required:
#  python -m pip install flask flask_jwt flask_sqlalchemy mutagen

from collections import defaultdict
from datetime import datetime
from flask import Flask, abort, jsonify, make_response, redirect, render_template, request, Response, send_file, send_from_directory, url_for
from flask_jwt import jwt_required, current_identity, JWT
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from flask_sqlalchemy import SQLAlchemy
from mutagen.mp3 import MP3
import hashlib
import os
import sys


# Init
app = Flask(__name__)
app.config['ALLOWED_EXTENSIONS'] = set(['mp3'])
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 * 1024  # 10GB
app.config['UPLOAD_DIR'] = os.path.join('.', 'data')

# SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'app.db')

# JWT
app.config['SECRET_KEY'] = 'develop'
app.config['JWT_AUTH_USERNAME_KEY'] = 'email'
app.config['JWT_AUTH_URL_RULE'] = '/auth/token'

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = '!SECRETKEY!'

db = SQLAlchemy(app)


# Models

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    pwdhash = db.Column(db.String(255))

    def __init__(self, email, password):
        self.email = email
        self.set_password(password)

    def __repr__(self):
        return '<User %r>' % self.email

    def set_password(self, password):
        self.pwdhash = hashlib.sha256(password.encode('UTF-8')).hexdigest()

    def check_password(self, password):
        return self.pwdhash == hashlib.sha256(password.encode('UTF-8')).hexdigest()


# Functions

def allowed_filename(filename):
    try:
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
    except Exception as e:
        print(e)
    return False


def allowed_filecontent(filename):
    try:
        audio = MP3(filename)
        if audio.info.length > 0:
            return True
    except Exception as e:
        print(e)
    return False


def authoricate(email, password):
    users = db.session.query(User).filter_by(email=email).all()
    target = next((user for user in users if user.email == email), None)
    is_auth = True if target is not None and target.pwdhash == hashlib.sha256(password.encode('UTF-8')).hexdigest() else False
    return target if is_auth else None


def identity(payload):
    users = db.session.query(User).all()
    user_id = payload['identity']
    target = next((user for user in users if user.id == user_id), None)
    return target


# Endpoints

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    if(request.method == "POST"):
        # ユーザーチェック
        if(authoricate(request.form["email"], request.form["password"])):
            # ユーザーが存在した場合はログイン
            login_user(db.session.query(User).filter_by(email=request.form["email"]).first())
            return Response('logined')
        else:
            return abort(401)
    else:
        return render_template("login.html")

# ログアウトパス
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template("login.html")


@app.route('/music/<string:music_id>', methods=['GET'])
@jwt_required()
def music_id(music_id):
    music_id = 'h.mp3' if music_id is None or music_id == '' else music_id
    filename = os.path.join(app.config['UPLOAD_DIR'], music_id)
    return send_file(filename, as_attachment=False, attachment_filename=filename, mimetype='audio/mpeg')


@app.route('/upload/music', methods=['GET'])
@login_required
def get_upload_music():
    return render_template('upload.html')


# API

@app.route('/upload/music', methods=['POST'])
def post_upload_music():
    if 'files' not in request.files:
        return make_response(jsonify({'result': 'file not selected'}))

    count_success = 0
    filenamepair_success = {}
    upload_files = request.files.getlist('files')
    for file in upload_files:
        filename = file.filename

        if allowed_filename(filename):
            hash = hashlib.sha256(file.read()).hexdigest()
            save_filename = hash + os.path.splitext(filename)[1]
            file.seek(0)
            save_filepath = os.path.join(
                app.config['UPLOAD_DIR'], save_filename)

            if os.path.exists(save_filepath) == False:
                file.save(save_filepath)
                if allowed_filecontent(save_filepath):
                    count_success += 1
                    filenamepair_success[file.filename] = save_filename
                else:
                    os.remove(save_filepath)

    if count_success == 0:
        return make_response(jsonify({'result': 'file not uploaded'}))
    else:
        mes = '{} files uploaded'.format(
            count_success) if count_success > 1 else 'a file uploaded'
        return make_response(jsonify({'result': mes, 'filename': filenamepair_success}))


# Init

@app.before_first_request
def init():
    db.create_all()

    email = 'ya.androidapp@gmail.com'
    users = db.session.query(User).filter_by(email=email).all()
    if len(users) == 0:
        user = User(email, 'PASSWORD')
        db.session.add(user)
        db.session.commit()


@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return redirect(url_for('login'))


@login_manager.user_loader
def load_user(email):
    try:
        return db.session.query(User).filter_by(email=email).first()
    except:
        return None


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_DIR'], exist_ok=True)

    jwt = JWT(app, authoricate, identity)

    app.run(host='localhost', port=3000)
