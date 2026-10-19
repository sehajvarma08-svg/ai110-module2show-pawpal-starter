import streamlit as st

from datetime import datetime

from pawpal_system import Owner, Pet, Priority, Recurrence, Scheduler, Task, TaskType

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input(
    "Available minutes per day", min_value=15, max_value=1440, value=120, step=15
)

# Create the Owner once per session; later re-runs reuse the stored object
if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        name=owner_name, email="", available_minutes_per_day=int(available_minutes)
    )
owner = st.session_state.owner
owner.name = owner_name
owner.available_minutes_per_day = int(available_minutes)

st.divider()

st.subheader("Add a Pet")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    pet_age = st.number_input("Age", min_value=0, max_value=50, value=2)

if st.button("Add pet"):
    if any(p.name.lower() == pet_name.strip().lower() for p in owner.pets):
        st.warning(f"{pet_name} is already added.")
    elif not pet_name.strip():
        st.warning("Please enter a pet name.")
    else:
        owner.add_pet(Pet(name=pet_name.strip(), species=species, age=int(pet_age)))
        st.success(f"Added {pet_name}.")

if owner.pets:
    st.write("Pets:")
    st.table(
        [{"name": p.name, "species": p.species, "age": p.age, "tasks": len(p.tasks)}
         for p in owner.pets]
    )
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Schedule a Task")
if not owner.pets:
    st.info("Add a pet first, then you can schedule tasks for it.")
else:
    selected_pet_name = st.selectbox("For which pet?", [p.name for p in owner.pets])
    col1, col2 = st.columns(2)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
        task_type = st.selectbox(
            "Type", list(TaskType), format_func=lambda t: t.value.capitalize()
        )
        due_date = st.date_input("Due date")
        due_clock = st.time_input("Due time", value=datetime.now().replace(minute=0).time())
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox(
            "Priority", list(Priority), index=2, format_func=lambda p: p.name.capitalize()
        )
        recurrence = st.selectbox(
            "Repeats", list(Recurrence), format_func=lambda r: r.value.capitalize()
        )

    if st.button("Add task"):
        pet = next(p for p in owner.pets if p.name == selected_pet_name)
        pet.add_task(
            Task(
                title=task_title,
                task_type=task_type,
                due_time=datetime.combine(due_date, due_clock),
                duration_minutes=int(duration),
                priority=priority,
                recurrence=recurrence,
            )
        )
        st.success(f"Added '{task_title}' for {pet.name}.")

scheduler = Scheduler(owner)

all_tasks = scheduler.sort_by_time()
if all_tasks:
    st.write("Current tasks (by time):")
    st.table(
        [
            {
                "pet": t.pet.name if t.pet else "",
                "title": t.title,
                "type": t.task_type.value,
                "due": f"{t.due_time:%Y-%m-%d %H:%M}",
                "minutes": t.duration_minutes,
                "priority": t.priority.name.lower(),
                "repeats": t.recurrence.value,
            }
            for t in all_tasks
        ]
    )
    for a, b in scheduler.detect_conflicts():
        st.warning(f"Conflict: '{a.title}' overlaps with '{b.title}'.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
plan_day = st.date_input("Plan for day", key="plan_day")

if st.button("Generate schedule"):
    plan = scheduler.build_daily_plan(plan_day)
    st.text(scheduler.explain_plan(plan))
