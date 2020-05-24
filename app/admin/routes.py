from app.admin import bp
from flask import render_template, flash, redirect, url_for, jsonify
from app.admin.forms import LiteratureForm, StructuredDrugbankForm, StructuredOboForm
from flask_login import login_required
from app import extractor


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def admin():
    literature_status = extractor.get_literature_status()
    structured_status = extractor.get_structured_resources_jobs_status()
    form_literature = LiteratureForm()
    if form_literature.submit1.data and form_literature.validate():
        flash('Job created for "{}"'.format(form_literature.mesh_term.data))
        return redirect(url_for("admin.admin"))

    form_drugbank = StructuredDrugbankForm()
    if form_drugbank.submit2.data and form_drugbank.validate():
        f = form_drugbank.xml_file.data
        flash('Job created for "{}"'.format(f.filename))
        return redirect(url_for("admin.admin"))

    form_obo = StructuredOboForm()
    if form_obo.submit3.data and form_obo.validate():
        f = form_obo.obo_file.data
        flash('Job created for "{}"'.format(f.filename))
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
    import time
    time.sleep(5)
    return jsonify({'message': 'Job created for literature update'})

