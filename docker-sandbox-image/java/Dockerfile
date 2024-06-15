FROM alpine:3.20


# set locale
ARG LOCALE_PLAIN=de_DE
ARG LOCALE=${LOCALE_PLAIN}.UTF-8

# todo: locale
# RUN apk add --no-cache --update musl musl-utils musl-locales tzdata
# ENV TZ=Europe/Berlin
# RUN cp /usr/share/zoneinfo/Europe/Berlin /etc/localtime
# RUN echo 'export LC_ALL=${LOCALE}' >> /etc/profile.d/locale.sh && \
#  sed -i 's|LANG=C.UTF-8|LANG=${LOCALE}|' /etc/profile.d/locale.sh \


ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk
ENV MAVEN_HOME=/usr/share/maven

RUN apk add --no-cache openjdk21
# RUN apk add --no-cache openjdk21 maven openjfx

ENV PATH=$JAVA_HOME/bin:$MAVEN_HOME/bin:$PATH

LABEL maintainer="Ostfalia"
LABEL version="1.0"
LABEL description="Dockerfile for JDK 21 and Maven"


ARG PRAKTOMAT_ID=1100

# ADD https://download2.gluonhq.com/openjfx/21.0.3/openjfx-21.0.3_linux-x64_bin-sdk.zip /usr/share/openjfx/lib/
# RUN unzip /usr/share/openjfx/lib/openjfx-21.0.3_linux-x64_bin-sdk.zip

ADD https://download2.gluonhq.com/openjfx/21.0.3/openjfx-21.0.3_linux-x64_bin-sdk.zip /
RUN unzip /openjfx-21.0.3_linux-x64_bin-sdk.zip && mv /javafx-sdk-21.0.3 /usr/share/openjfx && rm /openjfx-21.0.3_linux-x64_bin-sdk.zip

# RUN mkdir -p /usr/share/openjfx/lib && unzip /openjfx-21.0.3_linux-x64_bin-sdk.zip -d /usr/share/openjfx/lib

ADD extra /praktomat/extra


# add JAVA test specific libraries
# Checkstyle
ADD https://github.com/checkstyle/checkstyle/releases/download/checkstyle-10.17.0/checkstyle-10.17.0-all.jar \
    https://github.com/checkstyle/checkstyle/releases/download/checkstyle-10.1/checkstyle-10.1-all.jar \
    https://github.com/checkstyle/checkstyle/releases/download/checkstyle-8.23/checkstyle-8.23-all.jar \
    https://github.com/checkstyle/checkstyle/releases/download/checkstyle-8.29/checkstyle-8.29-all.jar \
# JUnit4 runtime libraries
    https://github.com/junit-team/junit4/releases/download/r4.12/junit-4.12.jar \
# JUnit 5
    https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/1.6.1/junit-platform-console-standalone-1.6.1.jar \
# destination
    http://www.java2s.com/Code/JarDownload/hamcrest/hamcrest-core-1.3.jar.zip \
    /praktomat/lib/

RUN cd /praktomat/lib && unzip hamcrest-core-1.3.jar.zip && rm hamcrest-core-1.3.jar.zip

# set permissions
# RUN chmod -R 0644 /praktomat/lib /praktomat/extra
RUN find /praktomat -type d -exec chmod 755 {} \; \
    && find /praktomat -type f -exec chmod 644 {} \;


# create sandbox folder and copy framework files into it
WORKDIR /sandbox

RUN chmod -R 777 /sandbox

# add user praktomat
RUN adduser -u ${PRAKTOMAT_ID} praktomat -s /bin/ash --disabled-password

# change user
USER praktomat


