from app.admin import bp
from flask import render_template, flash, redirect, url_for
from app.admin.forms import LiteratureForm, StructuredDrugbankForm, StructuredOboForm
from flask_login import login_required


@bp.route('/')
@bp.route('/dashboard')
@login_required
def admin():
    return render_template('admin/dashboard.html')


@bp.route('literature', methods=['GET', 'POST'])
@login_required
def literature():
    form = LiteratureForm()
    if form.validate_on_submit():
        flash('Job created for "{}"'.format(form.mesh_term.data))
        return redirect(url_for("admin.literature"))
    return render_template('admin/literature.html', form=form)


@bp.route('structured', methods=['GET', 'POST'])
@login_required
def structured():
    form_drugbank = StructuredDrugbankForm()
    form_obo = StructuredOboForm()
    if form_drugbank.submit1.data and form_drugbank.validate():
        f = form_drugbank.xml_file.data
        flash('Job created for "{}"'.format(f.filename))
        return redirect(url_for("admin.structured"))
    if form_obo.submit2.data and form_obo.validate():
        f = form_obo.obo_file.data
        flash('Job created for "{}"'.format(f.filename))
        return redirect(url_for("admin.structured"))
    return render_template('admin/structured.html',
                           form_drugbank=form_drugbank,
                           form_obo=form_obo)
