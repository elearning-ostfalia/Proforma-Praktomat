This is the source distribution of Praktomat, a programming course manager.
<!--
Prerequisites
============
  We recommend to run Praktomat within Apache, using Postgresql as
  database.

  On a Debian or Ubuntu System, install the packages

    postgresql
    apache2-mpm-worker	

  (For installing packages use 'apt-get install': e.g. apt-get install postgresql)

  Praktomat requires some 3rd-Party libraries programs to run.
  On a Ubuntu/Debian System, these can be installed by installing the following packages:

    libpq-dev
    libmysqlclient-dev
    libsasl2-dev
    libssl-dev
    swig
    libapache2-mod-xsendfile

    sun-java8-jdk (from the "Canonical Parner" Repository) (TODO -> manual)
    junit
    dejagnu
    gcj-jdk (jfc-dump, for checking Submissions for use of javax.* etc)
    jclassinfo
   
    git-core

 For Checkstyle, we recommend getting checkstyle-all-4.4.jar  

    http://sourceforge.net/projects/checkstyle/files/checkstyle/4.4/


Python 2.7
==========
  Unfortunately, Praktomat currently requires Python 2.7

  On Ubuntu 11.04, Python2.7 is installed by default,
  but you may need to install the packages

    python2.7-dev
    python-setuptools
    python-psycopg2
    
    sudo easy_install -U setuptools

  On Linux-Distributions (Ubuntu 10.4 LTS, Debian squeeze) that 
  ship with Python 2.6, we recommend to compile and install
  python 2.7 manually from source, by installing required packages with:

    sudo apt-get build-dep python
    sudo apt-get install libdb4.8-dev libgdbm-dev  

  and then something like:

    wget http://www.python.org/ftp/python/2.7.1/Python-2.7.1.tar.bz2
    tar xjf Python-2.7.1.tar.bz2
    cd Python-2.7.1/
    ./configure --enable-shared
    make 
    make altinstall

  Make sure to use this binary when bootstrapping praktomat in 
  the Installation Step 2: 

    python2.7 bootstrap.py
 
mod_wsgi
========
  If you want to run praktomat from within Apachhe, you will need mod_wsgi.
  On Linux-Distributions that ship with Python 2.7 per default, install
  the package

    libapache2-mod-wsgi


  If you compiled Python 2.7 manually, you have to compile
  and install mod_wsgi manually, as well. Get the source from
    http://code.google.com/p/modwsgi/
  and make sure to configure it similiarly to:

    ./configure --with-python=/usr/local/bin/python2.7


 
-->

Installation 
============

-> look at install.md ;)

8. It should now be possible to start the developmet server with `./bin/praktomat runserver` or `./bin/praktomat runserver_plus`

9. Setup an administration account with `./bin/praktomat createsuperuser` if you haven't installed the test data which includes an "admin" account.

10. If you want to deploy the project using mod_wsgi in apache you could use `documentation/apache_praktomat_wsgi.conf` as a starting point. Don't forget to install `mod_xsendfile` to serve uploaded files. 


Update 
======

1. update the source with git from github

2. update python dependencies with `./bin/buildout`

3. backup your database(seriously!) and run `./bin/praktomat syncdb` to install any new 3rd party tables as well as `./bin/praktomat migrate` to update praktomats tables

## using external URIs

### create a task

Format-Version 1.0.1
`curl -X POST -F "filename.end=@filename_in_directory.end" http://{server}importTaskObject/V1.01 > ./output.html`

Format-Version 0.9.4
`curl -X POST -F "filename.end=@filename_in_directory.end" http://{server}importTaskObject/V2 > ./output.html`

### grade submission

file submission:
`curl -X POST -F "submission.zip=@submission.zip" http://{server}/external_grade/proforma/v1/task/{taskID} > ./output.html`

text_field-submission:
`curl --data-urlencode LONCAPA_student_response='public class ..' http://{server}/textfield/lcxml/{filename}/{taskID}`

## Todo

### createTask
- check POST
- check ZIP
- check task -> version
- validate
- create
- return TaskID