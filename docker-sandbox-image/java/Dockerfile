FROM alpine:3.20

ARG PRAKTOMAT_ID=1100

# set locale
# THIS DOES NOT CHANGE THE LOCALE OF THE JDK OUTPUT!
# ARG LOCALE_PLAIN=de_DE
# ARG LOCALE=${LOCALE_PLAIN}.UTF-8
# RUN apk add --no-cache --update musl musl-utils musl-locales tzdata
# ENV TZ=Europe/Berlin
# RUN cp /usr/share/zoneinfo/Europe/Berlin /etc/localtime \
#    && echo 'export LC_ALL=${LOCALE}' >> /etc/profile.d/locale.sh \
#    && sed -i 's|LANG=C.UTF-8|LANG=${LOCALE}|' /etc/profile.d/locale.sh


RUN apk add --no-cache openjdk21

# Add JFX
ADD https://download2.gluonhq.com/openjfx/21.0.3/openjfx-21.0.3_linux-x64_bin-sdk.zip /

COPY extra /praktomat/extra

# add JAVA test specific libraries
# Checkstyle tests do not run in sandbox
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


RUN unzip /openjfx-21.0.3_linux-x64_bin-sdk.zip && mv /javafx-sdk-21.0.3 /usr/share/openjfx && rm /openjfx-21.0.3_linux-x64_bin-sdk.zip \
    && cd /praktomat/lib && unzip hamcrest-core-1.3.jar.zip && rm hamcrest-core-1.3.jar.zip \
# set permissions for folder and files in /praktomat
    && find /praktomat -type d -exec chmod 755 {} \; \
    && find /praktomat -type f -exec chmod 644 {} \; \
    # change permissions for sandbox (allow everything)
    # add user praktomat
    && adduser -u ${PRAKTOMAT_ID} praktomat -s /bin/ash --disabled-password



# create sandbox folder
WORKDIR /sandbox

RUN chmod -R 777 /sandbox

# change user
USER praktomat

