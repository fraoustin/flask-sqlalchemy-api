from flask import Blueprint, request, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint, Integer, Float
from sqlalchemy.sql import text
from sqlalchemy.orm.exc import UnmappedInstanceError
from functools import wraps
import logging

__version__ = '0.9.1'

SQLTYPE_TO_FLASKTYPE = {Integer: 'int', Float: 'float'}


def model_to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def unique_endpoint(cls):
    constraint = None
    if len([constraint for constraint in cls.__table__.constraints if isinstance(constraint, UniqueConstraint)]) > 0:
        constraint = [constraint for constraint in cls.__table__.constraints if isinstance(constraint, UniqueConstraint)][0]
    if len([constraint for constraint in cls.__table__.constraints if isinstance(constraint, PrimaryKeyConstraint)]) > 0:
        constraint = [constraint for constraint in cls.__table__.constraints if isinstance(constraint, PrimaryKeyConstraint)][0]
    if constraint is None:
        raise "%s does not PrimaryKeyConstraint or UniqueConstraint" % cls.__name__
    return ("/".join(["<%s:%s>" % (SQLTYPE_TO_FLASKTYPE.get(column.type.__class__, 'string'), column.name) for column in constraint.columns]))


class ItemNotFound(Exception):

    def __init__(self, item):
        super().__init__("Item not found %s" % item)


def error_api(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except UnmappedInstanceError as err:
            return {"code": 400, 'description': 'Item not found, %s' % str(err)}, 400
        except Exception as err:
            return {"code": 400, 'description': str(err)}, 400
    return decorated_view


def multi_decorators(decorators):
    def decorator(f):
        for d in reversed(decorators):
            f = d(f)
        return f
    return decorator


class ApiRest(Blueprint):

    def __init__(self, db, name='apirest', import_name=__name__, url_prefix='/api/v1', *args, **kwargs):
        Blueprint.__init__(self, name, import_name, url_prefix, *args, **kwargs)
        self._db = db
        self._url_prefix = url_prefix

    def add_api(self, cls, method, decorators=[], endpoint=None, serialize=model_to_dict):
        decorators = [error_api,] + decorators
        if method not in ['ALL', 'POST', 'GET', 'DELETE', 'PUT', 'PATCH']:
            raise "%s is not a method value (ALL, POST, GET, DELETE, PUT, PATCH)" % method
        if method == 'ALL':
            method = 'GET'
            if endpoint is None:
                endpoint = '%s/%ss' % (self._url_prefix, cls.__name__.lower())
            self.add_url_rule(endpoint, 'view_%ss' % endpoint[1:], multi_decorators(decorators)(self._all(cls, serialize)), methods=[method, ])
        elif method == 'POST':
            if endpoint is None:
                endpoint = '%s/%s' % (self._url_prefix, cls.__name__.lower())
            self.add_url_rule(endpoint, 'post_%s' % endpoint[1:], multi_decorators(decorators)(self._post(cls, serialize)), methods=[method, ])
        elif method == 'GET':
            if endpoint is None:
                endpoint = '%s/%s/%s' % (self._url_prefix, cls.__name__.lower(), unique_endpoint(cls))
            self.add_url_rule(endpoint, 'get_%s' % endpoint[1:], multi_decorators(decorators)(self._get(cls, serialize)), methods=[method, ])
        elif method == 'DELETE':
            if endpoint is None:
                endpoint = '%s/%s/%s' % (self._url_prefix, cls.__name__.lower(), unique_endpoint(cls))
            self.add_url_rule(endpoint, 'del_%s' % endpoint[1:], multi_decorators(decorators)(self._del(cls, serialize)), methods=[method, ])
        elif method == 'PUT':
            if endpoint is None:
                endpoint = '%s/%s/%s' % (self._url_prefix, cls.__name__.lower(), unique_endpoint(cls))
            self.add_url_rule(endpoint, 'put_%s' % endpoint[1:], multi_decorators(decorators)(self._put(cls, serialize)), methods=[method, ])
        elif method == 'PATCH':
            if endpoint is None:
                endpoint = '%s/%s/%s' % (self._url_prefix, cls.__name__.lower(), unique_endpoint(cls))
            self.add_url_rule(endpoint, 'patch_%s' % endpoint[1:], multi_decorators(decorators)(self._patch(cls, serialize)), methods=[method, ])
        logging.getLogger("werkzeug").info(" * add url rule %s for %s" % (endpoint, method))

    def _all(self, cls, serialize):
        def fct():
            offset = request.args.get('offset', 0)
            limit = request.args.get('limit', 999)
            order_by = request.args.get('orderby', '')
            filter = request.args.get('filter', '')
            return [serialize(item) for item in cls.query.filter(text(filter)).order_by(text(order_by)).offset(offset).limit(limit).all()], 200
        return fct

    def _post(self, cls, serialize):
        def fct(**kws):
            dct = {key: request.form.get(key) for key in request.form}
            for col in [c.name for c in cls.__table__.columns if c.autoincrement is True]:
                if col in dct:
                    del dct[col]
            item = cls(**dct)
            self._db.session.add(item)
            self._db.session.commit()
            return serialize(item), 201
        return fct

    def _get(self, cls, serialize):
        def fct(**kws):
            item = self._db.one_or_404(self._db.select(cls).filter_by(**kws), description=f"{cls.__name__} with parameters {','.join(['%s:%s' % (kw, kws[kw]) for kw in kws])}.")
            return serialize(item), 200
        return fct

    def _del(self, cls, serialize):
        def fct(**kws):
            item = self._db.one_or_404(self._db.select(cls).filter_by(**kws), description=f"{cls.__name__} with parameters {','.join(['%s:%s' % (kw, kws[kw]) for kw in kws])}.")
            self._db.session.delete(item)
            self._db.session.commit()
            return {"code": 200, "message": "element remove with success", "instance": request.path}, 200
        return fct

    def _put(self, cls, serialize):
        def fct(**kws):
            item = self._db.one_or_404(self._db.select(cls).filter_by(**kws), description=f"{cls.__name__} with parameters {','.join(['%s:%s' % (kw, kws[kw]) for kw in kws])}.")
            dct = {key: request.form.get(key) for key in request.form}
            for key in kws:
                dct[key] = kws[key]
            for col in [c.name for c in item.__table__.columns]:
                item.__setattr__(col, dct.get(col))
            self._db.session.commit()
            return serialize(item), 200
        return fct

    def _patch(self, cls, serialize):
        def fct(**kws):
            item = self._db.one_or_404(self._db.select(cls).filter_by(**kws), description=f"{cls.__name__} with parameters {','.join(['%s:%s' % (kw, kws[kw]) for kw in kws])}.")
            dct = {key: request.form.get(key) for key in request.form}
            for key in kws:
                dct[key] = kws[key]
            for col in [key for key in dct if key in item.__table__.columns]:
                item.__setattr__(col, dct.get(col))
            self._db.session.commit()
            return serialize(item), 200
        return fct

    def register(self, app, options):
        try:
            Blueprint.register(self, app, options)
        except Exception:
            app.logger.error("init ApiRest on register is failed")
