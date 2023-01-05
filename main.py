import boto3
import os
import PyPDF2
import shutil
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


def split_pdf(input_path: str, output_path: str) -> list[str]:
    res = []
    with open(input_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for index in range(len(reader.pages)):
            output = PyPDF2.PdfWriter()
            output.add_page(reader.pages[index])
            file_name = f'{output_path}/page-{index}.pdf'
            res.append(file_name)
            with open(file_name, 'wb') as out:
                output.write(out)

    return res


def pdf_to_image(input_path: str, output_dir: str) -> list[str]:
    res = []
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    pages = convert_from_path(input_path)
    for index, page in enumerate(pages):
        file_name = f'{output_dir}/page-{index}.png'
        res.append(file_name)
        page.save(file_name, 'PNG')

    return res


def download_pdf(bucket_name: str, file_name: str, output_path: str):
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, file_name, output_path)


def upload_folder(bucket_name: str, folder_name: str, output_dir: str):
    s3 = boto3.client('s3')
    # Open the file in binary mode
    for root, dirs, files in os.walk(folder_name):
        for file in files:
            file_path = os.path.join(root, file)
            s3_key = f"{output_dir}{file_path.replace(folder_name, '')}"
            s3.upload_file(file_path, bucket_name, s3_key)


if __name__ == '__main__':
    print(args)
    bucket_name = args['destination-bucket']
    source_file = args['source-file']
    destination_path = args['destination-path']
    temp_dir = "upload"
    origin_path = "origin.pdf"
    pdf_dir = f"{temp_dir}/pdfs"
    output_dir = f"{temp_dir}/images"
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(pdf_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    download_pdf(bucket_name, source_file, origin_path)
    pdfs = split_pdf(origin_path, pdf_dir)
    images = pdf_to_image(origin_path, output_dir)
    upload_folder(bucket_name, temp_dir, destination_path)
    os.remove(origin_path)
    shutil.rmtree(temp_dir)
