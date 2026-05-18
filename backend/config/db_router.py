"""Route les lectures vers une réplique PostgreSQL si configurée."""


class ReadReplicaRouter:
    read_app_labels = {'accounts', 'education', 'soils', 'sig_platform'}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.read_app_labels:
            return 'replica'
        return None

    def db_for_write(self, model, **hints):
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == 'default'
