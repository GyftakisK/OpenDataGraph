#!/bin/bash
source venv/bin/activate
if [ "$CONTAINER_TYPE" = "web" ]
then
    echo "Booting web..."
    flask init_db
    gunicorn -b 0.0.0.0:5000 $GUNICORN_OPTIONS "app:create_app()"
fi
if [ "$CONTAINER_TYPE" = "celery_job_worker" ]
then
    echo "Booting celery jobs worker..."
    $METAMAP_DIR/bin/skrmedpostctl start
    $METAMAP_DIR/bin/wsdserverctl start
    celery worker -A celery_worker.celery --loglevel=INFO --pool threads --concurrency=1 -Q jobsQueue
fi
if [ "$CONTAINER_TYPE" = "celery_mail_worker" ]
then
    echo "Booting celery mail worker..."
    celery worker -A celery_worker.celery --loglevel=INFO --pool threads -Q mailQueue
fi
echo "Bye!"
