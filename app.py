#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 YA-androidapp(https://github.com/YA-androidapp) All rights reserved.

from datetime import datetime
from flask import Flask, jsonify, make_response, redirect, render_template, request, send_file, send_from_directory
from mutagen.mp3 import MP3
import hashlib
import os
import sys

app = Flask(__name__)
app.config['ALLOWED_EXTENSIONS'] = set(['mp3'])
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 * 1024  # 10GB
app.config['UPLOAD_DIR'] = os.path.join('.', 'data')


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/music/<string:music_id>', methods=['GET', 'POST'])
def music_id(music_id):
    filename = os.path.join(app.config['UPLOAD_DIR'], 'k.mp3')
    return send_file(filename, as_attachment=False, attachment_filename=filename, mimetype='audio/mpeg')


@app.route('/upload/music', methods=['GET'])
def get_upload_music():
    return render_template('upload.html')


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
            save_filepath = os.path.join(app.config['UPLOAD_DIR'], save_filename)

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
        mes = '{} files uploaded'.format(count_success) if count_success > 1 else 'a file uploaded'
        return make_response(jsonify({'result': mes, 'filename': filenamepair_success}))


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_DIR'], exist_ok=True)
    app.run(host='localhost', port=3000)
