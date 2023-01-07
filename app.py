import boto3
import os
import PyPDF2
import shutil
from typing import Callable
from pathlib import Path
from pdf2image import convert_from_path

s3_client = boto3.client('s3')


def split_pdf(input_path: str, output_dir: str, on_created: Callable[[str], None]) -> list[str]:
    res = []
    with open(input_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for index in range(len(reader.pages)):
            output = PyPDF2.PdfWriter()
            output.add_page(reader.pages[index])
            number = f"{index}".zfill(4)
            file_path = f'{output_dir}/page-{number}.pdf'
            res.append(file_path)
            with open(file_path, 'wb') as out:
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
        file_name = f'{output_dir}/page-{number}.png'
        res.append(file_name)
        page.save(file_name, 'PNG')

    return res


def pdf_first_page_to_image(input_path: str, output_path: str):
    input_path = Path(input_path)
    output_path = Path(output_path)
    pages = convert_from_path(input_path)
    page = pages[0]
    page.save(output_path, 'PNG')


def download_pdf(bucket_name: str, file_name: str, output_path: str):
    s3 = boto3.client('s3')
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


def handler(event, context):
    print('Start!!!')
    print(event)

    source_bucket = event['source_bucket']
    destination_bucket = event.get('destination_bucket', source_bucket)
    source_file = event['source_file']
    destination_path = event['destination_path']
    temp_dir = "/tmp/upload"
    origin_path = "/tmp/origin.pdf"
    pdfs_dir = f"{temp_dir}/pdfs"
    images_dir = f"{temp_dir}/images"
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(pdfs_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    print('Finish make directories!!!')
    download_pdf(source_bucket, source_file, origin_path)
    print('Finish Download PDF!!!')

    def on_created(pdf_path):
        pdf_name = os.path.basename(pdf_path)
        image_name = pdf_name.replace('.pdf', '.png')
        image_path = f"{images_dir}/{image_name}"
        pdf_first_page_to_image(pdf_path, image_path)
        upload_file(
            destination_bucket, pdf_path,
            f"{destination_path}/pdfs/{pdf_name}"
        )
        print(f"Upload {destination_path}/pdfs/{pdf_name}")
        upload_file(
            destination_bucket, image_path,
            f"{destination_path}/images/{image_name}"
        )
        print(f"Upload {destination_path}/images/{image_name}")

        os.remove(pdf_path)
        print(f"Remove {pdf_path}")
        os.remove(image_path)
        print(f"Remove {image_path}")

    split_pdf(origin_path, pdfs_dir, on_created)

    # images = pdf_to_images(origin_path, images_dir)
    # upload_folder(destination_bucket, temp_dir, destination_path)
    print('Finish Upload!!!')
    os.remove(origin_path)
    print('Finish Cleaning!!!')
    shutil.rmtree(temp_dir)
    return {"statusCode": 200, "body": "Success"}
