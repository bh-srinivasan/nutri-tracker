<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Nutri Tracker Application Instructions

This is a Flask-based Protein and Nutrition Tracking web application with the following specifications:

## Technology Stack

- **Backend**: Flask 2.3.3, SQLite, SQLAlchemy, Werkzeug for security
- **Frontend**: Bootstrap 5.1.3, Font Awesome 6.0, Jinja2 templates
- **Authentication**: Flask-Login with role-based access control
- **Deployment**: Azure App Service with Gunicorn

## Architecture

- Modular Flask blueprints for authentication, admin, user dashboard, and API
- SQLAlchemy models for User, Food, MealLog, and NutritionGoal
- Role-based access control (Admin and Regular Users)
- Responsive Bootstrap UI with modern design

## Key Features

- Secure user authentication with password hashing
- Admin panel for user and food database management
- User dashboard with meal logging and nutrition tracking
- Indian food database with branded SKUs (Amul, Nestlé, etc.)
- Nutrition goal setting and progress tracking
- Gamified challenges and achievements

## Code Style

- Follow Flask best practices and PEP 8
- Use SQLAlchemy ORM for database operations
- Implement proper error handling and validation
- Use Bootstrap classes for responsive design
- Include comprehensive comments and docstrings
