from typing import Annotated
from datetime import datetime, timedelta
import random
from rich import print, panel  # noqa: E402
from rich.table import Table
from rich.console import Console
import typer
import json
import string
import os

# List of taken UID's for taskso
uids = set()


# Function to create a UID for a task
def create_id() -> str:
    while True:
        uid = "".join(random.choices(string.ascii_letters + string.digits, k=6))
        if uid not in uids:
            uids.add(uid)
            return uid


# This class defines a general Task. It contains an id, that is unique to each task.
class Task:
    task_id: str
    name: str
    description: str
    completed: bool
    due_date: datetime | None

    # If task_id is None, we generate a new, unique id
    def __init__(
        self,
        name: str,
        description: str,
        due_date: datetime | None = None,
        task_id: str = None,
    ):
        self.task_id = task_id or create_id()
        self.name = name
        self.description = description
        self.completed = False
        self.due_date = due_date

    def todict(self):
        return {
            "id": self.task_id,
            "name": self.name,
            "description": self.description,
            "completed": self.completed,
            "due_date": self.due_date.isoformat() if self.due_date else None,
        }

    @staticmethod
    def fromdict(dict):
        due_date = (
            datetime.fromisoformat(dict["due_date"]) if dict["due_date"] else None
        )
        task = Task(dict["name"], dict["description"], due_date, task_id=dict["id"])
        task.completed = dict["completed"]
        return task


# The Storage class, reads and writes all the task from a file provided by the constructor.
class Storage:
    tasks: list[Task]
    path: str

    def __init__(self, path: str):
        self.tasks = []
        self.path = path
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                json.dump([], f)
        self.load_tasks()

    def load_tasks(self):
        try:
            with open(self.path, "r+") as fd:
                db = json.load(fd)
                for task in db:
                    self.tasks.append(Task.fromdict(task))
        except Exception as err:
            raise RuntimeError(f"Error occurred while loading tasks: {err}")

    def add_task(self, task) -> str:
        self.tasks.append(task)
        self.sync()
        return task.task_id

    # Removes all over due tasks and stores the tasks in a file
    def sync(self):
        self.delete_over_due()
        try:
            with open(self.path, "w") as fd:
                tasks = [task.todict() for task in self.tasks]
                json.dump(tasks, fd)
        except Exception as e:
            raise RuntimeError(f"Error occurred while syncing tasks: {e}")

    def remove_task(self, task_id):
        self.tasks = [task for task in self.tasks if task.task_id != task_id]
        self.sync()

    def find_task(self, task_id) -> Task | None:
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None


    def complete(self, task_id):
        task = self.find_task(task_id)

        if task:
            task.completed = True
            self.sync()
        else:
            raise RuntimeError(f"Task with id {task_id} was not found")

    def uncomplete(self, task_id):
        task = self.find_task(task_id)

        if task:
            task.completed = False
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

    # Removes all dates from the array, that are overdue
    def delete_over_due(self):
        due_date_threshold = datetime.combine(
            datetime.now().date() - timedelta(days=1), datetime.min.time()
        )
        self.tasks = [
            task
            for task in self.tasks
            if not task.due_date or task.due_date >= due_date_threshold
        ]


console = Console()

storage = Storage("tasks.json")

app = typer.Typer()


def main():
    app()


@app.command()
def list(all: Annotated[bool, typer.Option()] = False):
    """
    Lists all uncompleted tasks.
    --all shows every single one.
    """
    # procentage of all completed tasks
    completed = len([task for task in storage.tasks if task.completed])
    total = len(storage.tasks)
    proc = 0
    if total == 0:
        proc = 0.0
    else:
        proc = (completed / total) * 100

    table = Table(title=f"Task List - [green]({proc:.2f}%)[/green] Completed")

    table.add_column("Task ID", justify="center", style="cyan", no_wrap=True)
    table.add_column("Name", justify="left", style="green")
    table.add_column("Description", justify="left", style="magenta")
    table.add_column("Completed", justify="center")
    table.add_column("Due Date", justify="center", style="yellow")

    for task in storage.tasks:
        completed = "[green]Yes[/green]" if task.completed else "[red]No[/red]"
        date = task.due_date.isoformat() if task.due_date else "None"
        table.add_row(
            task.task_id,
            task.name,
            task.description,
            completed,
            date,
        )

    console.print(table)


@app.command()
def add():
    """
    Adds a new task to the list of tasks.
    """
    name = typer.prompt("Task Name")
    description = typer.prompt("Task Description")
    due_date_str = typer.prompt("Due Date (YYYY-MM-DD)", default="")

    due_date = None
    if due_date_str:
        try:
            due_date = datetime.fromisoformat(due_date_str)
        except ValueError:
            print("[red]Invalid date format. Please use YYYY-MM-DD.[/red]")
            return

    task = Task(name, description, due_date)
    storage.add_task(task)
    date_display = due_date.isoformat() if due_date else "No due date"
    print(
        f"[green]Task '{task.name}' with ID '{task.task_id}' added successfully. Due Date: {date_display}[/green]"
    )


@app.command()
def complete(task: str):
    """
    Completes a task.
    """
    storage.complete(task)
    print(f"[green]Task with ID '{task}' has been completed.[/green]")
    return


@app.command()
def uncomplete(task: str):
    """
    Uncompletes a task.
    """
    storage.uncomplete(task)
    print(f"[green]Task with ID '{task}' has been uncompleted.[/green]")
    return


@app.command()
def get(task: str):
    """
    Get description, name, author and completion status of a task.
    """
    task = storage.find_task(task)
    if task:
        print(f"[green]Task ID: {task.task_id}[/green]")
        print(f"[green]Name: {task.name}[/green]")
        print(f"[green]Description: {task.description}[/green]")
        print(f"[green]Completed: {task.completed}[/green]")
        print(f"[green]Due Date: {task.due_date}[/green]")
    else:
        print(f"[red]Task with ID '{task}' not found.[/red]")


if __name__ == "__main__":
    main()
