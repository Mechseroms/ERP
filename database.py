import openfoodfacts, copy

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
def fetch_receipts() -> list:
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
    response = requests.post(f"{config['database']}/external/api/add_receipt", json=data)
    if response.status_code == 200:
        return True, response.json()["message"], response.json()["receipt_id"]
    return False, response.json()["message"], 0

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

def resolve_receipt_line(id: int, items: list):
    response = requests.post(f"{config['database']}/external/api/resolve-line/{id}", json={"items": items})
    if response.status_code == 200:
        return True, response.json()["messages"]
    return False, response.json()["messages"]

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


def fetch_pantry_paginated(page, search_query):
    query_a = "WHERE search_string LIKE ?"
    params_a = [f"%{search_query}%"]
        
    limit = 50
    offset = (page - 1) * limit

    query_b = query_a
    query_a += " LIMIT ? OFFSET ?"
    params_b = copy.deepcopy(params_a)
    params_a.append(limit)
    params_a.append(offset)

    print(query_a)
    print(params_a)

    payload = {
        "page": page,
        "query_a": query_a,
        "query_b": query_b,
        "params_a": params_a,
        "params_b": params_b,
        "limit": limit
    }

    response = requests.post(f"{config['database']}/query/pantry", json=payload)
    if response.status_code == 200:
        return True, response.json()
    return False, []

def fetch_pantry(id):
    response = requests.get(f"{config['database']}/query/pantry/{id}")
    if response.status_code == 200:
        return response.json()['item']
    return {}

def update_pantry(id, payload: dict) -> bool:
    response = requests.post(f"{config['database']}/query/pantry/update/{id}", json=payload)
    if response.status_code == 200:
        return True
    return False

# Recipes database functions
def fetch_recipe(id):
    response = requests.get(f"{config['database']}/query/recipe/{id}")
    if response.status_code == 200:
        return response.json()['recipe']
    return {}

# Groups Functions
def fetch_shopping_list(id):
    response = requests.get(f"{config['database']}/query/shopping_list/{id}")
    if response.status_code == 200:
        return response.json()['shopping_list']
    return {}

# shoppinglist Functions
def fetch_group(id):
    response = requests.get(f"{config['database']}/query/group/{id}")
    if response.status_code == 200:
        return response.json()['group']
    return {}