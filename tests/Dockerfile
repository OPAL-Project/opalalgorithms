# Select source image
FROM ubuntu:xenial

# Install all dependencies
ENV TERM linux

RUN apt-get update -q

RUN apt-get install -y dialog apt-utils
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN apt-get upgrade -y --no-install-recommends

RUN apt-get install -y python-pip python-dev gcc
RUN apt-get install -y apparmor apparmor-profiles apparmor-utils
RUN apt-get update && apt-get install -y sudo && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y git

# required libraries
RUN apt-get install -y libpthread-stubs0-dev

RUN apt-get install -y curl

RUN pip install --upgrade pip

RUN apt-get install -y build-essential

RUN rm -rf /etc/apparmor.d/docker-engine

COPY . /usr/opalalgorithms
WORKDIR /usr/opalalgorithms

# Install python library required
RUN pip install git+https://github.com/OPAL-Project/codejail.git \
    && pip install git+https://github.com/emalgorithm/bandicoot.git \
    && pip install -r requirements.txt \
    && python setup.py install

# Creating virtualenv for sandbox
RUN mkdir /usr/venv
RUN pip install virtualenv \
    && virtualenv /usr/venv/sandbox \
    && chmod +x /usr/venv/sandbox/bin/activate

RUN ls -alh /usr/venv/sandbox/bin/

# install libraries in virtualenv
RUN /bin/bash -c "source /usr/venv/sandbox/bin/activate \
    && pip install git+https://github.com/emalgorithm/bandicoot.git \
    && pip install git+https://github.com/OPAL-Project/codejail.git \
    && pip install -r requirements.txt \
    && python setup.py install \
    && deactivate"

# create a sandbox user
RUN useradd -ms /bin/bash sandbox
COPY ./tests/setup_scripts/usr.venv.sandbox.bin.python /etc/apparmor.d/

RUN useradd -ms /bin/bash opal
USER opal

COPY ./tests/setup_scripts/95-sandbox /etc/sudoers.d/
RUN sudo ldconfig -v | grep -v ^$'\t'

# generate dummy data
WORKDIR /home/opal
COPY . opalalgorithms
WORKDIR /home/opal/opalalgorithms/tests
RUN python generate_data.py --conf datagen.conf

CMD sh -c 'sudo mount -tsecurityfs securityfs /sys/kernel/security && sudo apparmor_parser -r -W /etc/apparmor.d/usr.venv.sandbox.bin.python && flake8 . && pytest .'
