import requests

def get_uuid_info(nickname):
    url = f"https://api.mojang.com/users/profiles/minecraft/{nickname}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "nickname": data["name"],
            "uuid": data["id"]
        }
    return {"error": "UUID not found"}
