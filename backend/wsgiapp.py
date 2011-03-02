"""
WSGI/PasteDeploy application bootstrap module.
"""

from restish.app import RestishApp

from backend.resource import root
#from repoze.who.config import make_middleware_with_config
from beaker.middleware import SessionMiddleware


def make_app(global_conf, **app_conf):
    """
    PasteDeploy WSGI application factory.

    Called by PasteDeploy (or a compatable WSGI application host) to create the
    backend WSGI application.
    """
    app = RestishApp(root.Root())
    #app = make_middleware_with_config(app, global_conf, 'who.ini')
    session_opts = {
        'session.type': 'memory',
        'session.cookie_expires' : True,
    }
    app = SessionMiddleware(app, session_opts)
    app = setup_environ(app, global_conf, app_conf)
    return app


def setup_environ(app, global_conf, app_conf):
    """
    WSGI application wrapper factory for extending the WSGI environ with
    application-specific keys.
    """

    # Create any objects that should exist for the lifetime of the application
    # here. Don't forget to actually include them in the environ below!
    from backend.lib.templating import make_templating
    templating = make_templating(app_conf)

    def application(environ, start_response):

        # Add additional keys to the environ here.
        environ['restish.templating'] = templating

        return app(environ, start_response)

    return application

