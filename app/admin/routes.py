import os
from app.admin import bp
from flask import render_template, flash, redirect, url_for, jsonify, current_app
from app.admin.forms import LiteratureForm, StructuredDrugbankForm, StructuredOboForm
from flask_login import login_required
from werkzeug.utils import secure_filename
from app import extractor
from app.tasks import add_disease_task, update_literature_task, add_drugbank_task, add_obo_task


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def admin():
    literature_status = extractor.get_literature_status()
    structured_status = extractor.get_structured_resources_jobs_status()
    form_literature = LiteratureForm()
    if form_literature.submit1.data and form_literature.validate():
        task = add_disease_task.apply_async([form_literature.mesh_term.data])
        flash('Job {} created for "{}"'.format(task.task_id, form_literature.mesh_term.data))
        return redirect(url_for("admin.admin"))

    form_drugbank = StructuredDrugbankForm()
    if form_drugbank.submit2.data and form_drugbank.validate():
        f = form_drugbank.xml_file.data
        filename = secure_filename(f.filename)
        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        f.save(filepath)
        task = add_drugbank_task.apply_async([filepath, form_drugbank.version.data])
        flash('Job {} created for "{}"'.format(task.task_id, f.filename))
        return redirect(url_for("admin.admin"))

    form_obo = StructuredOboForm()
    if form_obo.submit3.data and form_obo.validate():
        f = form_obo.obo_file.data
        filename = secure_filename(f.filename)
        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        f.save(filepath)
        obo_type = dict(form_obo.obo_type.choices).get(form_obo.obo_type.data)
        task = add_obo_task.apply_async([filepath, obo_type, form_obo.version.data])
        flash('Job {} created for "{}"'.format(task.task_id, f.filename))
        return redirect(url_for("admin.admin"))

    return render_template('admin/dashboard.html',
                           title="Admin dashboard",
                           mesh_terms=literature_status["mesh_terms"],
                           last_update=literature_status["last_update"],
                           structured_resources=structured_status,
                           form_literature=form_literature,
                           form_drugbank=form_drugbank,
                           form_obo=form_obo)


@bp.route('update_literature', methods=['POST'])
@login_required
def update_literature():
    update_literature_task.apply_async()
    return jsonify({'message': 'Job created for literature update'})
