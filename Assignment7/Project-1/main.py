import os
import tempfile    # To create temporary file before uploading to bucket
from google.cloud import storage
from flask import escape
from flask import jsonify
# Add any imports that you may need, but make sure to update requirements.txt


def create_text_file_http(request):
    bucket_name = os.environ["BUCKET_ENV_VAR"]
    storage_client = storage.Client()
    request_json = request.get_json(silent=True)
	
    if request_json and 'fileName' in request_json:
        fileName = request_json['fileName']
    
    if request_json and 'fileContent' in request_json:
        fileContent = request_json['fileContent']

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(fileName)

    blob.upload_from_string(fileContent)
    data = {"fileName" : fileName}
    return jsonify(data), 200