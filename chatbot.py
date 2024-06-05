import requests
import json

BASE_URL = "http://localhost:8080/v1/api/"
API_KEY = open('.chatapi', 'r').readline().rstrip()
HEADERS={'Authorization': f'Bearer {API_KEY}',
         'Content-Type': 'application/json'}

def create_conversation(uid):
    api_url = BASE_URL + "new_conversation"
    payload = {'user_id': uid}
    response = requests.get(api_url, headers=HEADERS, json=payload)
    return response.json()

def get_answer(uid, json):
    return 0

def get_doc_list(kb):
    api_url = BASE_URL + "list_kb_docs"
    payload = {'kb_name': kb,
               'page': 1,
               'page_size': 15,
               'orderby': 'create_time'}
    response = requests.post(api_url, headers=HEADERS, json=payload)
    return response.json()
