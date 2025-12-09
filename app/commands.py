import click
from flask.cli import with_appcontext
from datetime import datetime
from app.extensions import db, bcrypt
from app.models.user import User
from app.models.role import Role
from app.models.registration_sequence import RegistrationSequence
from app.models.program import Program
from app.services.username_generator import UsernameGenerator

@click.command("init-db")
@with_appcontext
def init_db_command():
    """Initialize the database."""
    db.create_all()
    click.echo("✅ Database tables created successfully!")


@click.command("create-admin")
@with_appcontext
@click.option('--username', default=None, help='Admin username (optional, auto-generated if not provided)')
@click.option('--email', default='admin@yca-abuja.com', help='Admin email')
@click.option('--password', default='Admin@123', help='Admin password')
def create_admin(username, email, password):
    """Create a system admin user."""
    
    # Ensure System Admin role exists
    admin_role = Role.query.filter_by(name="System Admin").first()
    if not admin_role:
        admin_role = Role(
            name="System Admin",
            description="Full system access and management"
        )
        db.session.add(admin_role)
        db.session.commit()
        click.echo("⚠️  Created System Admin role (roles not seeded)")
    
    # Check if user exists by email
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        click.echo(f"❌ User with email '{email}' already exists.")
        return
    
    # Generate username if not provided
    if not username:
        current_year = datetime.now().year % 100
        username = UsernameGenerator.generate_username(
            year=current_year,
            role_name='System Admin'
        )
        click.echo(f"📝 Auto-generated username: {username}")
    
    # Check if username exists
    existing_username = User.query.filter_by(username=username).first()
    if existing_username:
        click.echo(f"❌ Username '{username}' already exists.")
        return
    
    # Create user
    user = User(
        username=username,
        email=email,
        surname="Admin",
        first_name="System",
        middle_name="Administrator",
        gender="Male",
        password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
        is_active=True,
        email_verified=True,
        country="Nigeria",
        address="Flat 2A, House 83B, El-Habitat Close, Dogongada, Abuja City",
        phone="+2349079869903"
    )
    
    # Assign role
    user.roles.append(admin_role)
    
    db.session.add(user)
    db.session.commit()
    
    click.echo("✅ System admin created successfully!")
    click.echo(f"   📧 Email: {email}")
    click.echo(f"   👤 Username: {username}")
    click.echo(f"   🔑 Password: {password}")
    click.echo("\n⚠️  IMPORTANT: Change the password immediately after first login!")


@click.command("seed-db")
@with_appcontext
def seed_db():
    """Seed the database with initial data."""
    # Seed roles
    from seeders.roles_seeder import seed_roles
    seed_roles()
    click.echo("✅ Seeded roles")
    
    # Seed programs
    from seeders.programs_seeder import seed_programs
    seed_programs()
    click.echo("✅ Seeded programs")
    
    # Create default admin if doesn't exist
    admin_email = 'admin@yca-abuja.com'
    admin_exists = User.query.filter_by(email=admin_email).first()
    
    if not admin_exists:
        current_year = datetime.now().year % 100
        username = UsernameGenerator.generate_username(
            year=current_year,
            role_name='System Admin'
        )
        
        admin_role = Role.query.filter_by(name="System Admin").first()
        admin = User(
            username=username,
            email=admin_email,
            surname="Admin",
            first_name="System",
            gender="Male",
            password_hash=bcrypt.generate_password_hash('Admin@123').decode('utf-8'),
            is_active=True,
            email_verified=True,
            country="Nigeria"
        )
        admin.roles.append(admin_role)
        
        db.session.add(admin)
        db.session.commit()
        click.echo(f"✅ Created default admin user: {admin_email} / Admin@123")
    
    click.echo("🎉 Database seeded successfully!")


@click.command("test-username")
@with_appcontext
def test_username():
    """Test username generator."""
    click.echo("🧪 Testing username generator...")
    
    # Test various username generations
    tests = [
        ('System Admin', None),
        ('Student', 'Web Development'),
        ('Teacher', 'Python Programming'),
        ('Student', 'Data Analytics'),
        ('Head of School', None),
    ]
    
    for role_name, program_name in tests:
        try:
            username = UsernameGenerator.generate_username(
                year=24,
                role_name=role_name,
                program_name=program_name
            )
            click.echo(f"   ✅ {role_name} ({program_name or 'N/A'}): {username}")
        except Exception as e:
            click.echo(f"   ❌ {role_name}: {str(e)}")
    
    # Test batch generation
    try:
        usernames = UsernameGenerator.batch_generate_usernames(
            count=3,
            role_name='Student',
            program_name='Cybersecurity Fundamentals',
            cohort='B'
        )
        click.echo(f"\n   🔄 Batch generation (3 students):")
        for uname in usernames:
            click.echo(f"      - {uname}")
    except Exception as e:
        click.echo(f"   ❌ Batch generation failed: {str(e)}")
    
    click.echo("\n✅ Username generator test complete!")


@click.command("list-programs")
@with_appcontext
def list_programs():
    """List all programs in the database."""
    programs = Program.query.order_by(Program.category, Program.name).all()
    
    if not programs:
        click.echo("❌ No programs found. Run 'flask seed-db' first.")
        return
    
    current_category = None
    for program in programs:
        if program.category != current_category:
            current_category = program.category
            click.echo(f"\n📚 {current_category}")
            click.echo("-" * 40)
        
        price_display = "Sponsored" if program.is_sponsored else f"₦{program.price_ngn:,.2f}"
        click.echo(f"  • {program.code}: {program.name}")
        click.echo(f"    Duration: {program.display_duration}")
        click.echo(f"    Price: {price_display}")
        click.echo(f"    Status: {'Active' if program.is_active else 'Inactive'}")
    
    click.echo(f"\n📊 Total: {len(programs)} programs")


@click.command("list-roles")
@with_appcontext
def list_roles():
    """List all roles in the database."""
    roles = Role.query.order_by(Role.name).all()
    
    if not roles:
        click.echo("❌ No roles found. Run 'flask seed-db' first.")
        return
    
    click.echo("👥 System Roles:")
    click.echo("-" * 40)
    
    for role in roles:
        user_count = len(role.users)
        status = "Active" if role.is_active else "Inactive"
        click.echo(f"  • {role.name}")
        click.echo(f"    Description: {role.description or 'No description'}")
        click.echo(f"    Users: {user_count}")
        click.echo(f"    Status: {status}")
        click.echo()
    
    click.echo(f"📊 Total: {len(roles)} roles")