import os
import functools
from app.main import bp
from flask import render_template, request, jsonify
from db_manager.neo4j_manager import NeoManager
from app.utilities import relationships_to_d3_data


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('main/index.html')


@bp.route('/browse')
def browse():
    return render_template('main/browse.html')


@bp.route('/autocomplete', methods=['GET'])
def autocomplete():
    search_term = request.args.get('q')
    host = os.environ.get('NEO4J_HOST')
    port = os.environ.get('NEO4J_PORT')
    user = os.environ.get('NEO4J_USER')
    password = os.environ.get('NEO4J_PASS')
    matches = NeoManager(host, port, user, password).get_entities_matching_labels_beginning(search_term, 10)
    return jsonify(matching_results=matches)


@bp.route('/graph', methods=['POST'])
def graph():
    req_data = request.get_json()
    if req_data:
        node_label = req_data['label']
        frozen_sets = req_data['frozen']
        number_of_neighbours = req_data['number_of_neighbours']
        skip_nodes = req_data['skip_nodes']
        excl_rel = req_data["excluded_relationships"]
        excl_sem = req_data["excluded_semantic_types"]

        db_manager = NeoManager(os.environ.get('NEO4J_HOST'), os.environ.get('NEO4J_PORT'), os.environ.get('NEO4J_USER'),
                                os.environ.get('NEO4J_PASS'))
        node, relationships = db_manager.get_node_and_neighbors(node_label=node_label,
                                                                num_of_neighbors=number_of_neighbours,
                                                                skip_nodes=skip_nodes,
                                                                excl_rel=excl_rel,
                                                                excl_sem=excl_sem)
        skip_nodes = skip_nodes + len(relationships)
        if frozen_sets:
            for cui_1, cui_2 in frozen_sets:
                relationships.extend(db_manager.get_all_relationships_between_nodes_by_cui(cui_1, cui_2))
        data = relationships_to_d3_data(node, relationships)
        data["query_node_id"] = node.identity
        relationship_counts, sem_types_counts = db_manager.get_neighbor_stats_for_node(node_label)
        data["relationship_counts"] = relationship_counts
        data["sem_types_counts"] = sem_types_counts
        data['skip_nodes'] = skip_nodes
        data["total_relationships"] = functools.reduce((lambda a, b: a + b),
                                                       [count for count in relationship_counts.values()])
        return jsonify(data)
    else:
        return "Invalid term"


@bp.route('/articles', methods=['POST'])
def articles():
    node_label = request.form.get('label')
    host = os.environ.get('NEO4J_HOST')
    port = os.environ.get('NEO4J_PORT')
    user = os.environ.get('NEO4J_USER')
    password = os.environ.get('NEO4J_PASS')
    data = NeoManager(host, port, user, password).get_articles_for_entity(node_label)
    return jsonify(data)
