from flask import Flask, request, jsonify
import json
import os
import google.generativeai as genai
from flask_cors import CORS

# Initializing the App and Gemini API: We initialize our Flask app and load the Gemini API client.
working_dir = os.path.dirname(os.path.abspath(__file__))

# path of config_data file
config_file_path = f"{working_dir}/config.json"
config_data = json.load(open("config.json"))

# loading the GOOGLE_API_KEY
GOOGLE_API_KEY = config_data["GOOGLE_API_KEY"]

# configuring google.generativeai with API key
genai.configure(api_key=GOOGLE_API_KEY)

app = Flask(__name__)
app.debug = True

CORS(app)
config = {
    'temperature': 0.4,
    'top_k': 32,
    'top_p': 1,
    'max_output_tokens': 2048
}

model = genai.GenerativeModel(model_name="gemini-pro-vision", generation_config=config)


# Custom Error Handler
@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"message": "Internal Server Error"}), 500


# Defining Routes: We define two routes - one for the home page and another for handling chat messages.
@app.route('/', methods=['GET'])
def hello_world():
    return "Hii"


@app.route('/chat', methods=['POST'])
def chat():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No file part"})

        file = request.files['image']
        prompt = config_data.get("prompt")

        if file.filename == '':
            return jsonify({"error": "No selected file"})

        if file:
            image_data = file.read()
            image_parts = [
                {
                    "mime_type": file.content_type,
                    "data": image_data
                },
            ]

            prompt_parts = [prompt, image_parts[0]]

            response = model.generate_content(prompt_parts)

            return response.text.encode("utf-8")
    except Exception as e:
        app.logger.error("Exception occurred: %s", str(e))
        return jsonify({"message": "Internal Server Error"}), 500


# Finally, we'll add the entrypoint for the file which runs the Flask development server.
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
