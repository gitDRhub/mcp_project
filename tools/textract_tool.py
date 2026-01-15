import boto3
import time
import os
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
BUCKET = os.getenv("S3_BUCKET_NAME")

textract = boto3.client("textract", region_name=AWS_REGION)

def extract_text_from_pdf(file_name: str) -> str:
    """
    Run AWS Textract Document Text Detection on an S3 PDF and return all extracted lines.

    If "file_name" contains a slash, it is treated as a full S3 key.
    Otherwise it is assumed to be under the "voice/" prefix.
    """

    if not AWS_REGION or not BUCKET:
        return "Error: Missing AWS_REGION or S3_BUCKET_NAME in environment."

    # Allow passing full key (with '/'), else use the default voice/ prefix
    s3_key = file_name if "/" in file_name else f"voice/{file_name}"

    try:
        start = textract.start_document_text_detection(
            DocumentLocation={
                "S3Object": {
                    "Bucket": BUCKET,
                    "Name": s3_key,
                }
            }
        )

        job_id = start["JobId"]

        # Poll for completion
        status = "IN_PROGRESS"
        result = None
        attempts = 0
        while status not in ("SUCCEEDED", "FAILED"):
            result = textract.get_document_text_detection(JobId=job_id)
            status = result.get("JobStatus", "IN_PROGRESS")
            if status in ("SUCCEEDED", "FAILED"):
                break
            attempts += 1
            time.sleep(2)

        if status == "FAILED":
            return "Textract failed"

        # Collect text across all pages using pagination
        lines: list[str] = []
        next_token = None
        while True:
            page = (
                textract.get_document_text_detection(JobId=job_id, NextToken=next_token)
                if next_token
                else result
            )

            for block in page.get("Blocks", []):
                if block.get("BlockType") == "LINE":
                    text = block.get("Text")
                    if text:
                        lines.append(text)

            next_token = page.get("NextToken")
            if not next_token:
                break

        return "\n".join(lines)

    except Exception as e:
        return f"Error during Textract OCR: {e}"
