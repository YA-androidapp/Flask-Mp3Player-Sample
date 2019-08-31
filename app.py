#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 YA-androidapp(https://github.com/YA-androidapp) All rights reserved.

from datetime import datetime
from flask import Flask, jsonify, make_response, redirect, render_template, request, send_file, send_from_directory
import os
import sys
import werkzeug

app = Flask(__name__)
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


import hashlib

@app.route('/upload/music', methods=['POST'])
def post_upload_music():
    if 'files' not in request.files:
        return make_response(jsonify({'result': 'file not selected'}))

    count_success = 0
    filenamepair_success = {}
    upload_files = request.files.getlist('files')
    for file in upload_files:
        filename = file.filename

        hash = hashlib.sha256(file.read()).hexdigest()
        save_filename = hash + os.path.splitext(filename)[1]
        file.seek(0)

        # save_filename = datetime.now().strftime('%Y%m%d_%H%M%S_') + werkzeug.utils.secure_filename(filename)
        save_filepath = os.path.join(app.config['UPLOAD_DIR'], save_filename)

        if os.path.exists(save_filepath) == False:
            file.save(save_filepath)
            count_success += 1
            filenamepair_success[file.filename] = save_filename
    mes = '{} files uploaded'.format(count_success) if count_success > 1 else 'a file uploaded'
    return make_response(jsonify({'result': mes, 'filename': filenamepair_success}))


@app.errorhandler(werkzeug.exceptions.RequestEntityTooLarge)
def handle_over_max_file_size(error):
    return redirect(request.url)


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_DIR'], exist_ok=True)
    app.run(host='localhost', port=3000)
