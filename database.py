config = {"database": "http://192.168.1.45:5000"}

import requests

def fetch_receipts():
    response = requests.get(f"{config['database']}/query/receipts")
    if response.status_code == 200:
        return response.json()['receipts']
    return {}

def fetch_receipt(id):
    response = requests.get(f"{config['database']}/query/receipt/{id}")
    if response.status_code == 200:
        return response.json()['receipt']
    return {}

def update_receipt(id, data):
    response = requests.post(f"{config['database']}/query/receipt/update/{id}", json=data)
    if response.status_code == 200:
        return True
    return False