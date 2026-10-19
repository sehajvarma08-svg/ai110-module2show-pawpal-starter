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
        return self.due_time < other.end_time and other.due_time < self.end_time

    def mark_complete(self) -> Optional[Task]:
        """Mark complete and return the next occurrence if recurring, else None."""
        self.completed = True
        if self.recurrence == Recurrence.DAILY:
            step = timedelta(days=1)
        elif self.recurrence == Recurrence.WEEKLY:
            step = timedelta(weeks=1)
        else:
            return None
        next_task = Task(
            title=self.title,
            task_type=self.task_type,
            due_time=self.due_time + step,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            recurrence=self.recurrence,
        )
        if self.pet is not None:
            self.pet.add_task(next_task)
        return next_task

    def reschedule(self, new_time: datetime) -> None:
        """Move this task to a new due time."""
        self.due_time = new_time


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
        if any(t.id == task.id for t in self.tasks):
            return
        task.pet = self
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task (matched by id) from this pet."""
        for i, t in enumerate(self.tasks):
            if t.id == task.id:
                del self.tasks[i]
                t.pet = None
                return

    def get_tasks(self) -> List[Task]:
        """Return a copy of this pet's tasks."""
        return list(self.tasks)


@dataclass
class Owner:
    name: str
    email: str
    available_minutes_per_day: int
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner and set pet.owner (skip duplicates)."""
        if any(p is pet for p in self.pets):
            return
        pet.owner = self
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        for i, p in enumerate(self.pets):
            if p is pet:
                del self.pets[i]
                p.owner = None
                return

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.get_tasks()]


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
        """Create a scheduler for an owner with no plan built yet."""
        self.owner = owner
        self.last_plan: Optional[DailyPlan] = None

    def build_daily_plan(self, day: Optional[date] = None) -> DailyPlan:
        """Build a day's plan by priority within the time budget, skipping conflicts."""
        day = day or date.today()
        budget = self.owner.available_minutes_per_day
        plan = DailyPlan(day=day)

        todays = [
            t for t in self.owner.get_all_tasks()
            if not t.completed and t.due_time.date() == day
        ]
        for task in self.sort_by_priority(todays):
            if plan.total_minutes + task.duration_minutes > budget:
                plan.skipped.append(SkippedTask(task, "not enough time left in the day"))
                continue
            clash = next((t for t in plan.scheduled if task.overlaps(t)), None)
            if clash is not None:
                plan.skipped.append(SkippedTask(task, f"overlaps with '{clash.title}'"))
                continue
            plan.scheduled.append(task)
            plan.total_minutes += task.duration_minutes

        plan.scheduled = self.sort_by_time(plan.scheduled)
        self.last_plan = plan
        return plan

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Return tasks sorted by due time."""
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        return sorted(tasks, key=lambda t: t.due_time)

    def sort_by_priority(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Return tasks sorted by priority (highest first), ties by time."""
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        return sorted(tasks, key=lambda t: (-t.priority, t.due_time))

    def detect_conflicts(self, tasks: Optional[List[Task]] = None) -> List[Tuple[Task, Task]]:
        """Return pairs of tasks whose time windows overlap."""
        ordered = self.sort_by_time(tasks)
        conflicts: List[Tuple[Task, Task]] = []
        # Track the task that ends latest so far; any later task that starts
        # before it ends overlaps with it.
        latest: Optional[Task] = None
        for task in ordered:
            if latest is not None and task.overlaps(latest):
                conflicts.append((latest, task))
            if latest is None or task.end_time > latest.end_time:
                latest = task
        return conflicts

    def get_upcoming_tasks(self, now: Optional[datetime] = None) -> List[Task]:
        """Return incomplete tasks due after `now` (defaults to datetime.now())."""
        now = now or datetime.now()
        upcoming = [
            t for t in self.owner.get_all_tasks()
            if not t.completed and t.due_time > now
        ]
        return self.sort_by_time(upcoming)

    def explain_plan(self, plan: Optional[DailyPlan] = None) -> str:
        """Return a text summary of a plan's scheduled and skipped tasks."""
        plan = plan or self.last_plan or self.build_daily_plan()
        budget = self.owner.available_minutes_per_day

        def label(task: Task) -> str:
            return f"{task.title} ({task.pet.name})" if task.pet else task.title

        lines = [
            f"Plan for {plan.day:%A, %b %d}: {plan.total_minutes} of "
            f"{budget} available minutes used."
        ]
        if plan.scheduled:
            lines.append("Scheduled (highest priority first got the time):")
            for t in plan.scheduled:
                lines.append(
                    f"  {t.due_time:%H:%M}-{t.end_time:%H:%M}  {label(t)} "
                    f"[{t.priority.name.lower()} priority]"
                )
        else:
            lines.append("Nothing scheduled.")
        if plan.skipped:
            lines.append("Skipped:")
            for s in plan.skipped:
                lines.append(f"  {label(s.task)} - {s.reason}")
        return "\n".join(lines)
