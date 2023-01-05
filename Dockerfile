FROM python:3.11

WORKDIR /opt/app

COPY . .

RUN apt-get update
RUN apt-get install -y poppler-utils 
RUN pip install pdf2image boto3 PyPDF2
RUN mkdir outputs

CMD echo 'Hello docker world!'
