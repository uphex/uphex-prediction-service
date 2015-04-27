from ubuntu:trusty

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y build-essential g++ libblas-dev liblapack-dev gfortran python-dev python-pip

RUN pip install --upgrade numpy
RUN pip install --upgrade statsmodels
RUN pip install --upgrade flask

COPY . server

WORKDIR server

EXPOSE 5000
