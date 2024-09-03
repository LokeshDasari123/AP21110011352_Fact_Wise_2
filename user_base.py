import json
import os
import uuid
from datetime import datetime
from typing import List, Dict

from team_base import TeamBase

DB_PATH = 'db/teams.json'

class Team(TeamBase):
    def __init__(self):
        if not os.path.exists(DB_PATH):
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
            with open(DB_PATH, 'w') as db_file:
                json.dump({}, db_file)  
        self.load_teams()

    def load_teams(self):
        try:
            with open(DB_PATH, 'r') as db_file:
                self.teams = json.load(db_file)
        except json.JSONDecodeError:
            self.teams = {}  

    def save_teams(self):
        with open(DB_PATH, 'w') as db_file:
            json.dump(self.teams, db_file, indent=4)

    def create_team(self, request: str) -> str:
        data = json.loads(request)
        team_id = str(uuid.uuid4())
        name = data['name']
        description = data['description']
        admin = data['admin']

        if len(name) > 64 or len(description) > 128:
            raise ValueError("Team name or description exceeds maximum length")

        if name in [team['name'] for team in self.teams.values()]:
            raise ValueError("Team name must be unique")

        team = {
            "name": name,
            "description": description,
            "creation_time": datetime.now().isoformat(),
            "admin": admin,
            "users": [admin]
        }

        self.teams[team_id] = team
        self.save_teams()

        return json.dumps({"id": team_id})

    def list_teams(self) -> str:
        return json.dumps(list(self.teams.values()), indent=4)

    def describe_team(self, request: str) -> str:
        data = json.loads(request)
        team_id = data['id']

        if team_id not in self.teams:
            raise ValueError("Team not found")

        return json.dumps(self.teams[team_id], indent=4)

    def update_team(self, request: str) -> str:
        data = json.loads(request)
        team_id = data['id']
        team_details = data['team']
        name = team_details['name']
        description = team_details['description']
        admin = team_details['admin']

        if team_id not in self.teams:
            raise ValueError("Team not found")

        if len(name) > 64 or len(description) > 128:
            raise ValueError("Team name or description exceeds maximum length")

        
        if name in [team['name'] for team_id_check, team in self.teams.items() if team_id_check != team_id]:
            raise ValueError("Team name must be unique")

        team = self.teams[team_id]
        team.update({
            "name": name,
            "description": description,
            "admin": admin
        })
        self.save_teams()

        return json.dumps({"status": "success"})

    def add_users_to_team(self, request: str):
        data = json.loads(request)
        team_id = data['id']
        users = data['users']

        if team_id not in self.teams:
            raise ValueError("Team not found")

        team = self.teams[team_id]
        if len(team['users']) + len(users) > 50:
            raise ValueError("Cannot add more than 50 users to a team")

        team['users'].extend(users)
        self.save_teams()

        return json.dumps({"status": "success"})

    def remove_users_from_team(self, request: str):
        data = json.loads(request)
        team_id = data['id']
        users = data['users']

        if team_id not in self.teams:
            raise ValueError("Team not found")

        team = self.teams[team_id]
        team['users'] = [user for user in team['users'] if user not in users]
        self.save_teams()

        return json.dumps({"status": "success"})

        def list_team_users(self, request: str):
        data = json.loads(request)
        team_id = data['id']

        if team_id not in self.teams:
            raise ValueError("Team not found")

        team = self.teams[team_id]
        users = team['users']

        
        user_details = [{"id": user, "name": f"User {user}", "display_name": f"User {user}"} for user in users]

        return json.dumps(user_details, indent=4)
