import json
import os
import subprocess

import yaml
from schema import schema_config


def get_gallery_json(path: str, title: str, desc: str):
    return {
        "images_data_file": f"{path}/images_data.json",
        "public_path": f"{path}/public",
        "templates_path": f"{path}/templates",
        "images_path": f"{path}/public/images/photos",
        "thumbnails_path": f"{path}/public/images/thumbnails",
        "thumbnail_height": 160,
        "title": title,
        "description": desc,
        "background_photo": "",
        "url": "",
        "background_photo_offset": 30,
        "disable_captions": False
    }


def get_app_yaml(all_yaml_paths):
    return {
        "runtime": "python39",
        "instance_class": "F1",
        "automatic_scaling": {
            "min_instances": 1,
            "max_instances": 15,
            "min_idle_instances": 1,
        },
        "handlers": all_yaml_paths
    }


with open('src/config.json') as config_file:
    config = json.load(config_file)

config_data = schema_config(**config)

all_yaml_paths = []

for folder in config_data.folders:
    folder_path = os.path.join(config_data.root, folder.path, ".")
    target_path = os.path.join(config_data.target, folder.path)
    photos_path = os.path.join(target_path, "public", "images", "photos")

    subprocess.run(["rm", "-rf", target_path])
    subprocess.run(["mkdir", target_path])
    subprocess.run(["cp", "-r", config_data.template, target_path])
    subprocess.run(["cp", "-r", folder_path, photos_path])

    gallery_json = get_gallery_json(
        target_path,
        folder.title,
        folder.description
    )
    with open(os.path.join(target_path, 'gallery.json'), 'w') as f:
        json.dump(gallery_json, f)

    subprocess.run(["gallery-build", "-p", target_path])

    paths = [
        {
            "url": f"/{folder.path}/$",
            "static_files": f"photos/{folder.path}/public/index.html",
            "upload": f"photos/{folder.path}/public/index.html",
        },
        {
            "url": f"/{folder.path}/(.*)/$",
            "static_files": f"photos/{folder.path}/public/\\1/index.html",
            "upload": f"photos/{folder.path}/public/.*/index.html",
        },
        {
            "url": f"/{folder.path}/(.+)",
            "static_files": f"photos/{folder.path}/public/\\1",
            "upload": f"photos/{folder.path}/public/(.*)",
        }
    ]
    all_yaml_paths.extend(paths)

with open('app.yaml', 'w') as outfile:
    yaml.dump(get_app_yaml(all_yaml_paths), outfile, default_flow_style=False)
