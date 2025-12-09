from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO

# Database
db = SQLAlchemy()

# Authentication
login_manager = LoginManager()
bcrypt = Bcrypt()

# Migrations
migrate = Migrate()

# Email
mail = Mail()

# JWT for API
jwt = JWTManager()

# Rate Limiting with default limits
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # Explicitly set storage
)

# WebSockets
socketio = SocketIO(cors_allowed_origins="*")

# Initialize all extensions
def init_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    socketio.init_app(app)
    
    # Login manager configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.refresh_view = 'auth.login'
    
    return app
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from .models.user import User
        return User.query.get(int(user_id))
    
    return app