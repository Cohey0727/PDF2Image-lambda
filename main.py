import shutil
import boto3
import os
import sys
from pathlib import Path
from pdf2image import convert_from_path


args = {
    'source-bucket': os.environ.get('SOURCE_BUCKET'),
    'source-file': sys.argv.pop(1),
    'destination-bucket': os.environ.get('DESTINATION_BUCKET', os.environ.get('SOURCE_BUCKET')),
    'destination-path': sys.argv.pop(1),
}

for k, v in ((k.lstrip('-'), v) for k, v in (a.split('=') for a in sys.argv[1:])):
    args[k] = v


def pdf_to_image(input_path: str, output_path: str):
    input_path = Path(input_path)
    output_path = Path(output_path)
    convert_from_path(
        input_path, output_folder=output_path, fmt='png',
        output_file=input_path.stem
    )


def download_pdf(bucket_name: str, file_name: str, output_path: str):
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, file_name, output_path)


def upload_images():
    s3 = boto3.client('s3')
    # Set the name of the bucket that you want to upload the file to
    bucket_name = 'my-bucket'

    # Set the name that you want to give to the uploaded file
    file_name = 'image.png'

    # Open the file in binary mode
    with open(file_name, 'rb') as file:
        # Upload the file to S3
        s3.upload_fileobj(file, bucket_name, file_name)


if __name__ == '__main__':
    print(args)
    temp_dir = "temp"
    pdf_dir = f"{temp_dir}/pdf"
    pdf_path = f"{pdf_dir}/download.pdf"
    output_dir = f"{temp_dir}/images"
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(pdf_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    download_pdf(args['source-bucket'], args['source-file'], pdf_path)
    pdf_to_image(pdf_path, output_dir)
    shutil.rmtree(temp_dir)
