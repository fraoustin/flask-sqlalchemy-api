import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy_api import ApiRest, error_api, Swagger
from static import Static

app = Flask(__name__)

# db SQLAlchemy
database_file = "sqlite:///{}".format(os.path.join('.', "test.db"))
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy()


class Todo(db.Model):
    __tablename__ = 'todo'

    __table_args__ = (
        db.Index(
            'ix_unique_index',  # Index name
            'title', 'description',  # Columns which are part of the index
            unique=True),  # The condition
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False, comment="title of Todo, not visible by api, not update by api, not create by api")
    description = db.Column(db.String, nullable=True)
    status = db.Column(db.String, nullable=True)


apiManager = ApiRest(db)
swagger = Swagger()
swagger.title = "Test Interface Swagger"
swagger.description = "Just a test"
for method in ['ALL', 'POST', 'GET', 'DELETE', 'PUT', 'PATCH']:
    endpoint = apiManager.add_api(Todo, method)
    swagger.addEndPoint(endpoint)
app.register_blueprint(apiManager)

app.register_blueprint(Static(name="swagger", url_prefix="/swagger/", path=os.path.join('./sample', "swagger")))


@app.route('/swagger.json')
def swaggerjson():
    return swagger


if __name__ == "__main__":
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=5000, debug=True)
