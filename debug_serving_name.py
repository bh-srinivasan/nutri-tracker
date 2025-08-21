from app import create_app, db
from app.models import FoodServing

app = create_app()
with app.app_context():
    serving = FoodServing.query.get(139)
    print(f'Serving name: "{serving.serving_name}"')
    print(f'Starts with "1 ": {serving.serving_name.startswith("1 ")}')
    print(f'After removing first 2 chars: "{serving.serving_name[2:]}"')
