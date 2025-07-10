import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEBHOOK = os.getenv("BITRIX_WEBHOOK_URL")

def get_users():
    url = f"{WEBHOOK}user.get.json"
    response = requests.get(url)
    data = response.json()

    employees = []
    for user in data.get("result", []):
        full_name = f"{user['LAST_NAME']} {user['NAME']} {user.get('SECOND_NAME', '')}".strip()
        employees.append({
            "id": user["ID"],
            "name": full_name,
            "email": user.get("EMAIL", "—"),
            "phone": user.get("PERSONAL_PHONE", "—"),
            "birth": user.get("PERSONAL_BIRTHDAY", "—"),
            "department": user.get("UF_DEPARTMENT", []),
            "start_date": user.get("DATE_REGISTER", "—"),
        })
    return employees
