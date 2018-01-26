class DBRouter(object):
    """
    A router to control all database operations on models in the
    auth application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to auth_db.
        """
        if model._meta.app_label == 'sutra':
            return 'sutra_db'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Attempts to write sutra models go to sutra_db.
        """
        if model._meta.app_label == 'sutra':
            return 'sutra_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the sutra app is involved.
        """
        if obj1._meta.app_label == 'sutra' or \
           obj2._meta.app_label == 'sutra':
           return True
        return 'default'

    def allow_migrate(self, db, app_label, model=None, **hints):
        """
        Make sure the sutra app only appears in the 'sutra_db'
        database.
        """
        if app_label == 'sutra':
            return db == 'sutra_db'
        return 'default'