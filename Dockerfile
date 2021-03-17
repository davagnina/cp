FROM tensorflow/tensorflow:2.4.1

# add mariadb repository
RUN apt install -y software-properties-common
RUN apt-key adv --fetch-keys 'https://mariadb.org/mariadb_release_signing_key.asc'
RUN add-apt-repository -y 'deb [arch=amd64,arm64,ppc64el] http://mariadb.mirrors.ovh.net/MariaDB/repo/10.5/ubuntu bionic main'

RUN apt-get update

# install packages needed
RUN apt-get install -y --quiet libmariadb3 libmariadb-dev
RUN apt-get install -y --quiet python3-pip python3-dev
RUN apt-get install -y --quiet git cifs-utils

RUN cp /usr/include/x86_64-linux-gnu/sys/io.h /usr/include

# create directories for the code
RUN mkdir /app
RUN cd /app

# map network path to local folder?


# clone GitHub
RUN git clone https://github.com/davagnina/cp.git
WORKDIR /app

# upgrade and install python modules
RUN pip3 install --upgrade pip
RUN pip3 install -r deps.txt
