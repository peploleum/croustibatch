FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install -y openssh-server  && \
    mkdir /var/run/sshd  && \
    echo 'root:root' |chpasswd
    #sed -ri 's/^PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config
    #sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config && \

COPY sshd_config /etc/ssh/sshd_config
COPY requirements.txt ./

COPY dockerdist .
RUN apt-get update && apt-get install -y git
RUN apt-get update && apt-get install -y vim
RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update && apt-get install -y python3.6
RUN apt-get update && apt-get install -y python3-pip

RUN /usr/bin/pip3 install --no-cache-dir -r requirements.txt

RUN  apt-get -y autoclean && apt-get -y autoremove && \
     apt-get -y purge $(dpkg --get-selections | grep deinstall | sed s/deinstall//g) && \
     rm -rf /var/lib/apt/lists/*

EXPOSE 22

CMD    ["/usr/sbin/sshd", "-D"]