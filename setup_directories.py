import os

# Define the directory structure
directories = [
    'app',
    'app/templates',
    'app/static',
    'app/static/css',
    'app/static/js',
    'app/static/images',
    'app/data'
]

# Create directories
for directory in directories:
    os.makedirs(os.path.join(os.getcwd(), directory), exist_ok=True)

print("Directory structure created successfully!")