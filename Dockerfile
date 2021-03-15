FROM debian:buster

RUN apt-get update
RUN apt-get install python3-pip python3-venv git

RUN mkdir /cryptoproject
RUN mkdir /cryptoproject/code

RUN git -C /cryptoproject/code https://github.com/davagnina/cryptoproject.git

RUN python3 -m venv /cryptoproject

RUN source /cryptoproject/bin/activate

RUN pip3 install -r code/dependencies.txt

EOF
