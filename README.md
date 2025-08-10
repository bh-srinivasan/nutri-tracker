# Nutri Tracker - Protein & Nutrition Tracking Web Application

A comprehensive Flask-based web application for tracking protein intake and overall nutrition, featuring an extensive Indian food database, user authentication, admin panel, and gamified challenges.

## 🚀 Features

### User Features
- **Secure Authentication**: Registration and login with strong password policies
- **Meal Logging**: Easy-to-use interface for logging meals with search functionality
- **Nutrition Tracking**: Track protein, calories, carbs, fat, fiber, and other nutrients
- **Goal Setting**: Set personalized nutrition goals based on your profile
- **Progress Analytics**: View detailed reports and charts of your nutrition intake
- **Gamified Challenges**: Participate in challenges like "30g Protein a Day"
- **Streak Tracking**: Maintain daily logging streaks for motivation

### Admin Features
- **User Management**: Create, edit, deactivate, and reset user passwords
- **Food Database Management**: Add, edit, and delete food items with nutritional data
- **Bulk Food Upload**: Import foods via CSV format
- **System Analytics**: View platform usage statistics and user activity
- **Challenge Management**: Create and manage nutrition challenges

### Food Database
- **Comprehensive Indian Food Database**: Traditional dishes, regional cuisines
- **Branded Products**: Popular Indian brands like Amul, Nestlé, Britannia, etc.
- **Nutritional Information**: Complete macronutrient and micronutrient data
- **Categorized Foods**: Organized by food groups for easy discovery

## 🛠️ Technology Stack

- **Backend**: Flask 2.3.3, SQLAlchemy, Werkzeug
- **Frontend**: Bootstrap 5.1.3, Font Awesome 6.0, Chart.js
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: Flask-Login with role-based access control
- **Forms**: Flask-WTF with comprehensive validation
- **Deployment**: Gunicorn WSGI server, Azure App Service ready

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip package manager
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Nutri_Tracker
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   # Development server
   python app.py
   
   # Or using Flask CLI
   flask run
   ```

7. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - Default admin credentials: `admin` / `admin123`

## 🏗️ Project Structure

```
Nutri_Tracker/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── admin/               # Admin panel blueprint
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── routes.py
│   ├── auth/                # Authentication blueprint
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── routes.py
│   ├── dashboard/           # User dashboard blueprint
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── routes.py
│   ├── api/                 # API endpoints blueprint
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── main/                # Main pages blueprint
│   │   ├── __init__.py
│   │   └── routes.py
│   └── templates/           # Jinja2 templates
│       ├── base.html
│       ├── auth/
│       ├── admin/
│       ├── dashboard/
│       └── main/
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── app.py                 # Application entry point
├── wsgi.py               # WSGI entry point
├── Procfile              # Heroku deployment
└── README.md             # This file
```

## 🎯 Usage

### For Users
1. **Sign Up**: Create an account with your basic information
2. **Complete Profile**: Add your age, gender, height, weight, and activity level
3. **Set Goals**: Define your nutrition targets based on your objectives
4. **Log Meals**: Search and log your meals throughout the day
5. **Track Progress**: Monitor your daily intake and progress towards goals
6. **Join Challenges**: Participate in community challenges for motivation

### For Admins
1. **Access Admin Panel**: Login with admin credentials
2. **Manage Users**: View, edit, and manage user accounts
3. **Manage Foods**: Add new foods or edit existing nutritional data
4. **View Analytics**: Monitor platform usage and user engagement
5. **Create Challenges**: Set up new challenges for users

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```bash
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///nutri_tracker.db
FLASK_ENV=development
FLASK_DEBUG=True

# Azure Storage (optional)
AZURE_STORAGE_CONNECTION_STRING=your-connection-string
AZURE_CONTAINER_NAME=food-images
```

### Database Configuration
- **Development**: SQLite database (`nutri_tracker.db`)
- **Production**: PostgreSQL or other supported databases
- **Migrations**: Handled by Flask-Migrate

## 🚀 Deployment

### Azure App Service

1. **Prepare for deployment**
   ```bash
   # Ensure all dependencies are in requirements.txt
   pip freeze > requirements.txt
   ```

2. **Create Azure App Service**
   - Use Azure Portal or Azure CLI
   - Choose Python 3.8+ runtime
   - Configure environment variables

3. **Deploy using Git**
   ```bash
   git add .
   git commit -m "Deploy to Azure"
   git push azure main
   ```

4. **Configure startup command**
   ```bash
   gunicorn --bind=0.0.0.0 --timeout 600 wsgi:app
   ```

### Other Platforms
- **Heroku**: Uses `Procfile` for deployment
- **Docker**: Dockerfile can be created for containerization
- **VPS**: Use Gunicorn with Nginx as reverse proxy

## 🧪 Testing

```bash
# Run tests (when implemented)
python -m pytest

# Run with coverage
python -m pytest --cov=app
```

## 📊 Database Schema

### Core Models
- **User**: User authentication and profile information
- **Food**: Food items with nutritional data
- **MealLog**: User meal logging entries
- **NutritionGoal**: User-defined nutrition targets
- **Challenge**: Gamified challenges
- **UserChallenge**: User participation in challenges

### Key Relationships
- Users have many MealLogs and NutritionGoals
- Foods are referenced by MealLogs
- Users can participate in multiple Challenges

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, email support@nutritracker.com or create an issue in the repository.

## 🧪 Manual Testing Notes

### Edit Meal Quantity Flow
To test the edit meal quantity functionality:

1. **Test Edit Quantity Prefill**:
   - Navigate to `/dashboard`
   - Click "Edit" on a meal with quantity=400g
   - Verify input shows 400 and preview shows values computed for 400g
   - Modify quantity; preview updates live

2. **Test Quantity Input Responsiveness**:
   - Change quantity value in the input field
   - Verify nutrition preview updates in real-time
   - Confirm calculations are accurate (e.g., 200g = half of 100g values)

## 🔮 Future Enhancements

- [ ] Mobile app development
- [ ] Barcode scanning for food items
- [ ] Integration with fitness trackers
- [ ] Meal planning features
- [ ] Social features and community
- [ ] AI-powered nutrition recommendations
- [ ] Multi-language support

## 🎉 Acknowledgments

- Bootstrap team for the amazing UI framework
- Font Awesome for the beautiful icons
- Flask community for the excellent documentation
- Indian food nutrition data sources
- All contributors and users of the platform

---

**Nutri Tracker** - Track your nutrition, achieve your goals! 🥗💪
