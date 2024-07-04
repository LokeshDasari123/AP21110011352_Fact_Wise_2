import json
import os
import uuid
from datetime import datetime

from ..project_board_base import ProjectBoardBase

BOARD_DB_PATH = '../db/boards.json'
TASK_DB_PATH = '../db/tasks.json'
TEAM_DB_PATH = '../db/teams.json'

class ProjectBoard(ProjectBoardBase):
    def __init__(self):
        if not os.path.exists(BOARD_DB_PATH):
            os.makedirs(os.path.dirname(BOARD_DB_PATH), exist_ok=True)
            with open(BOARD_DB_PATH, 'w') as db_file:
                json.dump({}, db_file)
        if not os.path.exists(TASK_DB_PATH):
            os.makedirs(os.path.dirname(TASK_DB_PATH), exist_ok=True)
            with open(TASK_DB_PATH, 'w') as db_file:
                json.dump({}, db_file)
        if not os.path.exists(TEAM_DB_PATH):
            os.makedirs(os.path.dirname(TEAM_DB_PATH), exist_ok=True)
            with open(TEAM_DB_PATH, 'w') as db_file:
                json.dump({}, db_file)
        self.load_boards()
        self.load_tasks()
        self.load_teams()

    def load_boards(self):
        with open(BOARD_DB_PATH, 'r') as db_file:
            self.boards = json.load(db_file)

    def save_boards(self):
        with open(BOARD_DB_PATH, 'w') as db_file:
            json.dump(self.boards, db_file, indent=4)

    def load_tasks(self):
        with open(TASK_DB_PATH, 'r') as db_file:
            self.tasks = json.load(db_file)

    def save_tasks(self):
        with open(TASK_DB_PATH, 'w') as db_file:
            json.dump(self.tasks, db_file, indent=4)

    def load_teams(self):
        with open(TEAM_DB_PATH, 'r') as db_file:
            self.teams = json.load(db_file)

    def create_board(self, request: str) -> str:
        data = json.loads(request)
        board_id = str(uuid.uuid4())
        name = data['name']
        description = data['description']
        team_id = data['team_id']
        creation_time = data['creation_time']

        if len(name) > 64 or len(description) > 128:
            raise ValueError("Board name or description exceeds maximum length")

        if team_id not in self.teams:
            raise ValueError("Team does not exist")

        if name in [board['name'] for board in self.boards.values() if board['team_id'] == team_id]:
            raise ValueError("Board name must be unique for the team")

        board = {
            "name": name,
            "description": description,
            "team_id": team_id,
            "creation_time": creation_time,
            "status": "OPEN"
        }

        self.boards[board_id] = board
        self.save_boards()

        return json.dumps({"id": board_id})

    def close_board(self, request: str) -> str:
        data = json.loads(request)
        board_id = data['id']

        if board_id not in self.boards:
            raise ValueError("Board not found")

        board = self.boards[board_id]

        if board['status'] != "OPEN":
            raise ValueError("Only open boards can be closed")

        board_tasks = [task for task in self.tasks.values() if task['board_id'] == board_id]
        if any(task['status'] != "COMPLETE" for task in board_tasks):
            raise ValueError("All tasks must be complete to close the board")

        board['status'] = "CLOSED"
        board['end_time'] = datetime.now().isoformat()
        self.save_boards()

        return json.dumps({"status": "success"})

    def add_task(self, request: str) -> str:
        data = json.loads(request)
        task_id = str(uuid.uuid4())
        title = data['title']
        description = data['description']
        user_id = data['user_id']
        creation_time = data['creation_time']
        board_id = data['board_id']

        if len(title) > 64 or len(description) > 128:
            raise ValueError("Task title or description exceeds maximum length")

        if board_id not in self.boards:
            raise ValueError("Board does not exist")

        board = self.boards[board_id]

        if board['status'] != "OPEN":
            raise ValueError("Tasks can only be added to open boards")

        if title in [task['title'] for task in self.tasks.values() if task['board_id'] == board_id]:
            raise ValueError("Task title must be unique for the board")

        task = {
            "title": title,
            "description": description,
            "user_id": user_id,
            "creation_time": creation_time,
            "board_id": board_id,
            "status": "OPEN"
        }

        self.tasks[task_id] = task
        self.save_tasks()

        return json.dumps({"id": task_id})

    def update_task_status(self, request: str):
        data = json.loads(request)
        task_id = data['id']
        status = data['status']

        if status not in ["OPEN", "IN_PROGRESS", "COMPLETE"]:
            raise ValueError("Invalid status")

        if task_id not in self.tasks:
            raise ValueError("Task not found")

        task = self.tasks[task_id]
        task['status'] = status
        self.save_tasks()

        return json.dumps({"status": "success"})

    def list_boards(self, request: str) -> str:
        data = json.loads(request)
        team_id = data['id']

        if team_id not in self.teams:
            raise ValueError("Team not found")

        open_boards = [
            {"id": board_id, "name": board['name']}
            for board_id, board in self.boards.items()
            if board['team_id'] == team_id and board['status'] == "OPEN"
        ]

        return json.dumps(open_boards, indent=4)

    def export_board(self, request: str) -> str:
        data = json.loads(request)
        board_id = data['id']

        if board_id not in self.boards:
            raise ValueError("Board not found")

        board = self.boards[board_id]
        tasks = [task for task in self.tasks.values() if task['board_id'] == board_id]

        output = f"Board: {board['name']}\nDescription: {board['description']}\nCreation Time: {board['creation_time']}\nStatus: {board['status']}\n\nTasks:\n"
        for task in tasks:
            output += f"Task: {task['title']}\nDescription: {task['description']}\nAssigned to: {task['user_id']}\nStatus: {task['status']}\nCreation Time: {task['creation_time']}\n\n"

        output_file = f"out/board_{board_id}.txt"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(output)

        return json.dumps({"out_file": output_file})
