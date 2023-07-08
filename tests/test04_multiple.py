import unittest
from flask import Flask, request, json

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy_api import ApiRest, error_api
from sqlalchemy import PrimaryKeyConstraint


class BasicTest(unittest.TestCase):
    """
        Class for Basic Unitaire Test for flask_sqlalchemy_api
    """
    def setUp(self):
        self.app = Flask(__name__)
        self.app.testing = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        db = SQLAlchemy()

        class Todo(db.Model):
            __tablename__ = 'todo'
            id = db.Column(db.Integer)
            idd = db.Column(db.Integer)
            title = db.Column(db.String, nullable=False)
            description = db.Column(db.String, nullable=True)
            status = db.Column(db.String, nullable=True)
            __table_args__ = (
                PrimaryKeyConstraint(id, idd),
                {},
            )

        apiManager = ApiRest(db)
        for method in ['ALL', 'POST', 'GET', 'DELETE', 'PUT', 'PATCH']:
            apiManager.add_api(Todo, method)
        self.app.register_blueprint(apiManager)

        db.init_app(self.app)
        with self.app.app_context():
            db.create_all()

    def test_get_null(self):
        with self.app.test_client() as c:
            rv = c.get('/api/v1/todos')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(json.loads(rv.data), [])

    def test_post(self):
        with self.app.test_client() as c:
            todo = {'id': 1, 'idd': 2, 'title': 'test', 'description': 'test description', 'status': 'test'}
            rv = c.post('/api/v1/todo', data=todo)
            self.assertEqual(rv.status_code, 201)
            result = json.loads(rv.data)
            for key in todo:
                self.assertEqual(result[key], todo[key])

    def test_get_item(self):
        with self.app.test_client() as c:
            todo = {'id': 1, 'idd': 2, 'title': 'test', 'description': 'test description', 'status': 'test'}
            rv = c.post('/api/v1/todo', data=todo)
            rv = c.get('/api/v1/todo/1/2')
            self.assertEqual(rv.status_code, 200)
            result = json.loads(rv.data)
            for key in todo:
                self.assertEqual(result[key], todo[key])
