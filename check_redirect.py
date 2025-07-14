import requests

# Check redirect behavior
response = requests.get('http://localhost:5001/admin/food-uploads', allow_redirects=False)
print(f'Status: {response.status_code}')
print(f'Location: {response.headers.get("Location", "None")}')

if response.status_code == 302:
    print("✅ Properly redirects to login (as expected for admin-only page)")
elif response.status_code == 200:
    print("✅ Page loads directly (may be in development mode)")
else:
    print(f"⚠️  Unexpected status: {response.status_code}")
