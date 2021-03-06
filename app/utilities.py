import glob
import os
from flask import flash
from zipfile import ZipFile


def flash_info(message):
    flash(message, "info")


def flash_error(message):
    flash(message, "danger")


def flash_success(message):
    flash(message, "success")


def is_extension_allowed(filename: str, allowed_extensions: list):
    return filename.split('.')[-1].lower() in allowed_extensions


def handle_uploaded_file(filename: str, allowed_extensions: list):
    if filename.endswith('zip'):
        with ZipFile(filename) as myzip:
            namelist = myzip.namelist()
            if len(myzip.namelist()) > 1:
                raise Exception("Too many files in zip file {}".format(filename))
            file_in_zip = namelist[-1]
            if not is_extension_allowed(file_in_zip, allowed_extensions):
                raise Exception("Not allowed file extension")
            return myzip.extract(member=file_in_zip, path=os.path.dirname(filename))

    if not is_extension_allowed(filename, allowed_extensions):
        raise Exception("Not allowed file extension")
    else:
        return filename


def relationships_to_d3_data(query_node, relationships):
    nodes = {query_node.identity: {"id": query_node.identity,
                                   "cui": query_node["id"],
                                   "label": query_node["label"],
                                   "sem_types": query_node["sem_types"]}}

    links = []

    for relationship in set(relationships):
        start_node = relationship.start_node
        end_node = relationship.end_node
        for node in (start_node, end_node):
            if node.identity not in nodes:
                nodes[node.identity] = {"id": node.identity,
                                        "cui": node["id"],
                                        "label": node["label"],
                                        "sem_types": node["sem_types"]}
        links.append({"source": nodes[start_node.identity]["id"],
                      "target": nodes[end_node.identity]["id"],
                      "type": type(relationship).__name__})
    return {"nodes": list(nodes.values()), "links": links}


def delete_all_files_with_extension(path: str, extension: str):
    """
    Deletes all files with specified expression under given path (best effort)
    :param path:
    :param extension:
    :return:
    """

    file_list = glob.glob(os.path.join(path, f'*.{extension}'))

    for file_path in file_list:
        try:
            os.remove(file_path)
        except:
            pass


def normilize_mesh_term(mesh_term: str):
    """
    Reverse words in comma separated MeSH terms
    :param mesh_term: a MeSH term (e.g. Muscular Dystrophy, Duchenne)
    :return: MeSH term without comma suffixed with the word after comma
             (e.g. Duchenne Muscular Dystrophy)
    """
    if "," not in mesh_term:
        return mesh_term

    substrings = mesh_term.split(",")
    return " ".join([substring.strip() for substring in substrings[::-1]])