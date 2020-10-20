import py2neo


class NeoManager(object):
    def __init__(self, host: str, port: str, user: str, password: str):
        self.__graph = None
        self.__host = host
        self.__port = port
        self.__user = user
        self.__password = password

    def _connect(self):
        if not self.__graph:
            self.__graph = py2neo.Graph(sceme='http', host=self.__host, http_port=int(self.__port),
                                        user=self.__user, password=self.__password)

    def _run_query(self, query: str):
        self._connect()
        print("Running cypher query: {}".format(query))
        result = self.__graph.run(query)
        print("Query completed")
        return result

    def delete_all_orphan_nodes(self):
        query = "MATCH (n) WHERE NOT (n)--() DELETE n"
        self._run_query(query)

    def remove_item_from_list_property(self, property_name, item_name):
        query = 'MATCH ()-[r]->() ' \
                'WHERE "{item_name}" in r.{property_name} ' \
                'SET r.{property_name} = ' \
                'apoc.coll.removeAll(r.{property_name}, ["{item_name}"])'.format(item_name=item_name,
                                                                                 property_name=property_name)
        self._run_query(query)

    def delete_relationships_with_empty_list_property(self, property_name):
        query = 'MATCH ()-[r]->() WHERE r.{property_name} = [] DELETE r'.format(property_name=property_name)
        self._run_query(query)

    def create_in_memory_graph(self, graph_name: str):
        query = "CALL gds.graph.create('{graph_name}', '*', '*') " \
                "YIELD graphName, nodeCount, relationshipCount".format(graph_name=graph_name)
        self._run_query(query)

    def create_entity_only_in_memory_graph(self, graph_name: str):
        query = f"CALL gds.graph.create.cypher('{graph_name}', " \
                f"'MATCH (n:Entity)--(:Entity) RETURN DISTINCT id(n) AS id', " \
                f"'MATCH (n:Entity)--(m:Entity) RETURN id(n) AS source, id(m) AS target')"
        self._run_query(query)

    def drop_in_memory_graph(self, graph_name: str):
        query = f"CALL gds.graph.drop('{graph_name}') YIELD graphName;"
        self._run_query(query)

    def calculate_pagerank(self, graph_name: str, max_iterations: int, damping_factor: float):
        query = f"CALL gds.pageRank.write('{graph_name}', " \
                f"{{ maxIterations: {max_iterations}, " \
                f"dampingFactor: {damping_factor}, " \
                f"writeProperty: 'pagerank'}}) " \
                f"YIELD nodePropertiesWritten, ranIterations"
        self._run_query(query)

    def calculate_node2vec(self, graph_name: str, embedding_size: int = 128):
        query = f"CALL gds.alpha.node2vec.write('{graph_name}', {{embeddingSize: {embedding_size}, " \
                f"writeProperty: 'node2vec{embedding_size}'}})"
        self._run_query(query)

    def get_entities_matching_labels_beginning(self, search_string: str, limit: int):
        query = f"MATCH (n:Entity) WHERE n.label =~ '(?i){search_string}.*' " \
                f"RETURN n.label AS label LIMIT {limit}"
        result = self._run_query(query)
        return [node["label"] for node in result]

    def get_node_and_neighbors(self, node_label: str, num_of_neighbors: int, skip_nodes: int,
                               order_by: str = 'pagerank', excl_rel: list = [], excl_sem: list = []):
        query = f"MATCH (n:Entity) " \
                f"WHERE n.label = '{node_label}' " \
                f"RETURN n"
        result = self._run_query(query)
        node = next(result)["n"]

        query = "MATCH (n:Entity)-[r]-(m:Entity) " \
                "WHERE n.label = '{node_label}' AND NOT TYPE(r) IN {excl_rel} " \
                "AND none(x IN m.sem_types WHERE x IN {excl_sem})" \
                "RETURN r ORDER BY m.{order_by} " \
                "SKIP {skip_nodes} LIMIT {num_of_neighbors}".format(node_label=node_label,
                                                                    excl_rel=excl_rel,
                                                                    excl_sem=excl_sem,
                                                                    order_by=order_by,
                                                                    skip_nodes=skip_nodes,
                                                                    num_of_neighbors=num_of_neighbors)
        result = self._run_query(query)
        return node, [record["r"] for record in result]

    def get_neighbor_stats_for_node(self, node_label: str):
        query = f"MATCH (n:Entity)-[relationship]-(:Entity) " \
                f"WHERE n.label = '{node_label}' " \
                f"RETURN TYPE(relationship) AS type, COUNT(relationship) AS amount"
        result = self._run_query(query)
        relationship_counts = {record["type"]: record["amount"] for record in result}

        query = f"MATCH (n:Entity)-[relationship]-(m:Entity) " \
                f"WHERE n.label = '{node_label}' " \
                f"RETURN collect(m.sem_types) AS sem_types, COUNT(m) AS node_count"
        result = self._run_query(query)

        sem_types_counts = {}
        node_count = 0
        if result.forward():
            node_count = result.current["node_count"]
            for _list in result.current["sem_types"]:
                for sem_type in _list:
                    if sem_type in sem_types_counts:
                        sem_types_counts[sem_type] += 1
                    else:
                        sem_types_counts[sem_type] = 1

        return relationship_counts, sem_types_counts, node_count

    def get_articles_for_entity(self, node_label: str):
        query = f"MATCH(n: Entity)-[r]-(m:Article) " \
                f"WHERE n.label = '{node_label}' " \
                f"RETURN m.id, m.title, m.journal, type(r) AS rel, count(r.sent_id) AS occurrences"
        result = self._run_query(query)
        return [{"pmid": record["m.id"],
                 "title": record["m.title"],
                 "journal": record["m.journal"],
                 "rel": record["rel"],
                 "occurrences": record["occurrences"]} for record in result]

    def get_all_relationships_between_nodes_by_cui(self, cui_1: str, cui_2: str):
        query = f"MATCH (n:Entity)-[r]-(m:Entity) " \
                f"WHERE n.id = '{cui_1}' AND m.id = '{cui_2}' " \
                f"RETURN r"
        result = self._run_query(query)
        return [record["r"] for record in result]

    def get_articles_from_relationship(self, start_node_cui: str, end_node_cui: str, type: str):
        query = f"MATCH (n:Entity)-[r]-(m:Entity) " \
                f"WHERE n.id = '{start_node_cui}' AND m.id = '{end_node_cui}' AND TYPE(r) = '{type}' " \
                f"RETURN r.sent_id AS sent_ids"
        result = self._run_query(query)

        occurrences = {}
        for record in result:
            for sent_id in record["sent_ids"]:
                sent_id = sent_id.split('_')[0]
                if sent_id not in occurrences:
                    occurrences[sent_id] = 1
                else:
                    occurrences[sent_id] += 1

        query = f"MATCH (m:Article) " \
                f"WHERE m.id IN {list(occurrences.keys())} " \
                f"RETURN m.id, m.title, m.journal"
        result = self._run_query(query)
        return [{"pmid": record["m.id"],
                 "title": record["m.title"],
                 "journal": record["m.journal"],
                 "occurrences": occurrences[record["m.id"]]} for record in result]
