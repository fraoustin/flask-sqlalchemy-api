import unittest
from flask import Flask, request, json

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy_api import ApiRest, error_api


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
            id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="not visible by api")
            title = db.Column(db.String, nullable=False, comment="not update by api")
            description = db.Column(db.String, nullable=True)
            status = db.Column(db.String, nullable=True, comment="not create by api")

        apiManager = ApiRest(db)
        for method in ['ALL', 'POST', 'GET', 'DELETE', 'PUT', 'PATCH']:
            apiManager.add_api(Todo, method)
        self.app.register_blueprint(apiManager)

        db.init_app(self.app)
        with self.app.app_context():
            db.create_all()

    def test_post(self):
        with self.app.test_client() as c:
            todo = {'title': 'test', 'description': 'test description', 'status': 'test'}
            rv = c.post('/api/v1/todo', data=todo)
            self.assertEqual(rv.status_code, 201)
            result = json.loads(rv.data)
            self.assertTrue(id not in result.keys())
            self.assertEqual(result["status"], None)

    def test_put_items(self):
        with self.app.test_client() as c:
            todo = {'title': 'test1', 'description': 'test description1', 'status': 'test'}
            rv = c.post('/api/v1/todo', data=todo)
            todo['title'] = 'test1 change'
            todo['description'] = 'test description1 change'
            todo['status'] = 'test change'
            rv = c.put('/api/v1/todo/1', data=todo)
            rv = c.get('/api/v1/todo/1')
            result = json.loads(rv.data)
            self.assertEqual(result['title'], 'test1')
            self.assertEqual(result['description'], 'test description1 change')


if __name__ == '__main__':
    unittest.main()
