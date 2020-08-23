from flask import current_app
from app import celery, extractor


@celery.task(queue="jobsQueue")
def update_literature_task():
    with current_app.app_context():
        extractor.update_diseases()


@celery.task(queue="jobsQueue")
def add_disease_task(mesh_term):
    with current_app.app_context():
        extractor.add_disease(mesh_term)


@celery.task(queue="jobsQueue")
def add_drugbank_task(filename, version):
    with current_app.app_context():
        extractor.update_drugbank(filename, version=version)


@celery.task(queue="jobsQueue")
def add_obo_task(filename, obo_type, version):
    with current_app.app_context():
        extractor.update_obo(filename, obo_type, version=version)


@celery.task(queue="jobsQueue")
def remove_structured_resource(resource_type, version):
    with current_app.app_context():
        extractor.remove_resource("{}_{}".format(resource_type.upper(), version))
