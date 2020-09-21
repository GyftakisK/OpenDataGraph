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
    nodes = {query_node.identity: {"id": 0, "cui": query_node["id"], "label": query_node["label"]}}
    links = []
    node_id = 1
    for relationship in relationships:
        start_node = relationship.start_node
        end_node = relationship.end_node
        for node in (start_node, end_node):
            if node.identity not in nodes:
                nodes[node.identity] = {"id": node_id, "cui": node["id"], "label": node["label"]}
                node_id += 1
        links.append({"source": nodes[start_node.identity]["id"], "target": nodes[end_node.identity]["id"],
                      "type": type(relationship).__name__, "weight": 1})
    return {"nodes": list(nodes.values()), "links": links}

