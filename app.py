from flask import Flask, request, render_template, send_file
import boto3
import os
from dotenv import load_dotenv
import io

load_dotenv()

app = Flask(__name__)

# Cloudflare R2 configuration
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_BUCKET = os.getenv("R2_BUCKET")
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY")
R2_ENDPOINT = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

# Boto3 client with SigV4
s3 = boto3.client(
    "s3",
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY,
    config=boto3.session.Config(signature_version="s3v4")
)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        if file:
            s3.upload_fileobj(file, R2_BUCKET, file.filename)
            return "", 204  # Reload handled by JS in modern UI

    files = s3.list_objects_v2(Bucket=R2_BUCKET).get("Contents", [])
    file_names = [f["Key"] for f in files]
    return render_template("index.html", files=file_names)

@app.route("/file/<filename>")
def get_file(filename):
    """Serve file inline for preview/download"""
    obj = s3.get_object(Bucket=R2_BUCKET, Key=filename)
    file_stream = io.BytesIO(obj['Body'].read())
    return send_file(
        file_stream,
        download_name=filename,
        as_attachment=False  # inline preview
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
