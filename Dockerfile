FROM sanmaomashi/python:3.9.16-ubuntu20.04

# gpu
#FROM sanmaomashi/python:3.9.16-ubuntu20.04-cuda11.7-cudnn8

COPY . /app

RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "1701"]