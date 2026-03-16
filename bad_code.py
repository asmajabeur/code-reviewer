import os
import requests
from django.db import connection

# BAD: Secret API key in plain text
SECRET_API_KEY = "sk_live_1234567890abcdef"

def fetch_data(user_id):
    # BAD: Unused variable (Logic / Style)
    x = 10
    
    # BAD: SQL Injection vulnerability (Security)
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    
    # BAD: Redundant / inefficient loop just for example
    final_res = []
    for r in results:
        for item in r:
            final_res.append(item)
            
    return final_res

def check_website():
    # Calling external request library (Security agent might check CVE for 'requests')
    response = requests.get("http://example.com")
    print("Code: " + response.status_code) # BAD: Type error logic (string + int)
