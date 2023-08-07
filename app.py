import os
import logging
import openai
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="static")
CORS(app, resources={
     r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})

# Static Files


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/favicon.ico")
def favicon():
    return app.send_static_file('favicon.ico')


@app.route("/assets/<path:path>")
def assets(path):
    return send_from_directory("static/assets", path)


# AOAI Integration Settings
AZURE_OPENAI_RESOURCE = os.environ.get("AZURE_OPENAI_RESOURCE")
AZURE_OPENAI_KEY = os.environ.get("AZURE_OPENAI_KEY")
AZURE_OPENAI_PREVIEW_API_VERSION = os.environ.get(
    "AZURE_OPENAI_PREVIEW_API_VERSION", "2023-06-01-preview")


def image_create(request):
    openai.api_type = "azure"
    openai.api_base = f"https://{AZURE_OPENAI_RESOURCE}.openai.azure.com/"
    openai.api_version = AZURE_OPENAI_PREVIEW_API_VERSION
    openai.api_key = AZURE_OPENAI_KEY
    request_messages = request.json["messages"]

    response = openai.Image.create(
        prompt=request_messages,
        size='512x512',
        n=1
    )

    response_obj = {
        "created": response.created,
        "data": response.data
    }

    return jsonify(response_obj), 200


@app.route("/generate_img", methods=["GET", "POST"])
def generate_img():
    try:
        return image_create(request)
    except Exception as e:
        logging.exception("Exception in /generate_img")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
