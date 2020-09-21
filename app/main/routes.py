import os
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
    node_label = request.form.get('label')
    host = os.environ.get('NEO4J_HOST')
    port = os.environ.get('NEO4J_PORT')
    user = os.environ.get('NEO4J_USER')
    password = os.environ.get('NEO4J_PASS')
    node, relationships = NeoManager(host, port, user, password).get_node_and_neighbors(node_label, 10)
    data = relationships_to_d3_data(node, relationships)
    data["query_node_id"] = node.identity
    return jsonify(data)


@bp.route('/articles', methods=['POST'])
def articles():
    node_label = request.form.get('label')
    host = os.environ.get('NEO4J_HOST')
    port = os.environ.get('NEO4J_PORT')
    user = os.environ.get('NEO4J_USER')
    password = os.environ.get('NEO4J_PASS')
    data = NeoManager(host, port, user, password).get_articles_for_entity(node_label)
    return jsonify(data)
