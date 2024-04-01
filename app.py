from flask import Flask, request, jsonify
import json
import os
import google.generativeai as genai
from flask_cors import CORS
from google.generativeai.types import HarmCategory, HarmBlockThreshold

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
    'temperature': 0,
    'top_k': 20,
    'top_p': 0.9,
    'max_output_tokens': 500
}

model = genai.GenerativeModel(model_name="gemini-pro-vision")


# Defining Routes: We define two routes - one for the home page and another for handling chat messages.
@app.route('/', methods=['GET'])
def hello_world():
    return "Hii"


@app.route('/chat', methods=['POST'])
def chat():
    if 'image' not in request.files:
        return jsonify({"error": "Missing image file"})

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"})

    if file.content_type not in ['image/jpeg', 'image/png']:
        return jsonify({"error": "Unsupported image format. Only JPEG and PNG allowed"})

    if file:
        image_data = file.read()

        # (Optional) Use Google Cloud Vision to analyze image content

        prompt =  "Your role as an engineer requires a thorough analysis and elucidation of the technical aspects depicted in the provided image. Focus your explanation on components, architecture, algorithms, protocols, and other relevant technical elements pertinent to software engineering, project management, and information technology. Ensure that your analysis is detailed and accessible to technical audiences. However, if the image depicts subjects such as animals,scenery, objects not related to information technology field, trees, or human beings, or if it lacks relevance to software engineering, project management, or information technology, your response should simply state 'Non-technical'. Remember to format your response in Markdown and ensure it exceeds 100 words to provide a comprehensive analysis."

        image_parts = [
            {
                "mime_type": file.content_type,
                "data": image_data
            },
        ]

        prompt_parts = [prompt, image_parts[0]]

        try:
            response = model.generate_content(prompt_parts, safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    })
            # Access text from parts
            generated_text = response.parts[0].text.encode("utf-8")
            return generated_text
        except Exception as e:
            if response.candidates[0].safety_ratings:
                print("Safety Rating:")
                for rating in response.candidates[0].safety_ratings:
                    print(f"{rating.category}: {rating.probability}")
            else:
                print(f"Error generating content: {e}")
            return jsonify({"error": "internal server error"})

# Finally, we'll add the entrypoint for the file which runs the Flask development server.

# if __name__ == '__main__':
#     app.run(debug=True, host="0.0.0.0")
