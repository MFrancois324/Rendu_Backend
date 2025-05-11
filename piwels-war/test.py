import requests

# URL de base de votre serveur FastAPI
BASE_URL = "http://localhost:8000"

def test_preinit(nom_carte):
    url = f"{BASE_URL}/api/v1/{nom_carte}/preinit"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print(f"Preinit response for {nom_carte}: {response.json()}")
        return response.json()["key"]
    except requests.exceptions.RequestException as e:
        print(f"Error in preinit: {e}")
        return None

def test_init(nom_carte, key):
    url = f"{BASE_URL}/api/v1/{nom_carte}/init"
    params = {"keys": key}
    cookies = {"key": key}
    try:
        response = requests.get(url, params=params, cookies=cookies, timeout=10)
        response.raise_for_status()
        print(f"Init response for {nom_carte}: {response.json()}")
        return response.json()["id"]
    except requests.exceptions.RequestException as e:
        print(f"Error in init: {e}")
        return None

def test_deltas(nom_carte, user_id, key):
    url = f"{BASE_URL}/api/v1/{nom_carte}/deltas"
    params = {"id": user_id}
    cookies = {"id": user_id, "key": key}
    try:
        response = requests.get(url, params=params, cookies=cookies, timeout=10)
        response.raise_for_status()
        print(f"Deltas response for {nom_carte}: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error in deltas: {e}")

def test_set_pixel(nom_carte, user_id, key, x, y, r, g, b):
    url = f"{BASE_URL}/api/v1/{nom_carte}/set_pixel"
    pixel_data = {"x": x, "y": y, "r": r, "g": g, "b": b}
    cookies = {"id": user_id, "key": key}
    try:
        response = requests.post(url, json=pixel_data, cookies=cookies, timeout=10)
        response.raise_for_status()
        print(f"Set pixel response for {nom_carte}: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error in set_pixel: {e}")

if __name__ == "__main__":
    nom_carte = "0000"

    # Test preinit
    key = test_preinit(nom_carte)
    if key is None:
        print("Failed to get key from preinit")
        exit(1)

    # Test init
    user_id = test_init(nom_carte, key)
    if user_id is None:
        print("Failed to get user_id from init")
        exit(1)

    # Test deltas
    test_deltas(nom_carte, user_id, key)

    # Test set_pixel
    test_set_pixel(nom_carte, user_id, key, x=1, y=1, r=255, g=0, b=0)
