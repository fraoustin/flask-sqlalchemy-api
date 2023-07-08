import os
import logging
from flask import Flask, request, json, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy_api import ApiRest, error_api
# ------------------------ Manage login ----------------------------
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask import abort
from werkzeug.security import generate_password_hash, check_password_hash
import base64

app = Flask(__name__)

# db SQLAlchemy
database_file = "sqlite:///{}".format(os.path.join('.', "test.db"))
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy()

# ------------------------ Manage login ----------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.secret_key = 'my_secret_key'


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    apikey = db.Column(db.String, nullable=True)
    token = db.Column(db.String, nullable=True)

    def __setattr__(self, name, value):
        if name == 'password':
            value = generate_password_hash(value)
        db.Model.__setattr__(self, name, value)

    def __getattribute__(self, name):
        if name not in ('id') and db.Model.__getattribute__(self, name) is None:
            return ""
        return db.Model.__getattribute__(self, name)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the id to satisfy Flask-Login's requirements."""
        return self.id

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def is_authenticated(self):
        return True

    def check_password(self, password):
        return check_password_hash(self.password, password)


@login_manager.unauthorized_handler
def unauthorized():
    return {'authenticated': False}, 401


@login_manager.user_loader
def user_loader(id):
    return User.query.get(id)


@login_manager.request_loader
def load_user_from_request(request):
    # first, try to login using the api_key url arg
    apikey = request.args.get('api')
    if apikey:
        user = User.query.filter_by(apikey=apikey).first()
        if user is not None:
            return user

    # next, try to login using Basic Auth
    token = request.headers.get('Authorization')
    if token:
        token = token.replace('Basic ', '', 1)
        try:
            token = base64.b64decode(token)
        except Exception:
            pass
        user = User.query.filter_by(token=token).first()
        if user is not None:
            return user

    # finally, return None if both methods did not login the user
    return None


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    registered_user = User(username)
    if registered_user.check_password(password):
        login_user(registered_user, remember=True)
        return {'authenticated': True}, 200
    return {'authenticated': False}, 401


@app.route('/logout')
def logout():
    logout_user()
    return {}, 200

# ------------------------ End Manage login ----------------------------


class Todo(db.Model):
    __tablename__ = 'todo'

    __table_args__ = (
        db.Index(
            'ix_unique_index',  # Index name
            'title', 'description',  # Columns which are part of the index
            unique=True),  # The condition
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    status = db.Column(db.String, nullable=True)


apiManager = ApiRest(db)
for cls in [Todo, User]:
    for method in ['ALL', 'POST', 'GET', 'DELETE', 'PUT', 'PATCH']:
        apiManager.add_api(cls, method, decorators=[login_required])
app.register_blueprint(apiManager)


if __name__ == "__main__":
    db.init_app(app)
    with app.app_context():
        db.create_all()
        if len(User.query.all()) == 0:
            u = User(name="admin", password="admin", apikey="apikeyadmin", token="tokenadmin")
            db.session.add(u)
            db.session.commit()
    app.logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=5000, debug=True)
