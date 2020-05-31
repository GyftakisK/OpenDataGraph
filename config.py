import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['gyftakiskon@gmail.com']
    BROKER_URL = 'mongodb://{host}:{port}/celery'.format(host=os.environ.get('MONGODB_HOST'),
                                                         port=os.environ.get('MONGODB_PORT'))
    CELERY_RESULT_BACKEND = 'mongodb://{host}:{port}/celery'.format(host=os.environ.get('MONGODB_HOST'),
                                                                    port=os.environ.get('MONGODB_PORT'))
    CELERY_IGNORE_RESULT = False
    CELERY_TRACK_STARTED = True
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
    MAX_CONTENT_PATH = 1024 * 1024 * 1024 * 10  # 10GB

