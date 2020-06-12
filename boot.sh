#!/bin/sh
source venv/bin/activate
echo $(env)
if [ "$CONTAINER_TYPE" = "web" ]
then
    echo "Booting web..."
    flask init_db
    exec gunicorn -b 0.0.0.0:5000 "app:create_app()"
fi
if [ "$CONTAINER_TYPE" = "celery_worker" ]
then
    echo "Booting celery worker..."
    celery worker -A celery_worker.celery --pool threads --concurrency=1
fi
echo "Bye!"
