import os
from app.main import bp
from flask import render_template, request, jsonify
from db_manager.neo4j_manager import NeoManager


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
