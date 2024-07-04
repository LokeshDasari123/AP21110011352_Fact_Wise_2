import json
import os
import uuid
from datetime import datetime
from typing import List, Dict

from user_base import UserBase

USER_DB_PATH = '../db/users.json'
TEAM_DB_PATH = '../db/teams.json'

class User(UserBase):
    def __init__(self):
        if not os.path.exists(USER_DB_PATH):
            os.makedirs(os.path.dirname(USER_DB_PATH), exist_ok=True)
            with open(USER_DB_PATH, 'w') as db_file:
                json.dump({}, db_file)
        if not os.path.exists(TEAM_DB_PATH):
            os.makedirs(os.path.dirname(TEAM_DB_PATH), exist_ok=True)
            with open(TEAM_DB_PATH, 'w') as db_file:
                json.dump({}, db_file)
        self.load_users()
        self.load_teams()

    def load_users(self):
        with open(USER_DB_PATH, 'r') as db_file:
            self.users = json.load(db_file)

    def save_users(self):
        with open(USER_DB_PATH, 'w') as db_file:
            json.dump(self.users, db_file, indent=4)

    def load_teams(self):
        with open(TEAM_DB_PATH, 'r') as db_file:
            self.teams = json.load(db_file)

    def save_teams(self):
        with open(TEAM_DB_PATH, 'w') as db_file:
            json.dump(self.teams, db_file, indent=4)

    def create_user(self, request: str) -> str:
        data = json.loads(request)
        user_id = str(uuid.uuid4())
        name = data['name']
        display_name = data['display_name']

        if len(name) > 64 or len(display_name) > 64:
            raise ValueError("User name or display name exceeds maximum length")

        if name in [user['name'] for user in self.users.values()]:
            raise ValueError("User name must be unique")

        user = {
            "name": name,
            "display_name": display_name,
            "creation_time": datetime.now().isoformat()
        }

        self.users[user_id] = user
        self.save_users()

        return json.dumps({"id": user_id})

    def list_users(self) -> str:
        return json.dumps(list(self.users.values()), indent=4)

    def describe_user(self, request: str) -> str:
        data = json.loads(request)
        user_id = data['id']

        if user_id not in self.users:
            raise ValueError("User not found")

        return json.dumps(self.users[user_id], indent=4)

    def update_user(self, request: str) -> str:
        data = json.loads(request)
        user_id = data['id']
        user_details = data['user']
        display_name = user_details['display_name']

        if len(display_name) > 64:
            raise ValueError("Display name exceeds maximum length")

        if user_id not in self.users:
            raise ValueError("User not found")

        user = self.users[user_id]
        user.update({
            "display_name": display_name
        })
        self.save_users()

        return json.dumps({"status": "success"})

    def get_user_teams(self, request: str) -> str:
        data = json.loads(request)
        user_id = data['id']

        if user_id not in self.users:
            raise ValueError("User not found")

        user_teams = [
            {
                "name": team['name'],
                "description": team['description'],
                "creation_time": team['creation_time']
            }
            for team in self.teams.values()
            if user_id in team['users']
        ]

        return json.dumps(user_teams, indent=4)
