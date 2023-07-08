import unittest
from flask import Flask, request, json
from functools import wraps

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy_api import ApiRest, error_api


def myserialiser(obj):
    serialize = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
    serialize["test"] = "test"
    return serialize


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
            id = db.Column(db.Integer, primary_key=True, autoincrement=True)
            title = db.Column(db.String, nullable=False)
            description = db.Column(db.String, nullable=True)
            status = db.Column(db.String, nullable=True)

        apiManager = ApiRest(db)
        for method in ['ALL', 'POST', 'GET', 'DELETE', 'PUT', 'PATCH']:
            apiManager.add_api(Todo, method, serialize=myserialiser)
        self.app.register_blueprint(apiManager)

        db.init_app(self.app)
        with self.app.app_context():
            db.create_all()

    def test_classic(self):
        with self.app.test_client() as c:
            todo = {'title': 'test1', 'description': 'test description1', 'status': 'test'}
            check = {'title': 'test1', 'description': 'test description1', 'status': 'test', 'id': 1, 'test': 'test'}
            rv = c.post('/api/v1/todo', data=todo)
            self.assertEqual(rv.status_code, 201)
            self.assertEqual(json.loads(rv.data), check)
            todo['title'] = "change test1"
            rv = c.put('/api/v1/todo/1', data=todo)
            self.assertEqual(rv.status_code, 200)
            self.assertNotEqual(json.loads(rv.data), check)
            check['title'] = todo['title']
            self.assertEqual(json.loads(rv.data), check)
            check['title'] = 'other title'
            rv = c.patch('/api/v1/todo/1', data={'title': check['title']})
            self.assertEqual(rv.status_code, 200)
            self.assertNotEqual(json.loads(rv.data), todo)
            self.assertEqual(json.loads(rv.data), check)
            rv = c.get('/api/v1/todos')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(len(json.loads(rv.data)), 1)
            rv = c.delete('/api/v1/todo/1')
            rv = c.get('/api/v1/todos')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(json.loads(rv.data), [])
            rv = c.get('/api/v1/todo/999')
            self.assertEqual(rv.status_code, 400)
            rv = c.delete('/api/v1/todo/999')
            self.assertEqual(rv.status_code, 400)
            rv = c.put('/api/v1/todo/999', data=todo)
            self.assertEqual(rv.status_code, 400)
            rv = c.patch('/api/v1/todo/999', data={'title': check['title']})
            self.assertEqual(rv.status_code, 400)

    def test_get_serialize_effect(self):
        with self.app.test_client() as c:
            todo = {'title': 'test1', 'description': 'test description1', 'status': 'test'}
            rv = c.post('/api/v1/todo', data=todo)
            rv = c.get('/api/v1/todo/1')
            result = json.loads(rv.data)
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(result["test"], "test")


if __name__ == '__main__':
    unittest.main()
