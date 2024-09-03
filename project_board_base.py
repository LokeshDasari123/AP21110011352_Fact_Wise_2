import json
import os
import uuid
from datetime import datetime

class ProjectBoardBase:
    """
    A project board is a unit of delivery for a project. Each board will have a set of tasks assigned to a user.
    """

    def __init__(self):
        self.boards = {}
        self.tasks = {}
        self.load_boards()
        self.load_tasks()

    def load_boards(self):
        if os.path.exists('db/boards.json'):
            with open('db/boards.json', 'r') as f:
                self.boards = json.load(f)
        else:
            self.boards = {}

    def save_boards(self):
        with open('db/boards.json', 'w') as f:
            json.dump(self.boards, f, indent=4)

    def load_tasks(self):
        if os.path.exists('db/tasks.json'):
            with open('db/tasks.json', 'r') as f:
                self.tasks = json.load(f)
        else:
            self.tasks = {}

    def save_tasks(self):
        with open('db/tasks.json', 'w') as f:
            json.dump(self.tasks, f, indent=4)

    def create_board(self, request: str) -> str:
        data = json.loads(request)
        board_id = str(uuid.uuid4())
        name = data['name']
        description = data['description']
        team_id = data['team_id']
        creation_time = datetime.now().isoformat()

        # Validation
        if len(name) > 64:
            raise ValueError("Board name exceeds maximum length")
        if len(description) > 128:
            raise ValueError("Description exceeds maximum length")

        # Check uniqueness of board name within the team
        if any(board['name'] == name and board['team_id'] == team_id for board in self.boards.values()):
            raise ValueError("Board name must be unique within the team")

        board = {
            "name": name,
            "description": description,
            "team_id": team_id,
            "creation_time": creation_time,
            "status": "OPEN",
            "end_time": None
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
        if board['status'] != 'OPEN':
            raise ValueError("Only OPEN boards can be closed")

        # Check if all tasks are COMPLETE
        if any(self.tasks[task_id]['status'] != 'COMPLETE' for task_id in self.tasks if self.tasks[task_id]['board
                board['status'] = 'CLOSED'
                board['end_time'] = datetime.now().isoformat()
                self.save_boards()
            
                return json.dumps({"status": "success"})

    def add_task(self, request: str) -> str:
        data = json.loads(request)
        task_id = str(uuid.uuid4())
        title = data['title']
        description = data['description']
        user_id = data['user_id']
        creation_time = datetime.now().isoformat()
        board_id = data['board_id']
    
        if len(title) > 64:
            raise ValueError("Task title exceeds maximum length")
        if len(description) > 128:
            raise ValueError("Description exceeds maximum length")
    
        if board_id not in self.boards:
            raise ValueError("Board not found")
        if self.boards[board_id]['status'] != 'OPEN':
            raise ValueError("Tasks can only be added to OPEN boards")
    
        # Check uniqueness of task title within the board
        if any(task['title'] == title for task in self.tasks.values() if task['board_id'] == board_id):
            raise ValueError("Task title must be unique within the board")
    
        task = {
            "title": title,
            "description": description,
            "user_id": user_id,
            "creation_time": creation_time,
            "status": "OPEN",
            "board_id": board_id
        }
    
        self.tasks[task_id] = task
        self.save_tasks()
    
        return json.dumps({"id": task_id})
    
    def update_task_status(self, request: str):
        data = json.loads(request)
        task_id = data['id']
        status = data['status']
    
        if task_id not in self.tasks:
            raise ValueError("Task not found")
    
        if status not in ["OPEN", "IN_PROGRESS", "COMPLETE"]:
            raise ValueError("Invalid status")
    
        task = self.tasks[task_id]
        task['status'] = status
        self.save_tasks()
    
    def list_boards(self, request: str) -> str:
        data = json.loads(request)
        team_id = data['id']
    
        boards = [
            {"id": board_id, "name": board['name']}
            for board_id, board in self.boards.items()
            if board['team_id'] == team_id and board['status'] == 'OPEN'
        ]
    
        return json.dumps(boards, indent=4)
    
    def export_board(self, request: str) -> str:
        data = json.loads(request)
        board_id = data['id']
    
        if board_id not in self.boards:
            raise ValueError("Board not found")
    
        board = self.boards[board_id]
        tasks = {task_id: task for task_id, task in self.tasks.items() if task['board_id'] == board_id}
    
        out_file_name = f"board_{board_id}.txt"
        with open(f"out/{out_file_name}", 'w') as file:
            file.write(f"Board Name: {board['name']}\n")
            file.write(f"Description: {board['description']}\n")
            file.write(f"Creation Time: {board['creation_time']}\n")
            file.write(f"Status: {board['status']}\n")
            file.write("\nTasks:\n")
            for task_id, task in tasks.items():
                file.write(f"Task ID: {task_id}\n")
                file.write(f"Title: {task['title']}\n")
                file.write(f"Description: {task['description']}\n")
                file.write(f"Assigned User: {task['user_id']}\n")
                file.write(f"Creation Time: {task['creation_time']}\n")
                file.write(f"Status: {task['status']}\n")
                file.write("\n")
    
        return json.dumps({"out_file": out_file_name})
