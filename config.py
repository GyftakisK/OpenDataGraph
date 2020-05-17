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
    BROKER_URL = 'mongodb://{host}:{port}/{db_name}'.format(host=os.environ.get('MONGODB_HOST'),
                                                            port=os.environ.get('MONGODB_PORT'),
                                                            db_name=os.environ.get('MONGODB_NAME'))
    CELERY_RESULT_BACKEND = 'mongodb://{host}:{port}/{db_name}'.format(host=os.environ.get('MONGODB_HOST'),
                                                                       port=os.environ.get('MONGODB_PORT'),
                                                                       db_name=os.environ.get('MONGODB_NAME'))
