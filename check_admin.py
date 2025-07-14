from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f"Admin user found: {admin.username}")
        print(f"Is admin: {admin.is_admin}")
        print(f"Is active: {admin.is_active}")
        print(f"Email: {admin.email}")
    else:
        print("No admin user found")
        
    # Also check for any admin users
    all_admins = User.query.filter_by(is_admin=True).all()
    print(f"Total admin users: {len(all_admins)}")
    for admin_user in all_admins:
        print(f"  - {admin_user.username} (active: {admin_user.is_active})")
