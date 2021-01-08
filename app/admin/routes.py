import os
from app import graph_manager, db
from app.admin import bp
from flask import render_template, redirect, url_for, jsonify, current_app, request, abort
from app.admin.forms import LiteratureForm, StructuredDrugbankForm, StructuredOboForm
from flask_login import login_required, current_user
from functools import wraps
from werkzeug.utils import secure_filename
from app.tasks import (add_disease_task, update_literature_task, add_drugbank_task, add_obo_task,
                       remove_structured_resource, calculate_pagerank_task, calculate_node2vec_task,
                       update_ranking_task)
from app.utilities import flash_error, flash_success
from app.models import Task, User


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def save_task(task_id, task_name, task_inputs):
    task = Task(task_id=task_id, task_name=task_name,
                task_inputs=task_inputs, user_id=current_user.id)
    db.session.add(task)
    db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
@admin_required
def admin():
    literature_status = graph_manager.get_literature_status()
    structured_status = graph_manager.get_structured_resources_jobs_status()
    form_literature = LiteratureForm()
    if form_literature.submit1.data and form_literature.validate():
        mesh_term = form_literature.mesh_term.data
        if mesh_term in literature_status["mesh_terms"]:
            flash_error('Disease with MeSH term {} already in graph'.format(mesh_term))
            return redirect(url_for("admin.admin"))
        task = add_disease_task.apply_async([mesh_term])
        save_task(task.task_id, "add_disease_task", str({"mesh_term": mesh_term}))
        flash_success('Job {} created for "{}"'.format(task.task_id, mesh_term))
        return redirect(url_for("admin.admin"))

    form_drugbank = StructuredDrugbankForm()
    if form_drugbank.submit2.data and form_drugbank.validate():
        f = form_drugbank.xml_file.data
        filename = secure_filename(f.filename)
        version = form_drugbank.version.data
        if version in [resource["version"] for resource in structured_status
                       if resource["type"] == "DRUGBANK"]:
            flash_error('Drugbank XML with version {} already in graph'.format(version))
            return redirect(url_for("admin.admin"))
        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        f.save(filepath)
        task = add_drugbank_task.apply_async([filepath, version])
        save_task(task.task_id, "add_drugbank_task",
                  str({"filename": filename, "version": version}))
        flash_success('Job {} created for "{}"'.format(task.task_id, f.filename))
        return redirect(url_for("admin.admin"))

    form_obo = StructuredOboForm()
    if form_obo.submit3.data and form_obo.validate():
        f = form_obo.obo_file.data
        obo_type = dict(form_obo.obo_type.choices).get(form_obo.obo_type.data)
        version = form_obo.version.data
        if version in [resource["version"] for resource in structured_status
                       if resource["type"] == obo_type]:
            flash_error('OBO of type {} with version {} already in graph'.format(obo_type,
                                                                                 version))
            return redirect(url_for("admin.admin"))
        filename = secure_filename(f.filename)
        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        f.save(filepath)
        task = add_obo_task.apply_async([filepath, obo_type, version])
        save_task(task.task_id, "add_obo_task",
                  str({"filename": filename, "type": obo_type, "version": version}))
        flash_success('Job {} created for "{}"'.format(task.task_id, f.filename))
        return redirect(url_for("admin.admin"))

    tasks = Task.query.filter(Task.status.notin_(['SUCCESS', 'FAILURE'])).all()
    jobs = [{'task_id': task.task_id,
             'task_name': task.task_name,
             'task_inputs': task.task_inputs,
             'added_on': task.added_on,
             'user_email': task.get_creator_email(),
             'status': task.get_status()} for task in tasks]

    return render_template('admin/dashboard.html',
                           title="Admin dashboard",
                           mesh_terms=literature_status["mesh_terms"],
                           last_update=literature_status["last_update"],
                           structured_resources=structured_status,
                           form_literature=form_literature,
                           form_drugbank=form_drugbank,
                           form_obo=form_obo,
                           jobs=jobs)


@bp.route('update_literature', methods=['POST'])
@login_required
@admin_required
def update_literature():
    task = update_literature_task.apply_async()
    save_task(task.task_id, "update_literature_task",
              "")
    return jsonify({'message': 'Job {} created for literature update'.format(task.task_id)})


@bp.route('monitor_jobs', methods=['GET'])
@login_required
@admin_required
def monitor_jobs():
    tasks = Task.query.all()
    jobs = [{'task_id': task.task_id,
             'task_name': task.task_name,
             'task_inputs': task.task_inputs,
             'added_on': task.added_on,
             'user_email': task.get_creator_email(),
             'status': task.get_status()} for task in tasks]
    return render_template('admin/monitor_jobs.html',
                           title="Monitor Jobs",
                           jobs=reversed(jobs))


@bp.route('remove_resource', methods=['POST'])
@login_required
@admin_required
def remove_resource():
    resource_type = request.form.get("type")
    resource_version = request.form.get("version")
    # Retrieve data from the request and remove it from the database
    if resource_type and resource_version:
        task = remove_structured_resource.apply_async([resource_type, resource_version])
        save_task(task.task_id, "remove_structured_resource",
                  str({"resource_type": resource_type, "resource_version": resource_version}))
        json_content = {'return_code': 'SUCCESS',
                        'message': 'Job {} created for "{}_{}"'.format(task.task_id, resource_type, resource_version)}

    else:
        json_content = {'return_code': 'FAILURE',
                        'message': 'Invalid input'}
    return jsonify(json_content)


@bp.route('calculate_pagerank', methods=['POST'])
@login_required
@admin_required
def calculate_pagerank():
    task = calculate_pagerank_task.apply_async()
    save_task(task.task_id, "calculate_pagerank", "")
    return jsonify({'message': 'Job {} created for PageRank calculation'.format(task.task_id)})


@bp.route('calculate_node2vec', methods=['POST'])
@login_required
@admin_required
def calculate_node2vec():
    embedding_size = request.form.get("embeddingSize")
    task = calculate_node2vec_task.apply_async([embedding_size])
    save_task(task.task_id, "calculate_node2vec", str({"embeddingSize": embedding_size}))
    return jsonify({'message': 'Job {} created for Node2Vec calculation'.format(task.task_id)})


@bp.route('update_ranking', methods=['POST'])
@login_required
@admin_required
def update_ranking():
    model_name = request.form.get("modelName")
    task = update_ranking_task.apply_async([model_name])
    save_task(task.task_id, "update_ranking", str({"modelName": model_name}))
    return jsonify({'return_code': 'SUCCESS',
                    'message': 'Job {} created for node ranking update'.format(task.task_id)})


@bp.route('user_management', methods=['GET'])
@login_required
@admin_required
def user_management():
    users = User.query.all()
    return render_template('admin/users.html',
                           title="User Management",
                           users=sorted(users, key=lambda x: x.is_admin, reverse=True))


@bp.route('set_user_admin_rights', methods=['POST'])
@login_required
@admin_required
def set_user_admin_rights():
    req_data = request.get_json()
    user_id = int(req_data["userId"].strip("user"))
    if current_user.id == user_id:
        return jsonify({'return_code': 'ERROR',
                        'message': 'Changing your own administrative rights is forbidden'})

    is_admin = req_data["isAdmin"]
    user = User.query.get(user_id)
    user.is_admin = is_admin
    db.session.commit()
    return jsonify({'return_code': 'SUCCESS',
                    'message': '{} {} administrative rights'.format(user.username,
                                                                    "was given" if is_admin else "was striped of")})
