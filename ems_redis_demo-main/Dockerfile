FROM redis:latest

#换镜像源
RUN apt-get update
ADD ./attach_files/sources.list /etc/apt/sources.list 
RUN apt-get install gnupg -y
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 3B4FE6ACC0B21F32
RUN apt-get update
RUN apt-get upgrade -y

#安装python3.7
RUN apt-get install wget -y
RUN apt-get install gcc -y
RUN apt-get install make
RUN apt-get install --reinstall zlib1g=1:1.2.11.dfsg-2+deb11u2
RUN apt-get install --reinstall zlibc zlib1g-dev
RUN apt-get install libffi-dev libssl-dev 
RUN wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tgz
RUN mv Python-3.7.0.tgz /usr/local 
RUN cd /usr/local/ && \
    tar -zxvf /usr/local/Python-3.7.0.tgz && \
    rm /usr/local/Python-3.7.0.tgz && \
    cd Python-3.7.0 && \
        ./configure && \
            make && \
            make install
RUN ln -s /usr/local/bin/python3.7.0 /usr/bin/python


#代码部署
COPY Func /code/Func 
ADD ./attach_files/requirements.txt /code/requirements.txt

RUN pip3 install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple/
RUN pip3 install --no-cache-dir --upgrade -r /code/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

