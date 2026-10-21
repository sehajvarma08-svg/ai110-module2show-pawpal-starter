import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import Pet, Task, TaskType


def make_task() -> Task:
    return Task(
        title="Morning walk",
        task_type=TaskType.WALK,
        due_time=datetime(2026, 1, 1, 8, 0),
        duration_minutes=30,
    )


def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="Dog", age=3)
    assert len(pet.get_tasks()) == 0

    pet.add_task(make_task())

    assert len(pet.get_tasks()) == 1

#added Test after making logical changes

from datetime import date, timedelta

from pawpal_system import Owner, Priority, Recurrence, Scheduler


def _setup(minutes=120):
    owner = Owner("Sam", "s@x.com", minutes)
    pet = Pet("Mochi", "dog", 3)
    owner.add_pet(pet)
    return owner, pet, Scheduler(owner)


def test_mark_complete_twice_creates_one_next_occurrence():
    pet = Pet("Mochi", "dog", 3)
    t = make_task()
    t.recurrence = Recurrence.DAILY
    pet.add_task(t)
    t.mark_complete()
    assert t.mark_complete() is None
    assert len(pet.tasks) == 2


def test_daily_task_appears_on_future_day():
    owner, pet, sched = _setup()
    start = datetime.combine(date.today(), datetime.min.time()).replace(hour=8)
    pet.add_task(Task("Walk", TaskType.WALK, start, 30, recurrence=Recurrence.DAILY))
    plan = sched.build_daily_plan(date.today() + timedelta(days=3))
    assert len(plan.scheduled) == 1
    assert plan.scheduled[0].due_time.date() == date.today() + timedelta(days=3)


def test_overlap_skip_suggests_free_slot():
    owner, pet, sched = _setup()
    d = datetime.combine(date.today(), datetime.min.time())
    pet.add_task(Task("A", TaskType.WALK, d.replace(hour=8), 60, Priority.HIGH))
    pet.add_task(Task("B", TaskType.OTHER, d.replace(hour=8, minute=30), 30, Priority.LOW))
    plan = sched.build_daily_plan()
    assert plan.skipped[0].suggested_time == d.replace(hour=9)


def test_medication_ignores_time_budget():
    owner, pet, sched = _setup(minutes=10)
    d = datetime.combine(date.today(), datetime.min.time())
    pet.add_task(Task("Pill", TaskType.MEDICATION, d.replace(hour=9), 30, Priority.LOW))
    plan = sched.build_daily_plan()
    assert [t.title for t in plan.scheduled] == ["Pill"]
    assert plan.over_budget


def test_completing_projected_copy_completes_original_once():
    owner, pet, sched = _setup()
    start = datetime.combine(date.today(), datetime.min.time()).replace(hour=8)
    original = Task("Walk", TaskType.WALK, start, 30, recurrence=Recurrence.DAILY)
    pet.add_task(original)
    day = date.today() + timedelta(days=2)
    copy = sched.build_daily_plan(day).scheduled[0]
    nxt = copy.mark_complete()
    assert original.completed
    assert nxt.due_time == datetime.combine(day + timedelta(days=1), start.time())
    plan = sched.build_daily_plan(day + timedelta(days=1))
    assert len(plan.scheduled) == 1 and not plan.skipped


def test_late_completion_schedules_next_occurrence_in_future():
    pet = Pet("Mochi", "dog", 3)
    t = Task("Walk", TaskType.WALK, datetime(2026, 1, 1, 8), 30, recurrence=Recurrence.DAILY)
    pet.add_task(t)
    now = datetime(2026, 1, 5, 12)
    nxt = t.mark_complete(now=now)
    assert nxt.due_time == datetime(2026, 1, 6, 8)


def test_weekly_next_occurrence_is_one_week_later():
    pet = Pet("Mochi", "dog", 3)
    t = Task("Bath", TaskType.GROOMING, datetime(2026, 1, 1, 8), 30, recurrence=Recurrence.WEEKLY)
    pet.add_task(t)
    assert t.mark_complete(now=datetime(2026, 1, 1, 9)).due_time == datetime(2026, 1, 8, 8)
