from app import celery, graph_manager
from flask import current_app
from .utilities import handle_uploaded_file


@celery.task(queue="jobsQueue")
def update_literature_task():
    with current_app.app_context():
        graph_manager.update_diseases()


@celery.task(queue="jobsQueue")
def add_disease_task(mesh_term):
    with current_app.app_context():
        graph_manager.add_disease(mesh_term)


@celery.task(queue="jobsQueue")
def add_drugbank_task(filename, version):
    with current_app.app_context():
        graph_manager.update_drugbank(handle_uploaded_file(filename, ['xml']), version=version)


@celery.task(queue="jobsQueue")
def add_obo_task(filename, obo_type, version):
    with current_app.app_context():
        graph_manager.update_obo(handle_uploaded_file(filename, ['obo']), obo_type, version=version)


@celery.task(queue="jobsQueue")
def remove_structured_resource(resource_type, version):
    with current_app.app_context():
        graph_manager.remove_resource("{}_{}".format(resource_type, version))


@celery.task(queue="jobsQueue")
def calculate_pagerank_task():
    with current_app.app_context():
        graph_manager.calculate_pagerank()


@celery.task(queue="jobsQueue")
def calculate_node2vec_task(embedding_size):
    with current_app.app_context():
        graph_manager.calculate_node2vec(embedding_size)


@celery.task(queue="jobsQueue")
def update_ranking_task(model_name):
    with current_app.app_context():
        graph_manager.calculate_ranking(model_name)
