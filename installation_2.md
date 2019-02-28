# Praktomat Installation Guide for Ubuntu 16.04 LTS

## Installation Process

Praktomat requires some packages for a base installation (Postgresql, Python2.7,....). 

In addition further packages are needed in order to perform the grading functionality depending on the specific needs. E.g. if JUnit tests shall be performed JUnit must be installed. If DejaGnu tests are needed then you need to install DejaGnu.

Praktomat runs on Linux OS, either on a physical or a virtual machine. Network access shall be configured and running (with DHCP or static IP address). The installation guide assumes apt-get to be available.

Several Linux packages must be installed. You can get and install them easily with
    
    apt-get install ....

Since most installation requires administration (root) rights you must call 
    
    sudo apt-get install ....
    
instead.    
    
With 

    sudo aptitude 
    
you can easily view what packages are available. You can also use it for installation.


## Prerequisites
    
The following installation guide is tested under **Ubuntu Server 16.04 LTS (64 bit)**. With Ubuntu 14.04 Server LTS it failed.     
    
#### update apt-get 

In order to avoid problems with an outdated package list you should call 

    sudo apt-get update

at first.

#### get packages

Then retrieve the needed packages:

    sudo apt-get install apache2
    sudo apt-get install postgresql
    sudo apt-get install postgresql-server-dev-xxx
    
Replace xxx with the postgres version you have installed.

    sudo apt-get install swig
    sudo apt-get install git
    sudo apt-get install python2.7    
    sudo apt-get install libxml2-dev libxslt1-dev python-dev        
    sudo apt-get install python-pip

Install requirements for cunit-tests

sudo apt-get install libcunit1-dev
sudo apt-get install libcunit1

Note: With 

    pip freeze 
   
you get a list of the installed pip packages.


#### upgrade pip

    sudo pip install --upgrade pip

## Get Praktomat software    
    
Create a sub directory for your Praktomat code.

    mkdir justGrade
    cd justGrade
    
Fetch Praktomat code from GitLab.    
    
    git clone http://141.41.9.49/ostfalia/praktomat .

This installs (copies) the whole Praktomat source code into the subdirectory justGrade.

Note:

* You need to replace the IP address by the appropriate location. 
* The Dot (.) at the end of the command prevents git from creating a new subdirectory. 
* Git asks you for user name and password. 
* Of course you can also copy the source code from another source if you do not have a git account.
 
## Praktomat Configuration 

#### create upload directory for submission and testing

    mkdir upload

#### install python packages

    sudo pip install -r requirements.txt


#### use the existing files

    python bootstrap.py

creates several directories and generates a python build script. 

#### run build script

    python ./bin/buildout

#### create Postgres User 'pm_version2user'

    sudo -u postgres createuser -E -P pm_version2user
    
> PW : 1234123.


#### create Postgres Database 'pmversion2db'

    sudo -u postgres createdb -O pm_version2user -E UTF8 pmversion2db

just in case you want to delete a database

    sudo -u postgres dropdb $datenbankname


#### configure src/settings_local.py

this should be False when productive

    DEBUG = True
    
Set upload directory to the appropriate path:    

    UPLOAD_ROOT = /home/user/justGrade/upload

Replace user with the user name.

Set database configuration:

    DATABASE_NAME = 'pmversion2db'
    DATABASE_USER = 'pm_version2user'
    DATABASE_PASSWORD = '1234123.'    

Set directory names of the compiler binaries.

    JVM = /home/user/justGrade/src/checker/scripts/java
    CHECKSTYLEALLJAR= ...
    ....

Set the URL:

    BASE_URL = 'http://127.0.0.1:8000/'

Set the IP address according to your machine or to its hostname.

#### Create database tables and test your praktomat

Finally create database tables:

    ./bin/praktomat syncdb
    

Answer question

    You just installed Django's auth system, which means you don't have any superusers defined.
    Would you like to create one now? (yes/no): no
    
with no.    
   
#### Migrate  
   
    ./bin/praktomat migrate   

(If there is a new checker: ???)

    ./bin/praktomat schemamigration checker --auto

    ./bin/praktomat migrate checker

#### create superuser

    ./bin/praktomat createsuperuser
    
> admin adminpw    

## Install Further Packages for Grading 

## Installing Oracle Java

    sudo add-apt-repository ppa:webupd8team/java
    
    sudo apt-get update

    sudo apt-get install oracle-java8-installer

check with

    java -version 
    
## Run Praktomat

    ./bin/praktomat runserver_plus 127.0.0.1:8000

Set to your IP address or hostname!

Maybe you need to reboot your machine to get a connection from within a browser. 

## Connect to Praktomat from browser

Type in a new browser window

    http://127.0.0.1:8000
    
(use your Praktomat server IP address or hostname)

    DejaGnu?
    CheckStyle?
    JUnit?



