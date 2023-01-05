import boto3
from pathlib import Path
from pdf2image import convert_from_path


def pdf_to_image(input_path: Path, output_path: Path):
    convert_from_path(
        input_path, output_folder=output_path, fmt='png',
        output_file=input_path.stem
    )


def download_pdf(bucket_name: str, file_name: str):
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, file_name, file_name)


if __name__ == '__main__':
    pdf_path = Path("assets/sample.pdf")
    output_path = Path("outputs")
    pdf_to_image(pdf_path, output_path)
