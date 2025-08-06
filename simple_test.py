import requests

response = requests.get('http://localhost:5001/dashboard/log-meal')
print(f'Status: {response.status_code}')
print(f'Content length: {len(response.text)}')

# Check for key elements
has_food_search = 'foodSearch' in response.text
has_meal_logger = 'EnhancedMealLogger' in response.text
has_search_results = 'foodSearchResults' in response.text

print(f'Has foodSearch: {has_food_search}')
print(f'Has EnhancedMealLogger: {has_meal_logger}')
print(f'Has foodSearchResults: {has_search_results}')

# Show the title
import re
title_match = re.search(r'<title>(.*?)</title>', response.text)
if title_match:
    print(f'Page title: {title_match.group(1)}')

# Show first part of content to see what we get
print('\nFirst 1000 characters:')
print(response.text[:1000])
