FROM ubuntu:jammy
# => Python 3.10

MAINTAINER Ostfalia

ENV PYTHONUNBUFFERED 1
ARG PASSWORD=123

ARG GROUP_ID=999
# docker group id (name=docker cannot be used here)
# figure it out by call of "/etc/group"
ARG DOCKER_GROUP_ID=2000
ARG PRAKTOMAT_ID=1100
# ARG TESTER_ID=777


# set locale to German (UTF-8)
ARG LOCALE=de_DE.UTF-8

ARG DEBIAN_FRONTEND=noninteractive

# change locale to something UTF-8
RUN apt-get update && apt-get install -y locales && locale-gen ${LOCALE} && rm -rf /var/lib/apt/lists/*
ENV LANG ${LOCALE}
ENV LC_ALL ${LOCALE}


# libffi-dev is used for python unittests with pandas (avoid extra RUN command)
# squashfs-tools is used for sandbox templates
RUN apt-get update && \
    apt-get install -y libxml2-dev libxslt1-dev python3-pip libpq-dev wget cron netcat sudo \
    subversion git unzip \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

#    apt-get install -y swig libxml2-dev libxslt1-dev python3-pip python3-venv libpq-dev wget cron netcat sudo \

# Install Java needed for Checkstyle (currently not running in own sandbox)
RUN apt-get update && apt-get install -y openjdk-21-jdk && rm -rf /var/lib/apt/lists/*
# ADD UNIX USERS
################



# create group praktomat
RUN groupadd -g ${GROUP_ID} praktomat && \
  groupadd -g ${DOCKER_GROUP_ID} docker && \
# add user praktomat to group praktomat \
  useradd -g ${GROUP_ID} -u ${PRAKTOMAT_ID} praktomat -s /bin/sh --home /praktomat --create-home --comment "Praktomat Demon" && \
# add user praktomat to docker group \
  usermod -a -G ${DOCKER_GROUP_ID} praktomat && \
# add user praktomat to sudo (???) \
  usermod -aG sudo praktomat && \
  echo "praktomat:$PASSWORD" | sudo chpasswd
# add user tester (uid=777) \
#  useradd -g ${GROUP_ID} -u ${TESTER_ID} tester -s /bin/false --no-create-home -c "Test Execution User"

# allow user praktomat to start cron
RUN echo "praktomat ALL=NOPASSWD:SETENV: /usr/sbin/cron,/usr/bin/py3clean,/usr/bin/python3,/usr/bin/mount " >> /etc/sudoers && \
echo "praktomat ALL=(tester) NOPASSWD: ALL" >> /etc/sudoers


# RUN mkdir /praktomat && chown ${PRAKTOMAT_ID}:${GROUP_ID} /praktomat
WORKDIR /praktomat
ADD --chown=${PRAKTOMAT_ID}:${GROUP_ID} requirements.txt /praktomat/
RUN pip3 install --upgrade pip && \
    pip3 --version && \
    pip3 install -r requirements.txt --ignore-installed --force-reinstall --upgrade --no-cache-dir


COPY . /praktomat

RUN mkdir -p /praktomat/upload && mkdir -p /praktomat/media


# COPY src/ src/
# COPY extra extra/

# create cron job for deleting temporary files (no dots in new filename)
COPY cron.conf /etc/cron.d/praktomat-cron
#COPY --chown=999:999 cron.conf /etc/cron.d/praktomat-cron
#RUN chmod 0644 /etc/cron.d/praktomat-cron

# add JAVA test specific libraries
# Checkstyle
ADD https://github.com/checkstyle/checkstyle/releases/download/checkstyle-10.17.0/checkstyle-10.17.0-all.jar \
    https://github.com/checkstyle/checkstyle/releases/download/checkstyle-10.1/checkstyle-10.1-all.jar \
    https://github.com/checkstyle/checkstyle/releases/download/checkstyle-8.23/checkstyle-8.23-all.jar \
    https://github.com/checkstyle/checkstyle/releases/download/checkstyle-8.29/checkstyle-8.29-all.jar \
# destination
    /praktomat/lib/


# set permissions
# RUN chmod 0644 /praktomat/lib/* /praktomat/extra/* \
RUN chmod 0644 /praktomat/lib/* \
    && chown praktomat:praktomat /praktomat/init_database.sh /praktomat/entrypoint.sh \
    && chmod u+x /praktomat/init_database.sh /praktomat/entrypoint.sh

# compile and install restrict.c
# RUN cd /praktomat/src && make restrict && sudo install -m 4750 -o root -g praktomat restrict /sbin/restrict

# change user
USER praktomat

# run entrypoint.sh as user praktomat
ENTRYPOINT ["/praktomat/entrypoint.sh"]


