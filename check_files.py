import boto3
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

s3 = boto3.client(
    "s3",
    endpoint_url=f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
    aws_access_key_id=os.getenv("R2_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("R2_SECRET_KEY"),
)

bucket_name = os.getenv("R2_BUCKET")

files = s3.list_objects_v2(Bucket=bucket_name).get("Contents", [])
for f in files:
    print(f["Key"])
