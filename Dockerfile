FROM ubuntu:trusty
MAINTAINER ODL DevOps <mitx-devops@mit.edu>

# Add package files
WORKDIR /tmp

# Install base packages
COPY apt.txt /tmp/apt.txt
RUN apt-get update &&\
    apt-get install -y $(grep -vE "^\s*#" apt.txt  | tr "\n" " ") &&\
    ln -s /usr/bin/nodejs /usr/bin/node &&\
    pip install pip --upgrade &&\
    npm install -g dredd

# Add non-root user.
RUN adduser --disabled-password --gecos "" mitodl

# Install project packages

# Python 2
COPY requirements.txt /tmp/requirements.txt
COPY test_requirements.txt /tmp/test_requirements.txt
COPY dredd_requirements.txt /tmp/dredd_requirements.txt

RUN pip install -r requirements.txt &&\
    pip install -r test_requirements.txt &&\
    pip install -r dredd_requirements.txt

# Python 3
RUN pip3 install -r requirements.txt &&\
    pip3 install -r test_requirements.txt

# Add project
COPY . /src
WORKDIR /src
RUN chown -R mitodl:mitodl /src

RUN apt-get clean && apt-get purge
USER mitodl

# Set pip cache folder, as it is breaking pip when it is on a shared volume
ENV XDG_CACHE_HOME /tmp/.cache

# Set and expose port for uwsgi config
EXPOSE 8077
ENV PORT 8077
CMD uwsgi uwsgi.ini
