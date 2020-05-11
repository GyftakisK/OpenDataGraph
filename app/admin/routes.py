from app.admin import bp
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app.admin.forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User


@bp.route('/')
@bp.route('/dashboard')
@login_required
def admin():
    return render_template('admin/dashboard.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('Invalid username')
            return render_template('admin/login.html', title='Sign In', form=form)
        if not user.check_password(form.password.data):
            flash('Invalid password')
            return render_template('admin/login.html', title='Sign In', form=form)
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('admin/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('literature')
@login_required
def literature():
    return render_template('admin/literature.html')


@bp.route('structured')
@login_required
def structured():
    return render_template('admin/structured.html')

    # parser = argparse.ArgumentParser()
    # parser.add_argument("--add_disease", metavar='mesh_term',
    #                     help="Retrieve online articles relevant to a MeSH term from PubMed and PMC")
    # parser.add_argument("--harvest_go", metavar='path_to_obo',
    #                     help="Process the OBO file of gene ontology")
    # parser.add_argument("--harvest_do", metavar='path_to_obo',
    #                     help="Process the OBO file of disease ontology")
    # parser.add_argument("--harvest_mesh", metavar='path_to_obo',
    #                     help="Process the OBO file of MeSH terms ontology")
    # parser.add_argument("--harvest_drugbank", metavar='path_to_xml',
    #                     help="Process the XML file of DrugBank")
    # parser.add_argument("--update_diseases", action='store_true',
    #                     help="Update diseases already in DB")
    #
    # args = parser.parse_args()
    #
    # extractor = KnowledgeExtractor()
    #
    # try:
    #     extractor.setup()
    #     if args.harvest_go:
    #         extractor.update_obo(args.harvest_go, "GO")
    #     if args.harvest_do:
    #         extractor.update_obo(args.harvest_do, "DO")
    #     if args.harvest_mesh:
    #         extractor.update_obo(args.harvest_mesh, "MESH")
    #     if args.harvest_drugbank:
    #         extractor.update_drugbank(args.harvest_drugbank)
    #     if args.add_disease:
    #         extractor.add_disease(args.add_disease)
    #     if args.update_diseases:
    #         extractor.update_diseases()
    # finally:
    #     extractor.cleanup()