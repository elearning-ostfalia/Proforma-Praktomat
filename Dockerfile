# debian does not run with this dockerfile
# FROM debian:jessie
# FROM debian:buster
# focal: Ubuntu 20.04 LTS
# FROM ubuntu:focal
# => Python 3.8

# jammy: Ubuntu 22.04 LTS
# FROM ubuntu:jammy
# => Python 3.10

# bookworm => jammy
# FROM python:3.11.9-slim-bookworm
FROM python:3.11.9-bookworm
# FROM python:3.10.14-bookworm
# bullseye => focal
# FROM python:3.11.9-bullseye

MAINTAINER Ostfalia

ENV PYTHONUNBUFFERED 1
ARG PASSWORD=123
ARG LOCALE_PLAIN=de_DE
ARG LOCALE=${LOCALE_PLAIN}.UTF-8
ARG GROUP_ID=1234
ARG PRAKTOMAT_ID=1100
ARG TESTER_ID=1101
ARG DEBIAN_FRONTEND=noninteractive

# local-gen does not seem to work properly with debian images (with ubuntu it does)
# so we install locales-all :-(
#    locale-gen ${LOCALE} && \

# this is how to set locale for debian (from https://hub.docker.com/_/debian):
RUN apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/* \
	&& localedef -i ${LOCALE_PLAIN} -c -f UTF-8 -A /usr/share/locale/locale.alias ${LOCALE}

ENV LANG ${LOCALE}
ENV LC_ALL ${LOCALE}
ENV LANGUAGE ${LOCALE}

# libffi-dev is used for python unittests with pandas (avoid extra RUN command)
# squashfs-tools is used for sandbox templates
RUN apt-get update && \
    apt-get install -y swig libxml2-dev libxslt1-dev python3-pip python3-venv libpq-dev wget cron netcat-openbsd sudo \
    subversion git unzip \
    libffi-dev && \
    rm -rf /var/lib/apt/lists/*
#RUN apt-get update && apt-get install -y swig libxml2-dev libxslt1-dev python3 python3-pip libpq-dev locales wget cron netcat

# Java:
# install OpenJDK (for Java Compiler checks)
# install OpenJFK for GUI tests (for Java JFX tasks)
# install SVN (delete if you do not want to access submissions from SVN repository)
# install cmake and cunit for testing with cunit

# RUN apt-get update && apt-get install -y default-jdk openjfx subversion cmake libcunit1 libcunit1-dev

# install Java 17 from Bellsoft
# CHANGE 'arch=amd64' to something that fits your architecture
###RUN wget -q -O - https://download.bell-sw.com/pki/GPG-KEY-bellsoft | sudo apt-key add -
###RUN echo "deb [arch=amd64] https://apt.bell-sw.com/ stable main" | sudo tee /etc/apt/sources.list.d/bellsoft.list
###RUN sudo apt-get update && apt-get install -y bellsoft-java17

# Install Java 17 and JavaFX
RUN apt-get update && apt-get install -y openjdk-17-jdk openjfx && rm -rf /var/lib/apt/lists/*
# Install C, cmake, Googletest (must be compiled)
# pkg-config can be used to locate gmock (and other packages) after installation
RUN apt-get update && apt-get install -y cmake libcunit1 libcunit1-dev googletest pkg-config && \
    mkdir -p /tmp/googletest && cd /tmp/googletest && cmake /usr/src/googletest && cmake --build . && cmake --install . && \
    rm -rf /var/lib/apt/lists/*

# ADD UNIX USERS
################

# create group praktomat
RUN groupadd -g ${GROUP_ID} praktomat && \
# add user praktomat (uid=${PRAKTOMAT_ID}) \
  useradd -g ${GROUP_ID} -u ${PRAKTOMAT_ID} praktomat -s /bin/sh --home /praktomat --create-home --comment "Praktomat Demon" && \
  usermod -aG sudo praktomat && \
  echo "praktomat:$PASSWORD" | sudo chpasswd && \
# add user tester (uid=777) \
  useradd -g ${GROUP_ID} -u ${TESTER_ID} tester -s /bin/false --no-create-home -c "Test Execution User"

# allow user praktomat to execute 'sudo -u tester ...'
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
# COPY media media/




# create cron job for deleting temporary files (no dots in new filename)
COPY cron.conf /etc/cron.d/praktomat-cron
#COPY --chown=999:999 cron.conf /etc/cron.d/praktomat-cron
#RUN chmod 0644 /etc/cron.d/praktomat-cron

# add JAVA test specific libraries
# Checkstyle
ADD https://github.com/checkstyle/checkstyle/releases/download/checkstyle-10.1/checkstyle-10.1-all.jar /praktomat/lib/
ADD https://github.com/checkstyle/checkstyle/releases/download/checkstyle-8.23/checkstyle-8.23-all.jar /praktomat/lib/
ADD https://github.com/checkstyle/checkstyle/releases/download/checkstyle-8.29/checkstyle-8.29-all.jar /praktomat/lib/
# JUnit4 runtime libraries
ADD https://github.com/junit-team/junit4/releases/download/r4.12/junit-4.12.jar /praktomat/lib/
RUN wget http://www.java2s.com/Code/JarDownload/hamcrest/hamcrest-core-1.3.jar.zip && unzip -n hamcrest-core-1.3.jar.zip -d /praktomat/lib
# JUnit 5
ADD https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/1.6.1/junit-platform-console-standalone-1.6.1.jar /praktomat/lib/

RUN pip3 list && python3 --version && java -version

# set permissions
RUN chmod 0644 /praktomat/lib/* /praktomat/extra/*

# compile and install restrict.c
RUN cd /praktomat/src && make restrict && sudo install -m 4750 -o root -g praktomat restrict /sbin/restrict

# install fuse for sandbox templates
# user_allow_other is needed in or der to allow praktomat user to set option allow_other on mount
RUN apt-get update && apt-get install -y fuse3 unionfs-fuse squashfs-tools squashfuse fuse-overlayfs && \
    rm -rf /var/lib/apt/lists/* && \
    sed -i -e 's/^#user_allow_other/user_allow_other/' /etc/fuse.conf
# install tree and strace for debugging :-)
#    tree strace less nano && \

# RUN apt-get update && apt-get install -y libfuse3-dev automake unzip && \
#    wget https://github.com/containers/fuse-overlayfs/archive/refs/tags/v1.9.zip && \
#    unzip v1.9.zip && \
#    cd fuse-overlayfs-1.9 && sh ./autogen.sh && ./configure && make && mv /usr/bin/fuse-overlayfs /usr/bin/fuse-overlayfs.old && \
#    mv fuse-overlayfs /usr/bin/fuse-overlayfs

# change user
USER praktomat

# run entrypoint.sh as user praktomat
ENTRYPOINT ["/praktomat/entrypoint.sh"]


