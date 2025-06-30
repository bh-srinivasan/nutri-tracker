from app import create_app, db
from app.models import User, Food, MealLog, NutritionGoal, Challenge, UserChallenge

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell."""
    return {
        'db': db,
        'User': User,
        'Food': Food,
        'MealLog': MealLog,
        'NutritionGoal': NutritionGoal,
        'Challenge': Challenge,
        'UserChallenge': UserChallenge
    }

if __name__ == '__main__':
    app.run(debug=True, port=5001)
