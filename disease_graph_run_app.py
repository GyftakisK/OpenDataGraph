from app import create_app, db
from app.models import User

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}


@app.cli.command("init_db")
def init_db():
    db.create_all()
    for admin_user in app.config['ADMINS']:
        user = User(username=admin_user[:admin_user.index("@")], email=admin_user, is_admin=True)
        user.set_password('admin')
        db.session.add(user)
    db.session.commit()