import pytest
from datetime import datetime
from app.services.username_generator import UsernameGenerator
from app.models.registration_sequence import RegistrationSequence
from app.extensions import db
from app import create_app

@pytest.fixture
def app():
    """Create test application"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

class TestUsernameGenerator:
    
    def test_generate_student_username(self, app):
        """Test generating username for student"""
        with app.app_context():
            username = UsernameGenerator.generate_username(
                year=24,
                role_name='Student',
                program_name='Web Development'
            )
            
            assert username.startswith('YCA/24/')
            assert '/STD/' in username
            assert username.endswith('0001')  # First in sequence
    
    def test_generate_teacher_username(self, app):
        """Test generating username for teacher"""
        with app.app_context():
            username = UsernameGenerator.generate_username(
                year=24,
                role_name='Teacher',
                program_name='Python Programming'
            )
            
            assert username.startswith('YCA/24/PYT/TCH/')
    
    def test_generate_admin_username(self, app):
        """Test generating username for system admin"""
        with app.app_context():
            username = UsernameGenerator.generate_username(
                year=24,
                role_name='System Admin'
            )
            
            assert username.startswith('YCA/24/SYS/SYS/')
    
    def test_invalid_role(self, app):
        """Test error for invalid role"""
        with app.app_context():
            with pytest.raises(ValueError, match="Invalid role name"):
                UsernameGenerator.generate_username(
                    role_name='InvalidRole',
                    program_name='Web Development'
                )
    
    def test_concurrent_username_generation(self, app):
        """Test that username generation is thread-safe"""
        with app.app_context():
            import concurrent.futures
            
            def generate_username_thread():
                with app.app_context():
                    return UsernameGenerator.generate_username(
                        year=24,
                        role_name='Student',
                        program_name='Data Analytics',
                        cohort='B'
                    )
            
            # Generate usernames concurrently
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(generate_username_thread) for _ in range(10)]
                usernames = [f.result() for f in futures]
            
            # All usernames should be unique
            assert len(usernames) == len(set(usernames))
            
            # Should be sequential
            sequences = [int(u.split('/')[-1]) for u in usernames]
            assert sorted(sequences) == list(range(1, 11))
    
    def test_batch_generation(self, app):
        """Test batch generation of usernames"""
        with app.app_context():
            usernames = UsernameGenerator.batch_generate_usernames(
                count=5,
                role_name='Student',
                program_name='Cybersecurity Fundamentals'
            )
            
            assert len(usernames) == 5
            assert all(u.startswith('YCA/') for u in usernames)
            assert all('/STD/' in u for u in usernames)
    
    def test_parse_username(self, app):
        """Test parsing username into components"""
        with app.app_context():
            username = "YCA/24/WD/STD/0001"
            parsed = UsernameGenerator.parse_username(username)
            
            assert parsed['year'] == 24
            assert parsed['program_code'] == 'WD'
            assert parsed['role_code'] == 'STD'
            assert parsed['sequence'] == 1
            assert parsed['role_name'] == 'Student'
    
    def test_invalid_username_parsing(self, app):
        """Test error for invalid username format"""
        with app.app_context():
            with pytest.raises(ValueError):
                UsernameGenerator.parse_username("Invalid/Format")
            
            with pytest.raises(ValueError):
                UsernameGenerator.parse_username("YCA/24/WD/STD/not-a-number")
    
    def test_program_code_generation(self, app):
        """Test program code generation for unknown programs"""
        with app.app_context():
            username = UsernameGenerator.generate_username(
                year=24,
                role_name='Student',
                program_name='New Experimental Course'
            )
            
            # Should generate code from program name
            assert '/NEC/STD/' in username or '/NEW/STD/' in username
    
    def test_year_auto_detection(self, app):
        """Test auto-detection of current year"""
        with app.app_context():
            current_year = datetime.now().year % 100
            username = UsernameGenerator.generate_username(
                role_name='Student',
                program_name='Web Development'
            )
            
            assert f"YCA/{current_year}/" in username