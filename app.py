import boto3
import os
import PyPDF2
import shutil
import urllib.parse
from typing import Callable
from pathlib import Path
from pdf2image import convert_from_path


s3_client = boto3.client("s3")


def split_pdf(input_path: str, output_dir: str, on_created: Callable[[str], None]) -> list[str]:
    res = []
    with open(input_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for index in range(len(reader.pages)):
            output = PyPDF2.PdfWriter()
            output.add_page(reader.pages[index])
            number = f"{index}".zfill(4)
            file_path = f"{output_dir}/page-{number}.pdf"
            res.append(file_path)
            with open(file_path, "wb") as out:
                output.write(out)
            on_created(file_path)

    return res


def pdf_to_images(input_path: str, output_dir: str) -> list[str]:
    res = []
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    pages = convert_from_path(input_path)
    for index, page in enumerate(pages):
        number = f"{index}".zfill(4)
        file_name = f"{output_dir}/page-{number}.png"
        res.append(file_name)
        page.save(file_name, "PNG")

    return res


def pdf_first_page_to_image(input_path: str, output_path: str):
    input_path = Path(input_path)
    output_path = Path(output_path)
    pages = convert_from_path(input_path)
    page = pages[0]
    page.save(output_path, "PNG")


def download_pdf(bucket_name: str, file_name: str, output_path: str):
    s3 = boto3.client("s3")
    s3.download_file(bucket_name, file_name, output_path)


def upload_folder(bucket_name: str, folder_name: str, output_dir: str):
    # Open the file in binary mode
    for root, dirs, files in os.walk(folder_name):
        for file in files:
            file_path = os.path.join(root, file)
            s3_key = f"{output_dir}{file_path.replace(folder_name, '')}"
            upload_file(bucket_name, file_path, s3_key)


def upload_file(bucket_name: str, file_path: str, s3_key: str):
    s3_client.upload_file(file_path, bucket_name, s3_key)


def is_s3_event(event) -> bool:
    return event.get("Records") and event["Records"][0].get("s3")


def parse_s3_event(event) -> dict:
    record = event["Records"][0]["s3"]
    bucket_name = record["bucket"]["name"]
    source_file = urllib.parse.unquote(record["object"]["key"])
    return {
        "source_bucket": bucket_name,
        "source_file": source_file,
        "destination_bucket": os.getenv("DESTINATION_BUCKET", bucket_name),
        "destination_path": os.path.dirname(source_file),
    }


def handler(event: dict, context):
    print("Start!!!")
    print(event)
    if is_s3_event(event):
        event = parse_s3_event(event)

    # Prepare Source and Destination
    source_bucket = event.get("source_bucket", os.getenv("SOURCE_BUCKET"))
    destination_bucket = event.get(
        "destination_bucket", os.getenv("DESTINATION_BUCKET"))
    source_file = event["source_file"]
    destination_path = event["destination_path"]
    print("S3 Bucket And Path Information")
    print(
        {
            "source_bucket": source_bucket,
            "destination_bucket": destination_bucket,
            "source_file": source_file,
            "destination_path": destination_path,
        }
    )

    # Prepare Local Directories
    temp_dir = "/tmp/upload"
    origin_path = "/tmp/origin.pdf"
    pdfs_dir = f"{temp_dir}/pdfs"
    images_dir = f"{temp_dir}/images"
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(pdfs_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    print("Finish make directories!!!")

    # Download PDF File
    download_pdf(source_bucket, source_file, origin_path)
    print("Finish Download PDF!!!")

    def on_created(pdf_path):
        pdf_name = os.path.basename(pdf_path)
        image_name = pdf_name.replace(".pdf", ".png")
        image_path = f"{images_dir}/{image_name}"
        pdf_first_page_to_image(pdf_path, image_path)
        upload_file(destination_bucket, pdf_path,
                    f"{destination_path}/pdfs/{pdf_name}")
        print(f"Upload {destination_path}/pdfs/{pdf_name}")
        upload_file(destination_bucket, image_path,
                    f"{destination_path}/images/{image_name}")
        print(f"Upload {destination_path}/images/{image_name}")

        os.remove(pdf_path)
        print(f"Remove {pdf_path}")
        os.remove(image_path)
        print(f"Remove {image_path}")

    split_pdf(origin_path, pdfs_dir, on_created)

    shutil.rmtree(temp_dir)
    print("Finish Cleaning!!!")

    return {"statusCode": 200, "body": "Success"}
