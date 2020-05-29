from flask import current_app
from app import celery, extractor


@celery.task
def update_literature_task():
    with current_app.app_context():
        extractor.update_diseases()


@celery.task
def add_disease_task(mesh_term):
    with current_app.app_context():
        extractor.add_disease(mesh_term)


@celery.task
def add_drugbank_task(filename, version):
    with current_app.app_context():
        extractor.update_drugbank(filename, version=version)


@celery.task
def add_obo_task(filename, obo_type, version):
    with current_app.app_context():
        extractor.update_obo(filename, obo_type, version=version)
