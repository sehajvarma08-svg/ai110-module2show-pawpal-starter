# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

Sample Output: 
Plan for Sunday, Oct 18: 85 of 120 available minutes used.
Scheduled (highest priority first got the time):
  08:00-08:30  Morning walk (Mochi) [high priority]
  12:30-12:40  Medication (Kit) [medium priority]
  16:00-16:45  Grooming (Mochi) [low priority]
Skipped:
  Breakfast (Kit) - overlaps with 'Morning walk'

Heads up - overlapping tasks:
  Morning walk (Mochi) overlaps Breakfast (Kit)

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:
========================================
Today's Schedule for Sam
========================================
Plan for Sunday, Oct 18: 85 of 120 available minutes used.
Scheduled (highest priority first got the time):
  08:00-08:30  Morning walk (Mochi) [high priority]
  12:30-12:40  Medication (Kit) [medium priority]
  16:00-16:45  Grooming (Mochi) [low priority]
Skipped:
  Breakfast (Kit) - overlaps with 'Morning walk'

Heads up - overlapping tasks:
  Morning walk (Mochi) overlaps Breakfast (Kit)

```
# Paste your pytest output here
```
Requirement already satisfied: pytest in ./.venv/lib/python3.13/site-packages (9.1.1)
Requirement already satisfied: iniconfig>=1.0.1 in ./.venv/lib/python3.13/site-packages (from pytest) (2.3.1)
Requirement already satisfied: packaging>=22 in ./.venv/lib/python3.13/site-packages (from pytest) (26.3)
Requirement already satisfied: pluggy<2,>=1.5 in ./.venv/lib/python3.13/site-packages (from pytest) (1.7.0)
Requirement already satisfied: pygments>=2.7.2 in ./.venv/lib/python3.13/site-packages (from pytest) (2.21.0)
(.venv) sehajvarma@Mac ai110-module2show-pawpal-starter % python -m pytest
============================================================ test session starts =============================================================
platform darwin -- Python 3.13.7, pytest-9.1.1, pluggy-1.7.0
rootdir: /Users/sehajvarma/Desktop/ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 2 items                                                                                                                            

test/test_pawpal.py ..                                                                                                                 [100%]

============================================================= 2 passed in 0.01s ==============================================================
(.venv) sehajvarma@Mac ai110-module2show-pawpal-starter % 

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

The walkthrough follows the CLI demo in `main.py` (run it with `python main.py`).

1. **Create an owner.** Sam is set up with 120 available minutes per day.
2. **Add pets.** Two pets, Mochi (dog) and Kit (cat), are attached to the owner.
3. **Add tasks to each pet.** Each task has a type, start time, duration, priority, and optional daily/weekly recurrence:
   - Mochi: Morning walk (08:00, 30 min, high, daily) and Grooming (16:00, 45 min, low)
   - Kit: Breakfast (08:15, 15 min, high, daily) and Medication (12:30, 10 min, medium)
4. **Build the daily plan.** The `Scheduler` takes today's incomplete tasks, sorts them by priority (ties broken by time), and adds them one at a time. A task is skipped if it would exceed the time budget or overlap a task already scheduled.
5. **Read the explanation.** The plan lists each scheduled task with its time window, pet, and priority, then lists skipped tasks with the reason. Here, Breakfast is skipped because it overlaps the Morning walk.
6. **Check for conflicts.** The scheduler also reports every pair of overlapping tasks across all pets, so the owner can reschedule them.
7. **Complete a task.** Calling `mark_complete()` marks the task done. For a recurring task, it also adds the next occurrence to the pet.
8. **Verify with tests.** Run `python -m pytest` to check that completing a task changes its status and that adding a task increases the pet's task count.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
