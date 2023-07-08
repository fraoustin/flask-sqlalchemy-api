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
            id = db.Column(db.Integer, primary_key=True, autoincrement=True)
            title = db.Column(db.String, nullable=False)
            description = db.Column(db.String, nullable=True)
            status = db.Column(db.String, nullable=True)

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
            todo = {'title': 'test', 'description': 'test description', 'status': 'test'}
            rv = c.post('/api/v1/todo', data=todo)
            self.assertEqual(rv.status_code, 201)
            result = json.loads(rv.data)
            for key in todo:
                self.assertEqual(result[key], todo[key])
            self.assertEqual(result["id"], 1)

    def test_post_force_increment(self):
        with self.app.test_client() as c:
            todo = {'title': 'test', 'description': 'test description', 'status': 'test', 'id': 2}
            rv = c.post('/api/v1/todo', data=todo)
            self.assertEqual(rv.status_code, 201)
            result = json.loads(rv.data)
            todo['id'] = 1
            self.assertEqual(result, todo)

    def test_get_item(self):
        with self.app.test_client() as c:
            todo = {'title': 'test', 'description': 'test description', 'status': 'test'}
            rv = c.post('/api/v1/todo', data=todo)
            rv = c.get('/api/v1/todo/1')
            self.assertEqual(rv.status_code, 200)
            result = json.loads(rv.data)
            self.assertEqual(result["id"], 1)
            result.pop("id")
            self.assertEqual(result, todo)

    def test_get_items(self):
        with self.app.test_client() as c:
            todoOne = {'title': 'test1', 'description': 'test description1', 'status': 'test'}
            todoTwo = {'title': 'test2', 'description': 'test description2', 'status': 'test'}
            rv = c.post('/api/v1/todo', data=todoOne)
            rv = c.post('/api/v1/todo', data=todoTwo)
            rv = c.get('/api/v1/todos')
            self.assertEqual(rv.status_code, 200)
            result = json.loads(rv.data)
            self.assertEqual(len(result), 2)
            todoOne["id"] = 1
            self.assertEqual(result[0], todoOne)
            todoTwo["id"] = 2
            self.assertEqual(result[1], todoTwo)

    def test_get_item_not_found(self):
        with self.app.test_client() as c:
            rv = c.get('/api/v1/todo/1')
            self.assertEqual(rv.status_code, 400)

    def test_del_items(self):
        with self.app.test_client() as c:
            todoOne = {'title': 'test1', 'description': 'test description1', 'status': 'test'}
            todoTwo = {'title': 'test2', 'description': 'test description2', 'status': 'test'}
            rv = c.post('/api/v1/todo', data=todoOne)
            rv = c.post('/api/v1/todo', data=todoTwo)
            rv = c.get('/api/v1/todos')
            self.assertEqual(rv.status_code, 200)
            result = json.loads(rv.data)
            self.assertEqual(len(result), 2)
            rv = c.delete('/api/v1/todo/1')
            self.assertEqual(rv.status_code, 200)
            rv = c.get('/api/v1/todos')
            result = json.loads(rv.data)
            self.assertEqual(len(result), 1)
            todoTwo["id"] = 2
            self.assertEqual(result[0], todoTwo)

    def test_delete_item_not_found(self):
        with self.app.test_client() as c:
            rv = c.delete('/api/v1/todo/1')
            self.assertEqual(rv.status_code, 400)

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
            todo["id"] = 1
            self.assertEqual(result, todo)

    def test_put_item_not_found(self):
        with self.app.test_client() as c:
            todo = {'title': 'test1', 'description': 'test description1', 'status': 'test'}
            rv = c.put('/api/v1/todo/1', data=todo)
            self.assertEqual(rv.status_code, 400)

    def test_put_items_force_id(self):
        with self.app.test_client() as c:
            todo = {'title': 'test1', 'description': 'test description1', 'status': 'test'}
            rv = c.post('/api/v1/todo', data=todo)
            self.assertEqual(rv.status_code, 201)
            todo['title'] = 'test1 change'
            todo['description'] = 'test description1 change'
            todo['status'] = 'test change'
            todo["id"] = 2
            rv = c.put('/api/v1/todo/1', data=todo)
            rv = c.get('/api/v1/todo/1')
            result = json.loads(rv.data)
            todo["id"] = 1
            self.assertEqual(result, todo)

    def test_patch_items(self):
        with self.app.test_client() as c:
            todo = {'title': 'test1', 'description': 'test description1', 'status': 'test'}
            rv = c.post('/api/v1/todo', data=todo)
            todo['title'] = 'test1 change'
            rv = c.patch('/api/v1/todo/1', data={'title': todo['title']})
            rv = c.get('/api/v1/todo/1')
            result = json.loads(rv.data)
            todo["id"] = 1
            self.assertEqual(result, todo)

    def test_patch_items_check_id(self):
        with self.app.test_client() as c:
            todo = {'title': 'test1', 'description': 'test description1', 'status': 'test'}
            rv = c.post('/api/v1/todo', data=todo)
            todo['title'] = 'test1 change'
            rv = c.patch('/api/v1/todo/1', data={'title': todo['title'], 'id': 2})
            rv = c.get('/api/v1/todo/1')
            result = json.loads(rv.data)
            todo["id"] = 1
            self.assertEqual(result, todo)

    def test_patch_item_not_found(self):
        with self.app.test_client() as c:
            todo = {'title': 'test1'}
            rv = c.patch('/api/v1/todo/1', data=todo)
            self.assertEqual(rv.status_code, 400)

    def test_get_offset_limit(self):
        with self.app.test_client() as c:
            todo = {'title': 'test', 'description': 'test description', 'status': 'test'}
            for i in range(0, 1000):
                rv = c.post('/api/v1/todo', data=todo)
            rv = c.get('/api/v1/todos')
            self.assertEqual(rv.status_code, 200)
            result = json.loads(rv.data)
            self.assertEqual(len(result), 999)
            self.assertEqual(result[0]['id'], 1)
            self.assertEqual(result[998]['id'], 999)
            rv = c.get('/api/v1/todos?offset=50&limit=50')
            self.assertEqual(rv.status_code, 200)
            result = json.loads(rv.data)
            self.assertEqual(len(result), 50)
            self.assertEqual(result[0]['id'], 51)
            self.assertEqual(result[49]['id'], 100)

    def test_get_order_by(self):
        with self.app.test_client() as c:
            todoOne = {'title': 'before', 'description': 'test description1', 'status': 'test'}
            todoTwo = {'title': 'after', 'description': 'test description2', 'status': 'test'}
            rv = c.post('/api/v1/todo', data=todoOne)
            rv = c.post('/api/v1/todo', data=todoTwo)
            rv = c.get('/api/v1/todos?orderby=id')
            self.assertEqual(rv.status_code, 200)
            result = json.loads(rv.data)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['id'], 1)
            self.assertEqual(result[1]['id'], 2)
            rv = c.get('/api/v1/todos?orderby=title')
            self.assertEqual(rv.status_code, 200)
            result = json.loads(rv.data)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['id'], 2)
            self.assertEqual(result[1]['id'], 1)
            rv = c.get('/api/v1/todos?orderby=title%20desc')
            self.assertEqual(rv.status_code, 200)
            result = json.loads(rv.data)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['id'], 1)
            self.assertEqual(result[1]['id'], 2)
            rv = c.post('/api/v1/todo', data=todoOne)
            rv = c.get('/api/v1/todos?orderby=title%20desc%2Cid%20desc')
            self.assertEqual(rv.status_code, 200)
            result = json.loads(rv.data)
            self.assertEqual(len(result), 3)
            self.assertEqual(result[0]['id'], 3)
            self.assertEqual(result[1]['id'], 1)
            self.assertEqual(result[2]['id'], 2)

    def test_get_filter_by(self):
        with self.app.test_client() as c:
            todoOne = {'title': 'before', 'description': 'test description1', 'status': 'test'}
            todoTwo = {'title': 'after', 'description': 'test description2', 'status': 'test'}
            todoThree = {'title': 'title', 'description': 'test description3', 'status': 'close'}
            rv = c.post('/api/v1/todo', data=todoOne)
            rv = c.post('/api/v1/todo', data=todoTwo)
            rv = c.post('/api/v1/todo', data=todoThree)
            rv = c.get('/api/v1/todos?filter=id%3D2')
            self.assertEqual(rv.status_code, 200)
            result = json.loads(rv.data)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['id'], 2)
            rv = c.get('/api/v1/todos?filter=id%3D2')
            self.assertEqual(rv.status_code, 200)
            result = json.loads(rv.data)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['id'], 2)
            rv = c.get('/api/v1/todos?filter=status%3D%27test%27%20and%20id%3C2')
            self.assertEqual(rv.status_code, 200)
            result = json.loads(rv.data)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['id'], 1)


if __name__ == '__main__':
    unittest.main()
