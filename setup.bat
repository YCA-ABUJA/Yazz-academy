@echo off
echo Setting up Yazz Academy LMS...

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install requirements
echo Installing requirements...
pip install --upgrade pip
pip install -r requirements.txt

REM Create directories
echo Creating directories...
mkdir app 2>nul
mkdir app\models 2>nul
mkdir app\services 2>nul
mkdir app\auth 2>nul
mkdir app\admin 2>nul
mkdir app\teacher 2>nul
mkdir app\student 2>nul
mkdir app\marketing 2>nul
mkdir app\templates 2>nul
mkdir app\templates\auth 2>nul
mkdir app\templates\admin 2>nul
mkdir app\templates\teacher 2>nul
mkdir app\templates\student 2>nul
mkdir app\templates\marketing 2>nul
mkdir app\static 2>nul
mkdir app\static\css 2>nul
mkdir app\static\js 2>nul
mkdir app\static\images 2>nul
mkdir tests 2>nul
mkdir seeders 2>nul
mkdir scripts 2>nul
mkdir uploads 2>nul
mkdir uploads\photos 2>nul
mkdir uploads\resumes 2>nul
mkdir uploads\course_materials 2>nul

REM Create __init__.py files
echo Creating package files...
echo # Package > app\__init__.py
echo # Package > app\models\__init__.py
echo # Package > app\services\__init__.py
echo # Package > app\auth\__init__.py
echo # Package > app\admin\__init__.py
echo # Package > app\teacher\__init__.py
echo # Package > app\student\__init__.py
echo # Package > app\marketing\__init__.py
echo # Package > tests\__init__.py
echo # Package > seeders\__init__.py
echo # Package > scripts\__init__.py

REM Create minimal .env file
echo Creating environment file...
echo SECRET_KEY=dev-secret-key-change-in-production > .env
echo DATABASE_URL=mysql://root:@localhost:3306/yazz_academy >> .env
echo FLASK_APP=run.py >> .env

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Make sure MySQL is running in XAMPP/Laragon
echo 2. Create database: CREATE DATABASE yazz_academy;
echo 3. Run: python init_db.py
echo 4. Start server: python run.py