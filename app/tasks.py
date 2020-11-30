import os
from app import celery, extractor
from db_manager.neo4j_manager import NeoManager
from flask import current_app
from node_ranker.ml_ranker import MLRanker
from .utilities import handle_uploaded_file


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
        extractor.update_drugbank(handle_uploaded_file(filename, ['xml']), version=version)


@celery.task(queue="jobsQueue")
def add_obo_task(filename, obo_type, version):
    with current_app.app_context():
        extractor.update_obo(handle_uploaded_file(filename, ['obo']), obo_type, version=version)


@celery.task(queue="jobsQueue")
def remove_structured_resource(resource_type, version):
    with current_app.app_context():
        extractor.remove_resource("{}_{}".format(resource_type, version))


@celery.task(queue="jobsQueue")
def calculate_pagerank_task():
    with current_app.app_context():
        extractor.calculate_pagerank()


@celery.task(queue="jobsQueue")
def calculate_node2vec_task(embedding_size):
    with current_app.app_context():
        extractor.calculate_node2vec(embedding_size)


@celery.task(queue="jobsQueue")
def update_ranking_task(model_name):
    with current_app.app_context():
        ranker = MLRanker()
        ranker.load_model(model_name)
        db_manager = NeoManager(os.environ.get('NEO4J_HOST'), os.environ.get('NEO4J_PORT'),
                                os.environ.get('NEO4J_USER'), os.environ.get('NEO4J_PASS'))

        node_count = db_manager.get_count_of_entities_linked_to_other_entities()
        node_count_with_pagerank = db_manager.get_count_of_entities_with_pagerank()
        node_count_with_node2vec32 = db_manager.get_count_of_entities_with_node2vec32()

        if node_count != node_count_with_pagerank:
            extractor.calculate_pagerank()

        if node_count != node_count_with_node2vec32:
            extractor.calculate_node2vec(32)

        db_manager.remove_entities_ranking()
        current_index = 0
        increment = 1000
        min_ranking = 10000000
        while current_index < node_count:

            feature_data = db_manager.get_node_features(limit=increment, skip=current_index)

            nodes_rank = ranker.rank_nodes(feature_data)

            db_manager.set_nodes_ranking(nodes_rank)
            min_ranking = min(min(nodes_rank.values()), min_ranking)
            current_index += increment

        unranked_nodes = db_manager.get_entities_without_ranking()
        min_ranking -= 1.0
        db_manager.set_nodes_ranking({node_id: min_ranking for node_id in unranked_nodes})
