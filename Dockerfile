FROM python:3.11

WORKDIR /opt/app

RUN apt-get update
RUN apt-get install -y poppler-utils 
RUN pip install pdf2image PyPDF2

COPY . .

CMD echo 'Hello docker world!'
