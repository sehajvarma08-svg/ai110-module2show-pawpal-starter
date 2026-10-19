from datetime import date, datetime, time

from pawpal_system import (
    Owner,
    Pet,
    Priority,
    Recurrence,
    Scheduler,
    Task,
    TaskType,
)


def at(hour: int, minute: int = 0) -> datetime:
    """Return today's date at the given time."""
    return datetime.combine(date.today(), time(hour, minute))


def main() -> None:
    owner = Owner(name="Sam", email="abcd@gmail.com", available_minutes_per_day=120)

    mochi = Pet(name="Mochi", species="dog", age=3)
    kit = Pet(name="Kit", species="cat", age=2)
    owner.add_pet(mochi)
    owner.add_pet(kit)


    # Tasks are added deliberately OUT of time order (and across pets) so the
    # sorting and filtering output below proves those methods work.
    kit.add_task(Task("Medication", TaskType.MEDICATION, at(12, 30), 10, Priority.MEDIUM))
    mochi.add_task(Task("Grooming", TaskType.GROOMING, at(16, 0), 45, Priority.LOW))
    mochi.add_task(Task("Evening walk", TaskType.WALK, at(18, 0), 30, Priority.MEDIUM))
    kit.add_task(Task("Breakfast", TaskType.FEEDING, at(8, 15), 15, Priority.HIGH, Recurrence.DAILY))
    # Same due time as Breakfast but lower priority: tests the tie-break.
    mochi.add_task(Task("Quick cuddle", TaskType.OTHER, at(8, 15), 5, Priority.LOW))
    mochi.add_task(Task("Morning walk", TaskType.WALK, at(8, 0), 30, Priority.HIGH, Recurrence.DAILY))

    # Complete one task so the completion filter has something to find.
    # (Daily recurrence also adds tomorrow's walk, which won't be in today's plan.)
    mochi.tasks[-1].mark_complete()

    scheduler = Scheduler(owner)
    plan = scheduler.build_daily_plan()

    #2. this right here feels simple too i guess
    print("=" * 40)
    print(f"Today's Schedule for {owner.name}")
    print("=" * 40)
    print(scheduler.explain_plan(plan))

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        print("\nHeads up - overlapping tasks:")
        for a, b in conflicts:
            print(f"  {a.title} ({a.pet.name}) overlaps {b.title} ({b.pet.name})")

    def show(title: str, tasks) -> None:
        print(f"\n{title}")
        for t in tasks:
            status = "done" if t.completed else "todo"
            print(f"  {t.due_time:%m-%d %H:%M}  {t.title:<14} {t.pet.name:<6} "
                  f"{t.priority.name.lower():<6} {status}")

    print("\n" + "=" * 40)
    print("Sorting & filtering checks")
    print("=" * 40)
    show("In insertion order (unsorted):", owner.get_all_tasks())
    show("sort_by_time (ties -> higher priority first):", scheduler.sort_by_time())
    show("filter_tasks(completed=True):", scheduler.filter_tasks(completed=True))
    show("filter_tasks(completed=False):", scheduler.filter_tasks(completed=False))
    show("filter_tasks(pet_name='kit'):", scheduler.filter_tasks(pet_name="kit"))
    show(
        "Mochi's open tasks, sorted by time:",
        scheduler.sort_by_time(scheduler.filter_tasks(completed=False, pet_name="Mochi")),
    )

if __name__ == "__main__":
    main()
