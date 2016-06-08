# coding: utf-8
from .admin import ModelView
from .admin.common import _admin_registry, _document_registry
from .contrib.common import Model, View


class CoolManager(object):

    def __init__(self):
        self.admin = dict()
        self.models = dict()

    def init_app(self, app):
        self.app = app
        app.cool_manager = self
        self.load()

    def load(self):
        self.loading = True
        for name, view in _admin_registry.iteritems():
            self.admin[name] = view
        for name, doc in _document_registry.iteritems():
            if not doc._meta['abstract'] and doc._is_document:
                self.models[name] = doc

        for name, model in self.models.iteritems():
            data_model = Model.objects(name=name).first()
            if not data_model:
                data_model = Model(name=name, desc=(model.__doc__ or name).replace('模型', ''))
                data_model.save()
            view = self.get_view(name, model)
            data_view = View.objects(name=view.__name__).first()
            if not data_view:
                data_view = View(name=view.__name__, type=View.TYPE_MODEL, model=data_model, label=data_model.desc)
                data_view.save()
            model._admin_view_cls = view
            model._admin_view_data = data_view

        self.loading = False

    def init_admin(self, admin):
        for name, model in self.models.iteritems():
            view = model._admin_view_cls(model)
            model._admin_view_data.setup(admin, view)
            admin.add_view(view)

    def get_view(self, name, model):
        view = self.admin.get('%sView' % name)
        if name == 'ModelView':
            view = self.admin.get('ModelAdminView')
        if not view:
            view = type('%sView' % name, (ModelView,), {})
        return view


cm = CoolManager()