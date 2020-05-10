#!/usr/bin/env python


import argparse
from knowledge_extractor.knowledge_extractor import KnowledgeExtractor


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--add_disease", metavar='mesh_term',
                        help="Retrieve online articles relevant to a MeSH term from PubMed and PMC")
    parser.add_argument("--harvest_go", metavar='path_to_obo',
                        help="Process the OBO file of gene ontology")
    parser.add_argument("--harvest_do", metavar='path_to_obo',
                        help="Process the OBO file of disease ontology")
    parser.add_argument("--harvest_mesh", metavar='path_to_obo',
                        help="Process the OBO file of MeSH terms ontology")
    parser.add_argument("--harvest_drugbank", metavar='path_to_xml',
                        help="Process the XML file of DrugBank")
    parser.add_argument("--update_diseases", action='store_true',
                        help="Update diseases already in DB")

    args = parser.parse_args()

    disease_graph = KnowledgeExtractor()

    try:
        disease_graph.setup()
        if args.harvest_go:
            disease_graph.update_obo(args.harvest_go, "GO")
        if args.harvest_do:
            disease_graph.update_obo(args.harvest_do, "DO")
        if args.harvest_mesh:
            disease_graph.update_obo(args.harvest_mesh, "MESH")
        if args.harvest_drugbank:
            disease_graph.update_drugbank(args.harvest_drugbank)
        if args.add_disease:
            disease_graph.add_disease(args.add_disease)
        if args.update_diseases:
            disease_graph.update_diseases()
    finally:
        disease_graph.cleanup()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        exit(1)
    exit(0)
