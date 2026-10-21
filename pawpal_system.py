"""PawPal+ logic layer: Owner, Pet, Task and the Scheduler that ties them together."""
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional
from typing import List


@dataclass
class Task:
    """A single pet-care activity (feeding, walk, medication, appointment)."""

    description: str
    time: str  # "HH:MM", 24-hour
    frequency: str = "once"  # "once", "daily" or "weekly"
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    pet_name: str = ""  # filled in by Pet.add_task

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def next_occurrence(self) -> Optional["Task"]:
        """Return a fresh task for the next daily/weekly due date, or None for one-off tasks."""
        step = {"daily": 1, "weekly": 7}.get(self.frequency)
        if step is None:
            return None
        return Task(self.description, self.time, self.frequency,
                    due_date=self.due_date + timedelta(days=step))


@dataclass
class Pet:
    """A pet and the tasks that belong to it."""

    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet and stamp it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)


@dataclass
class Owner:
    """A pet owner who manages one or more pets."""

    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_pet(self, name: str):
        """Return the pet with this name, or None."""
        return next((p for p in self.pets if p.name == name), None)

    def get_all_tasks(self) -> List[Task]:
        """Return every task from every pet in one flat list."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Reads tasks through the Owner and organizes them."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def get_todays_schedule(self) -> List[Task]:
        """Return today's tasks that are not yet completed, in time order."""
        today = date.today()
        return self.sort_by_time(
            [t for t in self.owner.get_all_tasks()
             if t.due_date == today and not t.completed])

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Sort tasks chronologically by (due date, "HH:MM"); defaults to all tasks."""
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        return sorted(tasks, key=lambda t: (t.due_date, t.time))

    def filter_tasks(self, pet_name: Optional[str] = None,
                     completed: Optional[bool] = None) -> List[Task]:
        """Return tasks matching the given pet name and/or completion status (None = any)."""
        return [t for t in self.owner.get_all_tasks()
                if (pet_name is None or t.pet_name == pet_name)
                and (completed is None or t.completed == completed)]

    def detect_conflicts(self) -> List[str]:
        """Return a warning string for every group of pending tasks sharing a date and time."""
        slots = {}
        for t in self.owner.get_all_tasks():
            if not t.completed:
                slots.setdefault((t.due_date, t.time), []).append(t)
        return [
            f"Conflict on {d} at {tm}: "
            + ", ".join(f"{t.pet_name}: {t.description}" for t in group)
            for (d, tm), group in sorted(slots.items()) if len(group) > 1
        ]

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Complete a task; for daily/weekly tasks add the next occurrence to the same pet."""
        task.mark_complete()
        nxt = task.next_occurrence()
        pet = self.owner.get_pet(task.pet_name)
        if nxt is not None and pet is not None:
            pet.add_task(nxt)
        return nxt
