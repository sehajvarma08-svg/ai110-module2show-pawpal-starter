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

    mochi.add_task(Task("Morning walk", TaskType.WALK, at(8, 0), 30, Priority.HIGH, Recurrence.DAILY))
    mochi.add_task(Task("Grooming", TaskType.GROOMING, at(16, 0), 45, Priority.LOW))
    kit.add_task(Task("Breakfast", TaskType.FEEDING, at(8, 15), 15, Priority.HIGH, Recurrence.DAILY))
    kit.add_task(Task("Medication", TaskType.MEDICATION, at(12, 30), 10, Priority.MEDIUM))

    scheduler = Scheduler(owner)
    plan = scheduler.build_daily_plan()

    print("=" * 40)
    print(f"Today's Schedule for {owner.name}")
    print("=" * 40)
    print(scheduler.explain_plan(plan))

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        print("\nHeads up - overlapping tasks:")
        for a, b in conflicts:
            print(f"  {a.title} ({a.pet.name}) overlaps {b.title} ({b.pet.name})")


if __name__ == "__main__":
    main()
