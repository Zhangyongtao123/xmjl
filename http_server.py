#!/usr/bin/env python
# -*- coding:utf-8 -*-
from flask import Flask, jsonify, abort
from flask import request

app = Flask(__name__)


@app.route('/', methods=['POST'])
def index():
    print(request.content_length)
    print(request.get_data().decode().replace('"', '\\"'))
    print(request.get_json())
    return jsonify({'task': "you"}), 201


if __name__ == '__main__':
    app.run(
        host='localhost',
        port=5000,
        debug=True
    )