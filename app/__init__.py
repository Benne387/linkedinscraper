from flask import Flask

def create_app():
    app = Flask(__name__)
    
    from flask_basicauth import BasicAuth
    import os

    # Basic Auth Configuration
    app.config['BASIC_AUTH_USERNAME'] = os.environ.get('BASIC_AUTH_USERNAME', 'admin')
    app.config['BASIC_AUTH_PASSWORD'] = os.environ.get('BASIC_AUTH_PASSWORD', 'admin')
    app.config['BASIC_AUTH_FORCE'] = True # Protect entire app

    basic_auth = BasicAuth(app)

    # Register Blueprints
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    return app
