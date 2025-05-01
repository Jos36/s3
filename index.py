from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import uuid

app = Flask(__name__)
CORS(app)

s3_client = boto3.client('s3')
BUCKET_NAME = 'bucketproject2025'

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = f"{uuid.uuid4()}_{file.filename}"

    try:
        s3_client.upload_fileobj(file, BUCKET_NAME, filename)
        file_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': filename},
            ExpiresIn=3600
        )
        return jsonify({"message": "File uploaded successfully", "file_url": file_url}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/files', methods=['GET'])
def list_files():
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        files = [{'id': obj['Key'], 'name': obj['Key'], 'size': obj['Size']} for obj in response.get('Contents', [])]
        return jsonify(files), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/files/<filename>', methods=['GET'])
def get_file(filename):
    try:
        file_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': filename},
            ExpiresIn=3600
        )
        return jsonify({"file_url": file_url}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=filename)
        return jsonify({"message": "File deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
