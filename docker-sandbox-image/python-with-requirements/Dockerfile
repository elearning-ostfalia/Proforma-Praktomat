FROM python:3.11.9-slim-bookworm

# set locale
ARG LOCALE_PLAIN=de_DE
ARG LOCALE=${LOCALE_PLAIN}.UTF-8

# this is how to set locale for debian (from https://hub.docker.com/_/debian):
RUN apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/* \
	&& localedef -i ${LOCALE_PLAIN} -c -f UTF-8 -A /usr/share/locale/locale.alias ${LOCALE}

ENV LANG ${LOCALE}
ENV LC_ALL ${LOCALE}
ENV LANGUAGE ${LOCALE}

# create user with less capabilties 
RUN useradd praktomat -s /bin/bash

# create sandbox folder and copy task and framework files into it, make writable
WORKDIR /sandbox
RUN chmod -R 777 /sandbox

# create result folder and set writable
RUN mkdir -p __result__ && chmod -R 777 __result__


# create folder for matplotlib cache (suppresses warning)
RUN mkdir -p .matplotlib && chmod -R 777 .matplotlib
ENV MPLCONFIGDIR=/sandbox/.matplotlib

ADD framework /sandbox
ADD entrypoint.sh /
RUN chmod 777 /entrypoint.sh

ADD task /sandbox

# extra für Tests
RUN pip3 install --upgrade pip && pip3 install xmlrunner

# install requirements
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

# change user
USER praktomat    

# run entrypoint.sh as user praktomat
ENTRYPOINT ["../entrypoint.sh"]