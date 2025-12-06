from app.extensions import db
from app.models.program import Program

def seed_programs():
    """Seed initial programs from the catalogue"""
    programs_data = [
        # Tech & Digital Skills
        {
            'code': 'PYT',
            'name': 'Python Programming',
            'category': 'Tech & Digital Skills',
            'duration_weeks': 13,
            'price_ngn': 95000.00,
            'description': 'Learn Python from basics to advanced concepts with hands-on projects.',
            'learning_outcomes': [
                'Master Python syntax and core concepts',
                'Build real-world applications',
                'Understand object-oriented programming',
                'Work with databases and APIs'
            ]
        },
        {
            'code': 'WD',
            'name': 'Web Development',
            'category': 'Tech & Digital Skills',
            'duration_weeks': 14,
            'price_ngn': 120000.00,
            'description': 'Full-stack web development with modern frameworks.',
            'learning_outcomes': [
                'Build responsive websites',
                'Master frontend and backend development',
                'Deploy web applications',
                'Work with databases'
            ]
        },
        {
            'code': 'CC',
            'name': 'Creative Coding',
            'category': 'Tech & Digital Skills',
            'duration_weeks': 6,
            'price_ngn': 80000.00,
            'description': 'Combine programming with creative arts and design.',
            'learning_outcomes': [
                'Create interactive art with code',
                'Understand generative algorithms',
                'Build creative projects'
            ]
        },
        {
            'code': 'CYF',
            'name': 'Cybersecurity Fundamentals',
            'category': 'Tech & Digital Skills',
            'duration_weeks': 4,
            'price_ngn': 60000.00,
            'description': 'Introduction to cybersecurity concepts and practices.',
            'learning_outcomes': [
                'Understand security threats',
                'Implement basic security measures',
                'Learn ethical hacking basics'
            ]
        },
        {
            'code': 'DA',
            'name': 'Data Analytics',
            'category': 'Tech & Digital Skills',
            'duration_weeks': 8,
            'price_ngn': 90000.00,
            'description': 'Learn to analyze and visualize data for insights.',
            'learning_outcomes': [
                'Master data analysis tools',
                'Create data visualizations',
                'Generate business insights',
                'Work with real datasets'
            ]
        },
        
        # Communication & Soft Skills
        {
            'code': 'PS',
            'name': 'Public Speaking',
            'category': 'Communication & Soft Skills',
            'duration_days': 5,
            'price_ngn': 65000.00,
            'description': 'Develop confident public speaking skills.',
            'learning_outcomes': [
                'Overcome public speaking anxiety',
                'Deliver compelling presentations',
                'Engage with audiences effectively'
            ]
        },
        {
            'code': 'SW',
            'name': 'Speech Writing',
            'category': 'Communication & Soft Skills',
            'duration_weeks': 3,
            'price_ngn': 45000.00,
            'description': 'Learn to craft effective speeches for various occasions.',
            'learning_outcomes': [
                'Write persuasive speeches',
                'Structure speech content',
                'Adapt writing for different audiences'
            ]
        },
        {
            'code': 'ST',
            'name': 'Storytelling',
            'category': 'Communication & Soft Skills',
            'duration_weeks': 2,
            'price_ngn': 40000.00,
            'description': 'Master the art of storytelling for impact.',
            'learning_outcomes': [
                'Craft compelling narratives',
                'Use storytelling techniques',
                'Engage listeners emotionally'
            ]
        },
        
        # Teacher Training
        {
            'code': 'SC3',
            'name': 'Scratch 3.0',
            'category': 'Teacher Training',
            'duration_weeks': 8,
            'price_ngn': 50000.00,
            'description': 'Learn to teach programming with Scratch.',
            'learning_outcomes': [
                'Master Scratch programming',
                'Create educational projects',
                'Teach programming concepts to beginners'
            ]
        },
        {
            'code': 'CV',
            'name': 'Canva',
            'category': 'Teacher Training',
            'duration_weeks': 1,
            'price_ngn': 25000.00,
            'description': 'Master Canva for educational content creation.',
            'learning_outcomes': [
                'Create engaging educational materials',
                'Design presentations and infographics',
                'Use Canva for classroom activities'
            ]
        },
        {
            'code': 'GC',
            'name': 'Google Classroom',
            'category': 'Teacher Training',
            'duration_weeks': 1,
            'price_ngn': 25000.00,
            'description': 'Learn to manage virtual classrooms effectively.',
            'learning_outcomes': [
                'Set up and manage Google Classroom',
                'Create assignments and assessments',
                'Engage students online'
            ]
        },
        
        # Seasonal & Special
        {
            'code': 'SC',
            'name': 'Summer Camp',
            'category': 'Seasonal & Special',
            'duration_weeks': 3,
            'price_ngn': 55000.00,
            'description': 'Summer coding camp for kids and teens.',
            'learning_outcomes': [
                'Learn programming basics',
                'Work on fun projects',
                'Develop problem-solving skills'
            ]
        },
        {
            'code': 'CED',
            'name': 'connectED',
            'category': 'Seasonal & Special',
            'is_sponsored': True,
            'price_ngn': 0.00,
            'description': 'Sponsored program for underserved communities.',
            'learning_outcomes': [
                'Digital literacy skills',
                'Basic programming concepts',
                'Career readiness'
            ]
        },
        {
            'code': 'CMS',
            'name': 'Cybersecurity Mythology Series',
            'category': 'Seasonal & Special',
            'description': 'Special series on cybersecurity through mythology (on request).',
            'learning_outcomes': [
                'Understand cybersecurity through stories',
                'Learn security concepts in engaging way',
                'Apply lessons to real scenarios'
            ]
        }
    ]
    
    for program_data in programs_data:
        program = Program.query.filter_by(code=program_data['code']).first()
        if not program:
            program = Program(**program_data)
            db.session.add(program)
    
    db.session.commit()
    print(f"✓ Seeded {len(programs_data)} programs")