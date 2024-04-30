import json
import requests
import shutil
from exif import Image as ExifImage
from PIL import Image as PillowImage
from PIL import ExifTags
from datetime import datetime

def get_img(url, filename):
    res = requests.get(url, stream = True)
    if res.status_code == 200:
        with open(filename, 'wb') as f:
            shutil.copyfileobj(res.raw, f)
    else:
        print('Error getting image')

def get_filename(url):
    return url.rsplit('/', 1)[-1].rsplit('?', 1)[0]

def download_photos():
    all_urls = []
    for i in range(9):
        with open('bh_gallery_{}.json'.format(i+1), "r") as images_data_in:
            bh_data = json.load(images_data_in)
        urls = [item['url_big'] for item in bh_data]
        all_urls.extend(urls)
    unique_urls = list(set(all_urls))

    for url in unique_urls:
        filename = get_filename(url)
        get_img(url,  'bh_photos/' + filename)

def timestamp_to_exif_dt(ts):
    dt = datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S%z')
    dt_str = dt.strftime('%Y:%m:%d %H:%M:%S')
    return dt_str

def timestamp_to_filename(ts):
    dt = datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S%z')
    dt_str = dt.strftime('%Y%m%d_%H%M%S')
    return dt_str

def write_image_exif(in_image_path, out_image_path, created_at):
    pillow_image = PillowImage.open(in_image_path)
    img_exif = pillow_image.getexif()
    img_exif[36867] = created_at
    img_exif[306] = created_at
    pillow_image.save(out_image_path, exif=img_exif)


if __name__ == "__main__":
    all_imgs = []
    image_creation_date_map = {}
    for i in range(9):
        with open('bh_gallery_{}.json'.format(i+1), "r") as images_data_in:
            bh_data = json.load(images_data_in)
        for item in bh_data:
            image_creation_date_map.update({
                item['imageId']: item['createdAt']
            })
            all_imgs.append(item['imageId'])
    unique_imgs = list(set(all_imgs))
    for i in range(len(unique_imgs)):
        img = unique_imgs[i]
        ts = image_creation_date_map[img]
        filename = "nursery_{}".format(timestamp_to_filename(ts))
        exif_ts = timestamp_to_exif_dt(ts)
        source_img_path = "bh_photos/{}.jpg".format(img)
        out_img_path = "bh_photos_processed/{}_{}.jpg".format(filename, str(i))
        write_image_exif(source_img_path, out_img_path, exif_ts)