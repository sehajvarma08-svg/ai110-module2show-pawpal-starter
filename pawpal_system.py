#The Logic layer where all the backend classes live
from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, datetime, time, timedelta
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
    # For a projected copy of a recurring task (see Scheduler.build_daily_plan):
    # the stored task it was copied from, so completing the copy completes it.
    source: Optional[Task] = field(default=None, repr=False, compare=False)

    @property
    def end_time(self) -> datetime:
        """Return when this task finishes (due_time + duration)."""
        return self.due_time + timedelta(minutes=self.duration_minutes)

    @property
    def is_must_do(self) -> bool:
        """Return True for tasks that should never be dropped (medication, vet)."""
        # CHANGE (#3): health-critical tasks bypass the daily time budget.
        return self.task_type in (TaskType.MEDICATION, TaskType.VET)

    def occurs_on(self, day: date) -> bool:
        """Return True if this task falls on `day`, counting recurrence."""
        # CHANGE (#6): recurring tasks now show up on future days, not just
        # on their original due date.
        start = self.due_time.date()
        if day < start:
            return False
        if self.recurrence == Recurrence.DAILY:
            return True
        if self.recurrence == Recurrence.WEEKLY:
            return (day - start).days % 7 == 0
        return day == start

    def overlaps(self, other: Task) -> bool:
        """Return True if this task's time window overlaps another's."""
        return self.due_time < other.end_time and other.due_time < self.end_time

    def mark_complete(self, now: Optional[datetime] = None) -> Optional[Task]:
        """Mark complete and return the next occurrence if recurring, else None."""
        # CHANGE (#7): calling this twice used to spawn two copies of the next
        # occurrence; now a second call is a no-op.
        # CHANGE (#8): a projected copy completes the stored task it came from,
        # and the next occurrence is never scheduled in the past.
        original = self.source or self
        if self.completed or original.completed:
            return None
        self.completed = True
        original.completed = True
        if self.recurrence == Recurrence.DAILY:
            step = timedelta(days=1)
        elif self.recurrence == Recurrence.WEEKLY:
            step = timedelta(weeks=1)
        else:
            return None
        now = now or datetime.now()
        next_due = self.due_time + step
        while next_due <= now:
            next_due += step
        next_task = Task(
            title=self.title,
            task_type=self.task_type,
            due_time=next_due,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            recurrence=self.recurrence,
        )
        pet = original.pet or self.pet
        if pet is not None:
            pet.add_task(next_task)
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
    # CHANGE (#1): when a task was skipped for overlapping, suggest a free slot.
    suggested_time: Optional[datetime] = None


