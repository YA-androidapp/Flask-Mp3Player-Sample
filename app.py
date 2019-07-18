#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 YA-androidapp(https://github.com/YA-androidapp) All rights reserved.

from flask import Flask, make_response, render_template, send_file, send_from_directory

app = Flask(__name__, static_folder=None)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/music/<string:music_id>', methods=['GET', 'POST'])
def report1(music_id):
    filename = 'k.mp3'
    return send_file(filename, as_attachment = False, attachment_filename = filename, mimetype = 'audio/mpeg')

if __name__ == '__main__':
    app.run(host='localhost', port=3000)