import json
import os
import requests

JSON_EXAMS = os.environ.get('EXAMS')

response = requests.get(JSON_EXAMS)
json_data = json.loads(response.text)

def groups_exam(group):
    return json_data[group]['exams']