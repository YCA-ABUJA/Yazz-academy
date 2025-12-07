import click
from flask.cli import with_appcontext
from app.extensions import db
from app.models import User, Role


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Initialize the database."""
    db.create_all()
    click.echo("Database initialized.")


@click.command("create-admin")
@with_appcontext
@click.argument("username")
@click.argument("email")
@click.argument("password")
def create_admin(username, email, password):
    """Create a super admin user."""

    # Ensure System Admin role exists
    admin_role = Role.query.filter_by(name="System Admin").first()
    if not admin_role:
        admin_role = Role(name="System Admin")
        db.session.add(admin_role)
        db.session.commit()

    # Check if user exists
    existing = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()

    if existing:
        click.echo("User already exists.")
        return

    # Create user
    user = User(
        username=username,
        email=email,
        surname="Admin",
        first_name="Super",
        gender="Male",
        password=password
    )

    # Assign role
    user.roles.append(admin_role)

    db.session.add(user)
    db.session.commit()

    click.echo("✅ Super admin created successfully!")


@click.command("seed-db")
@with_appcontext
def seed_db():
    """Seed the database with initial data."""
    # Example: create default roles
    roles = ["System Admin", "Teacher", "Student"]

    for role_name in roles:
        if not Role.query.filter_by(name=role_name).first():
            db.session.add(Role(name=role_name))

    db.session.commit()
    click.echo("✅ Database seeded successfully!")