#The Logic layer where all the backend classes live
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum, IntEnum
from typing import List, Optional, Tuple
from uuid import uuid4


class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Recurrence(Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"


class TaskType(Enum):
    FEEDING = "feeding"
    WALK = "walk"
    MEDICATION = "medication"
    GROOMING = "grooming"
    VET = "vet"
    OTHER = "other"


@dataclass
class Task:
    title: str
    task_type: TaskType
    due_time: datetime
    duration_minutes: int
    priority: Priority = Priority.MEDIUM
    recurrence: Recurrence = Recurrence.NONE
    completed: bool = False
    id: str = field(default_factory=lambda: uuid4().hex)
    pet: Optional[Pet] = field(default=None, repr=False, compare=False)

    @property
    def end_time(self) -> datetime:
        """Return when this task finishes (due_time + duration)."""
        return self.due_time + timedelta(minutes=self.duration_minutes)

    def overlaps(self, other: Task) -> bool:
        """Return True if this task's time window overlaps another's."""
        pass

    def mark_complete(self) -> Optional[Task]:
        """Mark complete; return the next occurrence if recurring, else None."""
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
    owner: Optional[Owner] = field(default=None, repr=False, compare=False)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet and set task.pet to this pet."""
        pass

    def remove_task(self, task: Task) -> None:
        """Remove a task (matched by id) from this pet."""
        pass

    def get_tasks(self) -> List[Task]:
        """Return a copy of this pet's tasks."""
        pass


@dataclass
class Owner:
    name: str
    email: str
    available_minutes_per_day: int
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner and set pet.owner (skip duplicates)."""
        pass

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        pass

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks across all of this owner's pets."""
        pass


@dataclass
class SkippedTask:
    task: Task
    reason: str


@dataclass
class DailyPlan:
    day: date
    scheduled: List[Task] = field(default_factory=list)
    skipped: List[SkippedTask] = field(default_factory=list)
    total_minutes: int = 0


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner = owner
        self.last_plan: Optional[DailyPlan] = None

    def build_daily_plan(self, day: Optional[date] = None) -> DailyPlan:
        """Plan one day: filter incomplete tasks, sort by priority then time,
        add greedily while the time budget and conflict checks pass, and record
        skipped tasks with reasons. Stores the result in self.last_plan."""
        pass

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Return tasks sorted by due time."""
        pass

    def sort_by_priority(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Return tasks sorted by priority (highest first), ties by time."""
        pass

    def detect_conflicts(self, tasks: Optional[List[Task]] = None) -> List[Tuple[Task, Task]]:
        """Return pairs of tasks whose time windows overlap.
        Sort by time and compare neighbors instead of checking every pair."""
        pass

    def get_upcoming_tasks(self, now: Optional[datetime] = None) -> List[Task]:
        """Return incomplete tasks due after `now` (defaults to datetime.now())."""
        pass

    def explain_plan(self, plan: Optional[DailyPlan] = None) -> str:
        """Explain a plan (defaults to last_plan): what was scheduled, what was
        skipped and why, including pet names."""
        pass
