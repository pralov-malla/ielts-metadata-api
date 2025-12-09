

# Use current folder as project root
PROJECT_NAME=$(pwd)  # current folder

echo "📦 Creating project files inside: $PROJECT_NAME"

# Create subfolders
mkdir -p app

# Create Python package initializer
touch app/__init__.py

# Create Python files
touch app/main.py
touch app/vision_service.py
touch app/prompts.py

# Other project files
touch requirements.txt
touch .env
touch process_csv.py


echo " Project template created inside existing folder!"
