import os
import tempfile
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# API URL
API_URL = "https://musicir-1089901605984.asia-southeast1.run.app/upload"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if a file is in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and file.filename.endswith('.mp3'):
        # Use tempfile to create a temporary file in the correct platform-independent location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            file_path = temp_file.name
            file.save(file_path)

        # Send the file to the external API
        response = send_mp3_to_api(file_path)

        # Delete the file after sending it to the API (optional)
        os.remove(file_path)
        
        # Extract only the song name and link from the API response
        if 'item_sorted' in response:
            songs = [{"name": song["song_info"]["name"], "link": song["song_info"]["link"]} for song in response["item_sorted"]]
            return render_template('upload_result.html', songs=songs)

        return jsonify({"error": "No results found from the API"}), 400
    else:
        return jsonify({"error": "Invalid file type. Only MP3 files are allowed."}), 400

def send_mp3_to_api(file_path):
    with open(file_path, 'rb') as mp3_file:
        files = {'file': (mp3_file.name, mp3_file, 'audio/mpeg')}
        
        try:
            response = requests.post(API_URL, files=files, timeout=300)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed with status code {response.status_code}: {response.text}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"An error occurred: {str(e)}"}

# Entry point for Vercel's serverless function
# def handler(request):
#     with app.test_request_context(request.path, method=request.method, data=request.data):
#         return app.full_dispatch_request()

# This is for local run
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))





