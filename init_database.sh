#!/bin/bash
DATABASE_INITIALISED=0

echo "create database"

if [ -e "$HOME/.DATABASE_INITIALISED" ];  then
    echo "Database is already created"
    exit 0
#else
#    echo "Initialise Database"
fi

echo "syncing database"
python ./src/manage.py syncdb --noinput --migrate
#if [ $? -ne 0 ]; then 
#    exit 1 
#fi

# clear python cache since there can be old files that confuse migrations
echo "clean python cache"
pyclean .
# py3clean does not delete cache files generated from source files that have been deleted since
find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

#echo "initialise schema files"
#python ./src/manage.py schemamigration checker --initial
#exit

# update tables in case of a modified or added checker
echo "migrate schema"

# do not use exit here!
python ./src/manage.py schemamigration checker --auto
# use initial in order to create initial migrations file
#python ./src/manage.py schemamigration checker --initial
echo "migrate checker"
python ./src/manage.py migrate checker || exit

echo "create users"
echo "from django.contrib.auth.models import User; User.objects.create_superuser('$SUPERUSER', '$EMAIL', '$PASSWORD')" | python ./src/manage.py shell --plain
echo "from django.contrib.auth.models import User; User.objects.create_user('sys_prod', '$EMAIL', '$PASSWORD')" | python ./src/manage.py shell --plain

# update media folder for nginx to serve static django files
echo "collect static files for webserver"
python ./src/manage.py collectstatic -i tiny_mce -i django_tinymce  -i django_extensions  --noinput || exit
#save it output the file
echo $DATABASE_INITIALISED > "$HOME/.DATABASE_INITIALISED"
echo "Database has been initialised successfully"  




