from typing import Annotated
from datetime import datetime, timedelta
import random
import typer
import json
import uuid
import string
import os 
# List of taken UID's for taskso
uids = set()

# Function to create a UID for a task
def create_id() -> str:
    while True:
        uid = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        if uid not in uids:
            uids.add(uid)
            return uid

# Task()
class Task:
    task_id: str
    name: str
    description: str
    completed: bool
    due_date: datetime | None

    def __init__(self, name: str, description: str, due_date: datetime | None=None, task_id=None|str):
        print()
        self.task_id = None
        if id is None:
            self.task_id = create_id()
        else:
            print(type(task_id))
            self.task_id = task_id
        self.name = name
        self.description = description
        self.completed = False
        self.due_date = due_date


    def todict(self):
        return {"id": self.task_id, "name": self.name, "description": self.description, "completed": self.completed,"due_date": self.due_date}

    @staticmethod
    def fromdict(dict):
        return Task.__init__( dict["name"], dict["description"], dict["completed"], task_id=dict["id"])

class Storage:
    tasks: list[Task]
    path: str
    
    def __init__(self, path: str):
        self.tasks = []
        self.path = path
        if not os.path.exists(self.path):
            with open(self.path, 'w') as f:
                json.dump([], f)
        self.db = json.load(open(self.path, "r+"))
        self.load_tasks()

    def load_tasks(self):
        self.tasks = [Task.fromdict(d) for d in self.db]
        
    def add_task(self, task) -> str:
        self.tasks.append(task)
        self.sync()
        return task.id

    def sync(self):
        self.delete_over_due()
        try:
            self.db = [task.todict() for task in self.tasks]
            json.dump(self.db, open(self.path, "w+"))
        except Exception:
            raise RuntimeError(f"OS threw: {Exception}")

    def remove_task(self, task_id):
        self.tasks = [task for task in self.tasks if task.task_id != task_id]
        self.sync()

    def close(self):
        self.sync()
        self.db.close()

    def find_task(self, task_id) -> Task | None:
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    def replace(self, task_id, task_) -> None:
        for i, task in enumerate(self.tasks):
            if task.task_id == task_id:
                self.tasks[i] = task_
                return
        raise RuntimeError(f"Task with id {task_id} was not found")
            
    
    def complete(self, task_id):
        #Getting the task
        task = self.find_task(task_id)
        
        #Checking if the task is not empty
        if task:
            #Setting the complete to true a
            task.completed = True
            self.sync()
        else:
            raise RuntimeError(f"Task with id {task_id} was not found")

    def add_due_date(self, task_id, due_date):
        task = self.find_task(task_id)
        
        if task:
            task.due_date = due_date
            self.sync() 
        else:
            raise RuntimeError(f"Task with id {task_id} was not found")

    def delete_over_due(self):
        due_date_threshold = datetime.now().date() - timedelta(days=1)
        self.tasks = [task for task in self.tasks if not task.due_date or task.due_date >= due_date_threshold]



from rich import print, panel  # noqa: E402
 
storage = Storage("tasks.json")
storage.add_task(Task("Hello", "Hello"))
storage.sync()

app = typer.Typer()
@app.command()
def list(all: Annotated[bool, typer.Option()] = False):
    """
    Lists all uncompleted tasks.
    --all shows every single one.
    """
    for task in storage.tasks:
        completed = ""
        if task.completed:
            completed = "Yes"
        else:
            completed = "No"
        
        date = task.due_date
        if date is None:
            date = "None"
        print(panel.Panel("[green]" + task.name + "[/]", task.description, "[bold]completed: " + completed + "[/]", "Due Date: " + task.due_date))

@app.command()
def add():
    """
    Adds a new task to the list of tasks.
    """
    pass

@app.command()
def complete(task: str):
    """
    Completes a task.
    """
    pass

@app.command()
def uncomplete(task: str):
    """
    Uncompletes a task.
    """
    pass

@app.command()
def get(task: str):
    """
    Get description, name, author and completion status of a task.
    """
    pass

if __name__ == "__main__":
    app()
