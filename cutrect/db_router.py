class DBRouter(object):
    """
    A router to control all database operations on models in the
    auth application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to auth_db.
        """
        if model._meta.app_label == 'jwt_auth':
            return 'users'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Attempts to write jwt_auth models go to users.
        """
        if model._meta.app_label == 'jwt_auth':
            return 'users'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the jwt_auth app is involved.
        """
        if obj1._meta.app_label == 'jwt_auth' or \
           obj2._meta.app_label == 'jwt_auth':
           return True
        return None

    def allow_migrate(self, db, app_label, model=None, **hints):
        """
        Make sure the jwt_auth app only appears in the 'users'
        database.
        """
        if app_label == 'jwt_auth':
            return db == 'users'
        return None