@dataclass
class DailyPlan:
    day: date
    scheduled: List[Task] = field(default_factory=list)
    skipped: List[SkippedTask] = field(default_factory=list)
    total_minutes: int = 0
    # CHANGE (#3): True when must-do tasks pushed the plan past the budget.
    over_budget: bool = False


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        """Create a scheduler for an owner with no plan built yet."""
        self.owner = owner
        self.last_plan: Optional[DailyPlan] = None

    def build_daily_plan(self, day: Optional[date] = None) -> DailyPlan:
        """Build a day's plan by priority within the time budget, skipping conflicts.

        Algorithm: collect incomplete tasks that occur on `day` (recurring
        tasks are projected onto `day`), order them must-do first, then by
        priority (high to low), then by due time, and greedily accept each
        one. A task is skipped if it would exceed the daily budget (must-do
        tasks are exempt and set `over_budget`) or overlaps an already
        accepted task; overlap skips get a suggested free slot.

        Args:
            day: The day to plan; defaults to today.

        Returns:
            A DailyPlan with scheduled tasks sorted by time and the skipped
            tasks with reasons. Also stored in `self.last_plan`.
        """
        day = day or date.today()
        budget = self.owner.available_minutes_per_day
        plan = DailyPlan(day=day)

        # CHANGE (#6): use occurs_on() so recurring tasks appear on future days.
        # A recurring task from an earlier date is shown as a copy moved onto
        # `day` (same id, same pet) so overlap checks use the right clock time.
        todays = []
        for t in self.owner.get_all_tasks():
            if t.completed or not t.occurs_on(day):
                continue
            if t.due_time.date() != day:
                t = replace(
                    t,
                    due_time=datetime.combine(day, t.due_time.time()),
                    source=t,
                )
            todays.append(t)

        # CHANGE (#3): must-do tasks (medication, vet) are scheduled first.
        ordered = sorted(
            todays, key=lambda t: (not t.is_must_do, -t.priority, t.due_time)
        )
        for task in ordered:
            over = plan.total_minutes + task.duration_minutes > budget
            if over and not task.is_must_do:
                plan.skipped.append(SkippedTask(task, "not enough time left in the day"))
                continue
            clash = next((t for t in plan.scheduled if task.overlaps(t)), None)
            if clash is not None:
                # CHANGE (#1): offer the next free slot instead of just dropping it.
                slot = None if over else self.find_next_free_slot(task, plan.scheduled)
                plan.skipped.append(
                    SkippedTask(task, f"overlaps with '{clash.title}'", slot)
                )
                continue
            if over:
                plan.over_budget = True
            plan.scheduled.append(task)
            plan.total_minutes += task.duration_minutes

        plan.scheduled = self.sort_by_time(plan.scheduled)
        self.last_plan = plan
        return plan

    def find_next_free_slot(
        self, task: Task, scheduled: List[Task]
    ) -> Optional[datetime]:
        """Return the earliest start at/after task.due_time that fits, or None.

        Algorithm: walk `scheduled` in time order with a candidate start
        beginning at task.due_time. If the task fits entirely before the
        next scheduled task, stop; otherwise, if that task ends after the
        candidate, push the candidate to its end time.

        Args:
            task: The task needing a slot (its duration is used).
            scheduled: Tasks already occupying time.

        Returns:
            The candidate start, or None if the task would run past midnight.
        """
        # CHANGE (#1): walk the scheduled tasks in time order, pushing the
        # candidate start past any task it would collide with.
        candidate = task.due_time
        length = timedelta(minutes=task.duration_minutes)
        for t in self.sort_by_time(scheduled):
            if candidate + length <= t.due_time:
                break  # fits in the gap before t
            if t.end_time > candidate:
                candidate = t.end_time
        midnight = datetime.combine(candidate.date() + timedelta(days=1), time.min)
        return candidate if candidate + length <= midnight else None

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Return tasks sorted by due time, ties broken by priority (highest first).

        Args:
            tasks: Tasks to sort; defaults to all of the owner's tasks.

        Returns:
            A new sorted list; the input is not modified.
        """
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        # CHANGE: tasks with the same due_time are ordered by priority so the
        # result is predictable instead of depending on insertion order.
        return sorted(tasks, key=lambda t: (t.due_time, -t.priority))

    def filter_tasks(
        self,
        completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
        tasks: Optional[List[Task]] = None,
    ) -> List[Task]:
        """Return tasks matching completion status and/or pet name (None = any).

        Both filters are combined with AND. Pet names are compared
        case-insensitively and ignore surrounding whitespace; tasks with no
        pet never match a pet_name filter.

        Args:
            completed: True for done tasks, False for open ones, None for both.
            pet_name: Pet name to match, or None for any pet.
            tasks: Tasks to filter; defaults to all of the owner's tasks.
        """
        # CHANGE: new filter; pet names match case-insensitively, and both
        # filters can be combined.
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        wanted = pet_name.strip().lower() if pet_name is not None else None
        return [
            t for t in tasks
            if (completed is None or t.completed == completed)
            and (wanted is None or (t.pet is not None and t.pet.name.lower() == wanted))
        ]

    def sort_by_priority(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Return tasks sorted by priority (highest first), ties by time."""
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        return sorted(tasks, key=lambda t: (-t.priority, t.due_time))

    def detect_conflicts(self, tasks: Optional[List[Task]] = None) -> List[Tuple[Task, Task]]:
        """Return pairs of tasks whose time windows overlap.

        Algorithm: sort by time, then sweep once while tracking the task
        that ends latest so far. Each task that starts before that task
        ends is reported as a conflict with it. Completed tasks are not
        excluded, and a task is only paired with the latest-ending earlier
        task, so a long task overlapping several others pairs with each
        later task but not every pair is listed.

        Args:
            tasks: Tasks to check; defaults to all of the owner's tasks.

        Returns:
            (earlier_task, later_task) tuples in time order.
        """
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
        if plan.over_budget:
            lines.append("Note: medication/vet tasks exceed your available time.")
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
                hint = f" (free at {s.suggested_time:%H:%M})" if s.suggested_time else ""
                lines.append(f"  {label(s.task)} - {s.reason}{hint}")
        return "\n".join(lines)
