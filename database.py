import openfoodfacts

config = {"database": "http://192.168.1.45:5000"}
api = openfoodfacts.API(user_agent="MyAwesomeApp/1.0")

import requests

def check_linked_lists(barcode: str) -> tuple[bool, dict]:
    response = requests.get(f"{config['database']}/query/links/{barcode}")
    if response.status_code == 200:
        link = response.json()
        return True, link
    return False, {}

def check_pantry_database(barcode: str) -> tuple[bool, dict]:
    reponse = requests.get(f"{config['database']}/query/{barcode}")
    if reponse.status_code == 200:
        data = reponse.json()
        return True, data
    return False, {}

def check_openfoodfacts_api(barcode: str) -> tuple[bool, dict]:
    data = api.product.get(barcode)
    if data != None:
        return True, data
    return False, {}

# Receipts Database Handling Helper Functions
def fetch_receipts():
    response = requests.get(f"{config['database']}/query/receipts")
    if response.status_code == 200:
        return response.json()['receipts']
    return []

def fetch_receipt(id):
    response = requests.get(f"{config['database']}/query/receipt/{id}")
    if response.status_code == 200:
        return response.json()['receipt']
    return {}

def insert_receipt(data):
    response = requests.post(f"{config['database']}/query/receipt/insert", json=data)
    if response.status_code == 200:
        return True
    return False

def update_receipt(id, data):
    response = requests.post(f"{config['database']}/query/receipt/update/{id}", json=data)
    if response.status_code == 200:
        return True
    return False

def resolve_receipt(id):
    response = requests.post(f"{config['database']}/query/receipt/resolve/{id}")
    if response.status_code == 200:
        return True
    return False

def deny_receipt(id):
    response = requests.post(f"{config['database']}/query/receipt/deny/{id}")
    if response.status_code == 200:
        return True
    return False


# Vendor Database Handling Helper Functions
def insert_vendor(data):
    response = requests.post(f"{config['database']}/query/vendor/insert", json=data)
    if response.status_code == 200:
        return True
    return False

def fetch_vendors():
    response = requests.get(f"{config['database']}/query/vendors")
    if response.status_code == 200:
        return response.json()['vendors']
    return []

def fetch_vendor(id):
    response = requests.get(f"{config['database']}/query/vendor/{id}")
    if response.status_code == 200:
        return response.json()['vendor']
    return {}

def update_vendor(id, data):
    response = requests.post(f"{config['database']}/query/vendor/update/{id}", json=data)
    if response.status_code == 200:
        return True
    return False

def delete_vendor(id):
    response = requests.get(f"{config['database']}/query/vendor/delete/{id}")
    if response.status_code == 200:
        return True
    return False