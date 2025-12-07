from flask import Flask
from config import config
from flask_migrate import Migrate

from app.extensions import init_extensions, db

def create_app(config_name: str='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    init_extensions(app)

    # Initialize migrations
    migrate = Migrate(app, db)

    # Import models so Alembic can detect them
    from app.models import User, Role, user_roles

    # Register CLI commands
    from app.commands import init_db_command, create_admin, seed_db
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin)
    app.cli.add_command(seed_db)
    return app