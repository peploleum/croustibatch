FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install -y openssh-server  && \
    mkdir /var/run/sshd  && \
    echo 'root:root' |chpasswd
    #sed -ri 's/^PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config
    #sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config && \

COPY sshd_config /etc/ssh/sshd_config
COPY requirements.txt ./

RUN apt-get update && apt-get install -y git
RUN apt-get update && apt-get install -y vim
RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update && apt-get install -y python3.6
RUN apt-get update && apt-get install -y curl
RUN apt-get update && apt-get install -y unzip
RUN apt-get update && apt-get install -y openalpr openalpr-utils libopenalpr-dev
RUN apt-get update && apt-get install -y tesseract-ocr
RUN apt-get update && apt-get install -y python-imaging
RUN apt-get update && apt-get install -y libjpeg62 libjpeg62-dev

RUN mkdir /app
RUN mkdir /app/source
RUN mkdir /app/download
COPY dockerdist/source /app/source
COPY entrypoint.sh /app
COPY dockerdist/*.py /app/
RUN mkdir /app/runtime_data
COPY dockerdist/runtime_data /app/runtime_data
RUN mkdir /app/samples
COPY dockerdist/samples /app/samples
RUN mkdir /app/conf
COPY dockerdist/conf /app/conf
COPY openalpr-2.3.0.zip app/

RUN ln -s /usr/lib/x86_64-linux-gnu/libz.so /usr/lib/libz.so
RUN ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib/libjpeg.so
RUN ln -s /usr/lib/x86_64-linux-gnu/libfreetype.so /usr/lib/libfreetype.so

RUN curl https://bootstrap.pypa.io/get-pip.py | python3.6
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt


RUN  apt-get -y autoclean && apt-get -y autoremove && \
     apt-get -y purge $(dpkg --get-selections | grep deinstall | sed s/deinstall//g) && \
     rm -rf /var/lib/apt/lists/*

RUN cd app && unzip openalpr-2.3.0.zip && rm openalpr-2.3.0.zip && cd openalpr-2.3.0
RUN cd /app/openalpr-2.3.0/src/bindings/python && python3.6 setup.py install --record files.txt
EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]