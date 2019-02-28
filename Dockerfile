FROM python:2.7


ENV DJANGO_VERSION 1.3.7
ENV DEFAULT_USER ecult
ENV DEFAULT_EMAIL user@localhost
ENV DEFAULT_PASS user

RUN mkdir /praktomat
WORKDIR /praktomat

# install build dependencies
RUN apt-get update && \
    apt-get install -y sudo git \
                       gcc gettext flex bison \
                       wget make dejagnu libsasl2-dev \
                       libssl-dev libxml2-dev libxslt1-dev \
                       libcunit1-dev libcunit1 swig sudo jclassinfo \
                       software-properties-common
#install java -> # https://github.com/dockerfile/java/tree/master/oracle-java8
RUN \
  echo oracle-java10-installer shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections && \
  add-apt-repository ppa:linuxuprising/java && \
  apt-get update && \
  apt-get install -y --allow-unauthenticated oracle-java10-installer && \
  rm -rf /var/lib/apt/lists/* && \
  rm -rf /var/cache/oracle-jdk8-installer

# Define commonly used JAVA_HOME variable
ENV JAVA_HOME /usr/lib/jvm/java-10-oracle

#### create upload directory for submission and testing
RUN mkdir upload
COPY README.md requirements.txt ./
COPY src/ src/
COPY extra extra/
COPY media media/

#### creates several directories and generates a python build script and build
RUN pip install --upgrade pip && \
    pip install -r requirements.txt --ignore-installed --force-reinstall --upgrade --no-cache-dir

# RUN python bootstrap.py && \
#    python ./bin/buildout

# sync db and migrate
RUN ./src/manage.py syncdb --noinput --migrate
# RUN ./src/manage.py schemamigration checker --auto && \
#    ./src/manage.py migrate checker
EXPOSE 8000
#### create superuser and sys_prod
RUN echo "from django.contrib.auth.models import User; User.objects.create_superuser('$DEFAULT_USER', '$DEFAULT_EMAIL', '$DEFAULT_PASS')" | python ./src/manage.py shell --plain
RUN echo "from django.contrib.auth.models import User; User.objects.create_user('sys_prod', '$DEFAULT_EMAIL', '$DEFAULT_PASS')" | python ./src/manage.py shell --plain
CMD [ "/usr/local/bin/python", "/praktomat/src/manage.py", "runserver", "0.0.0.0:8000"]
#ENTRYPOINT echo "Hello, praktomat"
# CMD [ "python", "./manage.py", "runserver", "0.0.0.0:8000", "--settings=mysite.settings.prod" ]
# command: bash -c "sleep 3 && python manage.py runserver_plus 0.0.0.0:80"
