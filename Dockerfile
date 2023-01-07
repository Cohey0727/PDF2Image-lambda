FROM public.ecr.aws/lambda/python:3.9

RUN yum install poppler-utils -y
RUN pip3 install pdf2image boto3 PyPDF2 --target "${LAMBDA_TASK_ROOT}"

COPY . ${LAMBDA_TASK_ROOT}

CMD [ "app.handler" ]
