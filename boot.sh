#!/bin/sh
source venv/bin/activate
flask init_db
exec gunicorn -b 0.0.0.0:5000 "app:create_app()"
