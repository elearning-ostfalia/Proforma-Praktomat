#!/bin/sh

echo "Docker entrypoint used"

# this script is executed in each worker 
# => do not initialise database here !


if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for PostgreSQL..."
    
#    while !</dev/tcp/$DB_HOST/$DB_PORT; do sleep 1; done;

#    while ! nc -z $DB_HOST $DB_PORT; do sleep 1; done;

    echo "PostgreSQL started"
fi

echo "assume that database is started"

#python manage.py flush --no-input
#python manage.py migrate
#python manage.py collectstatic --no-input

cd /praktomat/src

exec "$@"
