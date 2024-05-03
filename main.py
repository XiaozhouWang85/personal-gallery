#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import urllib.parse
import os
import tempfile
from flask import Flask, make_response, render_template, request, send_from_directory
import datetime
from google.cloud import storage
from google import auth

app = Flask(__name__, static_url_path='/static')

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'photo-gallery-336913-a3e805ba7d36.json'

PROJECT = 'photo-gallery-336913'
GCS_BUCKET_NAME = 'xiaozhou-photo-gallery'
GCS_SUBFOLDER = 'gallery/'
GCS_CLIENT = storage.Client(PROJECT)
GCS_BUCKET = GCS_CLIENT.bucket(GCS_BUCKET_NAME)

def get_gcs_json(filename):
    blob = GCS_BUCKET.blob(GCS_SUBFOLDER + filename)
    data = json.loads(blob.download_as_string(client=None))
    return data

def month_to_string(month):
    return datetime.date(int(month[:4]), int(month[4:6]), 1).strftime('%B %Y')

@app.route("/_ah/warmup")
def warmup():
    return make_response("Warm up", 200)

@app.route("/")
def index():
    gallery_data = get_gcs_json('image_metadata/gallery.json')
    new_list = []
    for year_dict in gallery_data:
        month_list = [ {"path": month, "title": month_to_string(month)} for month in year_dict['months']]
        new_list.append({
            "year":year_dict['year'],
            "months":month_list
        })
    return render_template("index.html", gallery_list=new_list)

@app.route('/get_image/<object>')
def get_image(object):
    object_path = urllib.parse.unquote(object)
    object_name = os.path.basename(object_path)
    blob = GCS_BUCKET.blob(os.path.join(GCS_SUBFOLDER, object_path))
    with tempfile.TemporaryDirectory() as tmpdirname:
        fullpath = os.path.join(tmpdirname, object_name)
        blob.download_to_filename(fullpath)
        return send_from_directory(tmpdirname, object_name)

@app.route("/gallery", methods=['GET'])
def gallery():
    args = request.args
    month = args.get("month")
    folder_date = month_to_string(month)
    
    # Load the images_data from gcs
    images_data = get_gcs_json('image_metadata/{}.json'.format(month))
    images_data_list = [{**images_data[image], "name": image} for image in images_data.keys()]
    images_data_list = list(sorted(images_data_list, key=lambda x:x['unix_time']))

    for image in images_data_list:
        image['src'] = urllib.parse.quote(image['src'], safe='')
        image['thumbnail'] = urllib.parse.quote(image['thumbnail'], safe='')

    for image in images_data_list:
        if image["type"] == "image":
            background_photo = image["src"]
            break
    
    gallery_config = {
        "thumbnail_height": 160,
        "title": folder_date,
        "description": "",
        "background_photo": background_photo,
        "url": "",
        "background_photo_offset": 30
    }
    return render_template(
        "gallery_template.jinja",
        images=images_data_list,
        gallery_config=gallery_config,
        background_photo=background_photo
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
