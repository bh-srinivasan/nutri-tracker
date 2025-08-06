#!/usr/bin/env python3
"""Create a simple test page to debug the meal logging functionality."""

html_content = '''
<!DOCTYPE html>
<html>
<head>
    <title>Meal Logger Debug</title>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</head>
<body>
    <div class="container mt-4">
        <h2>Meal Logger Debug Test</h2>
        
        <div class="alert alert-info">
            <h6>Steps to test:</h6>
            <ol>
                <li>Open Developer Tools (F12)</li>
                <li>Go to Console tab</li>
                <li>Login as non-admin user (demo)</li>
                <li>Go to Log a Meal page</li>
                <li>Search for "rice"</li>
                <li>Click on first result</li>
                <li>Check if submit button becomes enabled</li>
            </ol>
        </div>
        
        <div class="alert alert-warning">
            <h6>What to look for in console:</h6>
            <ul>
                <li>Should see "[MealLogger] Selecting food with ID: X"</li>
                <li>Should see "[MealLogger] API response status: 200"</li>
                <li>Should see "[MealLogger] Received food data: {...}"</li>
                <li>Should see "[MealLogger] Food selection completed successfully"</li>
                <li>Check for any errors or failed API calls</li>
            </ul>
        </div>
        
        <p><a href="http://127.0.0.1:5001" class="btn btn-primary">Go to Nutri Tracker</a></p>
    </div>
</body>
</html>
'''

with open('debug_meal_logger.html', 'w') as f:
    f.write(html_content)

print("Debug page created: debug_meal_logger.html")
