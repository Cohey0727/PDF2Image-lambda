from pathlib import Path
from pdf2image import convert_from_path


def pdf_to_image(input_path: Path, output_path: Path):
    convert_from_path(
        input_path, output_folder=output_path, fmt='png',
        output_file=input_path.stem
    )


pdf_path = Path("assets/sample.pdf")
output_path = Path("outputs")

if __name__ == '__main__':
    pdf_to_image(pdf_path, output_path)
