#The Logic layer where all the backend classes live
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class Task:
    title: str
    task_type: str
    due_time: datetime
    duration_minutes: int
    priority: str = "medium"
    recurrence: str = "none"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        pass

    def reschedule(self, new_time: datetime) -> None:
        """Move this task to a new due time."""
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    notes: str = ""
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet."""
        pass

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        pass

    def get_tasks(self) -> List[Task]:
        """Return all tasks for this pet."""
        pass


@dataclass
class Owner:
    name: str
    email: str
    available_minutes_per_day: int
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        pass

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks across all of this owner's pets."""
        pass


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def build_daily_plan(self) -> List[Task]:
        """Build a daily plan that fits within the owner's available time."""
        pass

    def sort_by_time(self) -> List[Task]:
        """Return tasks sorted by due time."""
        pass

    def sort_by_priority(self) -> List[Task]:
        """Return tasks sorted by priority."""
        pass

    def detect_conflicts(self) -> List[Task]:
        """Return tasks whose scheduled times overlap."""
        pass

    def get_upcoming_tasks(self) -> List[Task]:
        """Return incomplete tasks due in the future."""
        pass

    def explain_plan(self) -> str:
        """Return a human-readable explanation of the daily plan."""
        pass
