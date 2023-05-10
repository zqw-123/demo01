FROM python:3.7

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN /usr/local/bin/python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple/

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

RUN apt-get update 

RUN apt-get install ffmpeg libsm6 libxext6  -y

COPY . /code/


