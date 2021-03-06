import os
from app import graph_manager
from app.main import bp
from flask import render_template, request, jsonify
from app.utilities import relationships_to_d3_data, normilize_mesh_term


@bp.route('/')
@bp.route('/index')
def index():
    literature_status = graph_manager.get_literature_status()
    diseases = [normilize_mesh_term(mesh_term) for mesh_term in literature_status["mesh_terms"]]
    node_counts, entity_rel_type_counts, article_rel_type_counts = graph_manager.get_graph_info()
    return render_template('main/index.html',
                           diseases=f'{", ".join(diseases[:-1])} and {diseases[:-1]}' if len(diseases) > 1
                                    else f'{diseases[0]}',
                           node_counts=node_counts,
                           ent_relationship_count=len(entity_rel_type_counts),
                           art_relationship_count=len(article_rel_type_counts))


@bp.route('/browse')
def browse():
    return render_template('main/browse.html')


@bp.route('/autocomplete', methods=['GET'])
def autocomplete():
    search_term = request.args.get('q')
    matches = []
    matches.extend(graph_manager.get_neo4j_manager().get_entities_matching_label(search_term, 15, 'ranking'))
    lexicographical_matches = graph_manager.get_neo4j_manager().get_entities_matching_labels_beginning(search_term, 15, 'ranking')
    matches.extend([match for match in lexicographical_matches if match not in matches])
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

        db_manager = graph_manager.get_neo4j_manager()
        query_node, relationships = db_manager.get_node_and_neighbors(node_label=node_label,
                                                                      num_of_neighbors=number_of_neighbours,
                                                                      skip_nodes=skip_nodes,
                                                                      excl_rel=excl_rel,
                                                                      excl_sem=excl_sem)
        skip_nodes = skip_nodes + len(relationships)
        if frozen_sets:
            for cui_1, cui_2 in frozen_sets:
                relationships.extend(db_manager.get_all_relationships_between_nodes_by_cui(cui_1, cui_2))
        data = relationships_to_d3_data(query_node, relationships)
        data["query_node_id"] = query_node.identity
        data['skip_nodes'] = skip_nodes
        return jsonify(data)
    else:
        return "Invalid term"


@bp.route('/articles', methods=['POST'])
def articles():
    req_data = request.get_json()
    if not req_data:
        return "Invalid JSON"

    node_label = req_data.setdefault('node_label', None)
    start_cui = req_data.setdefault('start_cui', None)
    end_cui = req_data.setdefault('end_cui', None)
    rel_type = req_data.setdefault('rel_type', None)

    db_manager = graph_manager.get_neo4j_manager()

    if node_label:
        data = db_manager.get_articles_for_entity(node_label)
    elif start_cui and end_cui and rel_type:
        data = db_manager.get_articles_from_relationship(start_node_cui=start_cui,
                                                         end_node_cui=end_cui,
                                                         type=rel_type)
    else:
        return "Invalid input"
    return jsonify(data)


@bp.route('/node', methods=['POST'])
def node():
    req_data = request.get_json()
    if req_data:
        node_label = req_data['label']

        db_manager = graph_manager.get_neo4j_manager()
        relationship_counts, sem_types_counts, node_count = db_manager.get_neighbor_stats_for_node(node_label)
        return jsonify({"relationship_counts": relationship_counts, "sem_types_counts": sem_types_counts,
                        "node_count": node_count})
    else:
        return "Invalid term"
