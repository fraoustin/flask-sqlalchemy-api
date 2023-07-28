# flask-sqlachemy-api

generate API Rest from Model Class


## Installation


    pip install flask-sqlachemy-api
        
Or

    git clone https://github.com/fraoustin/flask-sqlachemy-api.git
    cd flask-sqlachemy-api
    python setup.py install

You can load test by

    flake8 --ignore E501,E226,E128,F401
    python -m unittest discover -s tests


## Usage

    import os, logging
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from flask_sqlalchemy_api import ApiRest, error_api

    app = Flask(__name__)

    # db SQLAlchemy
    database_file = "sqlite:///{}".format(os.path.join('.', "test.db"))
    app.config["SQLALCHEMY_DATABASE_URI"] = database_file
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
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
    app.register_blueprint(apiManager)


    if __name__ == "__main__":
        db.init_app(app)
        with app.app_context():
            db.create_all()
        app.logger.setLevel(logging.DEBUG)
        app.run(host='0.0.0.0', port=5000, debug=True)

This code generate api url:

- GET http://127.0.0.1:5000/api/v1/todos
- POST http://127.0.0.1:5000/api/v1/todo
- GET http://127.0.0.1:5000/api/v1/todo/<id>
- DELETE http://127.0.0.1:5000/api/v1/todo/<id>
- PUT http://127.0.0.1:5000/api/v1/todo/<id>
- PATCH http://127.0.0.1:5000/api/v1/todo/<id>


flask-sqlachemy-api generate 6 Apis from Model Class

- ALL: it's a get request for list of item with url http://domain/api_path/items. You can add parameter filter, orderby, offset, limit.

    http://127.0.0.1:5000/api/v1/todos?orderby=title%20desc  method GET

    http://127.0.0.1:5000/api/v1/todos?orderby=title%20desc&filter=id%3D  method GET

    http://127.0.0.1:5000/api/v1/todos?offset=50&limit=50  method GET

- GET: it's get request for  a specific item with url http://domain/api_path/item/<id>

    http://127.0.0.1:5000/api/v1/todo/1 method GET

- DELETE: it's delete request for a specific item url http://domain/api_path/item/<id>

    http://127.0.0.1:5000/api/v1/todo/1  method DELETE

- POST: it's post request for add a item with url http://domain/api_path/item. You add data on your request

    http://127.0.0.1:5000/api/v1/todo  method POST

- PUT: it's put request for modify a specific item with url http://domain/api_path/item/<id>. You add data on your request

    http://127.0.0.1:5000/api/v1/todo/1  method PUT

- PATCH: it's patch request for modify a specific item on specific column with url http://domain/api_path/item/<id>. You add data on your request

    http://127.0.0.1:5000/api/v1/todo/1  method PATCH

You can 

- specific url (default /api/v1) on ApiRest
- add decorator (login, ...) in sample/sample1.py
- specific endpoint
- specific serialize: transform item to json

## Sample

You can launch sample 0 and 1

    python sample/sample0.py &
    python sample/sample0_test.py

You can launch sample3

    python sample/sample3.py

And you test API by swagger UI on http://127.0.0.1:5000/swagger

## TODO

- voir pour faire des apis lié au fk ex /api/person/(int: id)/computers (https://flask-restless.readthedocs.io/en/stable/requestformat.html)
- faire exemple flask-sqlalchemy-api + dbml-to-sqlalchemy
- faire full application todo avec gestion user