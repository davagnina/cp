FROM debian:buster
RUN echo ####
RUN apt-get update
RUN apt-get install python3-pip python3-venv git
