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

    def drop_in_memory_graph(self, graph_name: str):
        query = "CALL gds.graph.drop('{graph_name}') YIELD graphName;".format(graph_name=graph_name)
        self._run_query(query)

    def calculate_pagerank(self, graph_name: str, max_iterations: int, damping_factor: float):
        query = "CALL gds.pageRank.write('{graph_name}', " \
                    "{{ maxIterations: {max_iterations}, " \
                    "dampingFactor: {damping_factor}, " \
                    "writeProperty: 'pagerank'}}) " \
                "YIELD nodePropertiesWritten, ranIterations".format(graph_name=graph_name,
                                                                    max_iterations=max_iterations,
                                                                    damping_factor=damping_factor)
        self._run_query(query)

    def get_entities_matching_labels_beginning(self, search_string: str, limit: int):
        query = f"MATCH (n:Entity) WHERE n.label =~ '(?i){search_string}.*' " \
                f"RETURN n.label AS label LIMIT {limit}"
        result = self._run_query(query)
        return [node["label"] for node in result]

    def get_node_and_neighbors(self, node_label: str, num_of_neighbors: int):
        query = f"MATCH (n:Entity) " \
                f"WHERE n.label = '{node_label}' " \
                f"RETURN n"
        result = self._run_query(query)
        node = result.data()[-1]["n"]

        query = f"MATCH (n:Entity)-[r]-(:Entity) " \
                f"WHERE n.label = '{node_label}' " \
                f"RETURN r LIMIT {num_of_neighbors}"
        result = self._run_query(query)
        return node, [record["r"] for record in result.data()]

    def get_articles_for_entity(self, node_label: str):
        query = f"MATCH(n: Entity)-[r]-(m:Article) " \
                f"WHERE n.label = '{node_label}' " \
                f"RETURN m.id, m.title, m.journal, type(r) AS rel"
        result = self._run_query(query)
        return [{"pmid": record["m.id"],
                 "title": record["m.title"],
                 "journal": record["m.journal"],
                 "rel": record["rel"]} for record in result.data()]
