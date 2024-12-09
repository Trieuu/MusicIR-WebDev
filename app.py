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
    
    # Check for valid file extensions: .mp3 or .m4a
    if file and (file.filename.endswith('.mp3') or file.filename.endswith('.m4a')):
        # Use tempfile to create a temporary file in the correct platform-independent location
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[-1]) as temp_file:
            file_path = temp_file.name
            file.save(file_path)

        # Send the file to the external API
        response = send_audio_to_api(file_path)

        # Delete the file after sending it to the API (optional)
        os.remove(file_path)
        
        # Extract only the song name and link from the API response
        if 'item_sorted' in response:
            songs = [{"name": song["song_info"]["name"], "link": song["song_info"]["link"]} for song in response["item_sorted"]]
            return render_template('upload_result.html', songs=songs)

        return jsonify({"error": "No results found from the API"}), 400
    else:
        return jsonify({"error": "Invalid file type. Only MP3 and M4A files are allowed."}), 400

def send_audio_to_api(file_path):
    # Determine the MIME type based on the file extension
    mime_type = 'audio/mpeg' if file_path.endswith('.mp3') else 'audio/mp4'

    with open(file_path, 'rb') as audio_file:
        files = {'file': (audio_file.name, audio_file, mime_type)}
        
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





