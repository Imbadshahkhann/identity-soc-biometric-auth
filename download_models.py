import os
import urllib.request

print("Downloading required OpenCV models...")

MODELS_DIR = "models"
os.makedirs(MODELS_DIR, exist_ok=True)

files_to_download = {
    "deploy.prototxt": "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt",
    "res10_300x300_ssd_iter_140000.caffemodel": "https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel",
    "openface_nn4.small2.v1.t7": "https://raw.githubusercontent.com/pyannote/pyannote-data/master/openface.nn4.small2.v1.t7"
}

for filename, url in files_to_download.items():
    filepath = os.path.join(MODELS_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Downloading {filename}...")
        try:
            urllib.request.urlretrieve(url, filepath)
            print(f"Downloaded {filename} successfully.")
        except Exception as e:
            print(f"Error downloading {filename}: {e}")
    else:
        print(f"{filename} already exists.")

print("All models downloaded.")
