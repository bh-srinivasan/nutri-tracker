# Test file to verify Python imports work
import sys
print("Python version:", sys.version)
print("Python executable:", sys.executable)

try:
    import flask
    print("✅ Flask imported successfully")
    print("Flask version:", flask.__version__)
except ImportError as e:
    print("❌ Flask import failed:", e)

try:
    import flask_sqlalchemy
    print("✅ Flask-SQLAlchemy imported successfully")
except ImportError as e:
    print("❌ Flask-SQLAlchemy import failed:", e)

try:
    import flask_login
    print("✅ Flask-Login imported successfully")
except ImportError as e:
    print("❌ Flask-Login import failed:", e)

try:
    import flask_wtf
    print("✅ Flask-WTF imported successfully")
except ImportError as e:
    print("❌ Flask-WTF import failed:", e)

try:
    import wtforms
    print("✅ WTForms imported successfully")
except ImportError as e:
    print("❌ WTForms import failed:", e)

try:
    import sqlalchemy
    print("✅ SQLAlchemy imported successfully")
except ImportError as e:
    print("❌ SQLAlchemy import failed:", e)

try:
    import werkzeug
    print("✅ Werkzeug imported successfully")
except ImportError as e:
    print("❌ Werkzeug import failed:", e)

print("\nAll tests completed!")
