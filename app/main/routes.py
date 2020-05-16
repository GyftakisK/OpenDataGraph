from app.main import bp
from flask import render_template


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('main/index.html')
