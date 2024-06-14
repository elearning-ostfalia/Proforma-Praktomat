
# jammy: Ubuntu 22.04 LTS
FROM ubuntu:jammy
# => Python 3.10

MAINTAINER Ostfalia

ENV PYTHONUNBUFFERED 1
ARG PASSWORD=123

ARG PRAKTOMAT_ID=1100


# set locale to German (UTF-8)
ARG LOCALE=de_DE.UTF-8

ARG DEBIAN_FRONTEND=noninteractive

# change locale to something UTF-8
RUN apt-get update && apt-get install -y locales && locale-gen ${LOCALE} && rm -rf /var/lib/apt/lists/*
ENV LANG ${LOCALE}
ENV LC_ALL ${LOCALE}


# libffi-dev is used for python unittests with pandas (avoid extra RUN command)
# squashfs-tools is used for sandbox templates
RUN apt-get update \
    && apt-get install -y wget \
    && rm -rf /var/lib/apt/lists/*

# Java:
# install OpenJDK (for Java Compiler checks)
# install OpenJFK for GUI tests (for Java JFX tasks)

# RUN apt-get update && apt-get install -y default-jdk openjfx subversion cmake libcunit1 libcunit1-dev

# install Java 17 from Bellsoft
# CHANGE 'arch=amd64' to something that fits your architecture
###RUN wget -q -O - https://download.bell-sw.com/pki/GPG-KEY-bellsoft | sudo apt-key add -
###RUN echo "deb [arch=amd64] https://apt.bell-sw.com/ stable main" | sudo tee /etc/apt/sources.list.d/bellsoft.list
###RUN sudo apt-get update && apt-get install -y bellsoft-java17

# Install Java 17 and JavaFX
RUN apt-get update && apt-get install -y openjdk-21-jdk openjfx && rm -rf /var/lib/apt/lists/*
# Install C, cmake, Googletest (must be compiled)
# pkg-config can be used to locate gmock (and other packages) after installation
# RUN apt-get update && apt-get install -y cmake libcunit1 libcunit1-dev googletest pkg-config && \
#    mkdir -p /tmp/googletest && cd /tmp/googletest && cmake /usr/src/googletest && cmake --build . && cmake --install . && \
#    rm -rf /var/lib/apt/lists/*






# add JAVA test specific libraries
# Checkstyle
ADD https://github.com/checkstyle/checkstyle/releases/download/checkstyle-10.17.0/checkstyle-10.17.0-all.jar /praktomat/lib/
ADD https://github.com/checkstyle/checkstyle/releases/download/checkstyle-10.1/checkstyle-10.1-all.jar /praktomat/lib/
ADD https://github.com/checkstyle/checkstyle/releases/download/checkstyle-8.23/checkstyle-8.23-all.jar /praktomat/lib/
ADD https://github.com/checkstyle/checkstyle/releases/download/checkstyle-8.29/checkstyle-8.29-all.jar /praktomat/lib/
# JUnit4 runtime libraries
ADD https://github.com/junit-team/junit4/releases/download/r4.12/junit-4.12.jar /praktomat/lib/
RUN wget http://www.java2s.com/Code/JarDownload/hamcrest/hamcrest-core-1.3.jar.zip && unzip -n hamcrest-core-1.3.jar.zip -d /praktomat/lib
# JUnit 5
ADD https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/1.6.1/junit-platform-console-standalone-1.6.1.jar /praktomat/lib/

# set permissions
RUN chmod 0644 /praktomat/lib/* /praktomat/extra/*

# create sandbox folder and copy framework files into it
WORKDIR /sandbox

RUN chmod -R 777 /sandbox

# add user praktomat
RUN useradd -u ${PRAKTOMAT_ID} praktomat -s /bin/bash

# change user
USER praktomat


