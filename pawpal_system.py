"""PawPal+ logic layer: Owner, Pet, Task and the Scheduler that ties them together."""
from dataclasses import dataclass, field
from datetime import date
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
        """Return today's tasks that are not yet completed."""
        today = date.today()
        return [t for t in self.owner.get_all_tasks()
                if t.due_date == today and not t.completed]
