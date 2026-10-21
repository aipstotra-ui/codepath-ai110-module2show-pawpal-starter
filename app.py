import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# Streamlit reruns this script on every click, so the Owner lives in session_state.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner = st.session_state.owner
scheduler = Scheduler(owner)

st.subheader("Add a pet")
with st.form("add_pet", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet") and pet_name.strip():
        owner.add_pet(Pet(pet_name.strip(), species))
        st.success(f"Added {pet_name.strip()}!")

st.subheader("Schedule a task")
if not owner.pets:
    st.info("Add a pet first.")
else:
    with st.form("add_task", clear_on_submit=True):
        target = st.selectbox("Pet", [p.name for p in owner.pets])
        desc = st.text_input("Task description")
        time = st.time_input("Time")
        freq = st.selectbox("Frequency", ["once", "daily", "weekly"])
        if st.form_submit_button("Add task") and desc.strip():
            owner.get_pet(target).add_task(
                Task(desc.strip(), time.strftime("%H:%M"), freq))
            st.success(f"Scheduled '{desc.strip()}' for {target}.")

st.subheader("Today's schedule")
conflicts = scheduler.detect_conflicts()
for warning in conflicts:
    st.warning(f"⚠️ {warning}. Consider moving one of these tasks.")

tasks = scheduler.get_todays_schedule()
if tasks:
    st.table([{"Time": t.time, "Pet": t.pet_name, "Task": t.description,
               "Repeats": t.frequency} for t in tasks])
    if not conflicts:
        st.success("No scheduling conflicts. You're all set!")
else:
    st.info("No tasks for today yet.")

st.subheader("Mark a task done")
pending = scheduler.sort_by_time(scheduler.filter_tasks(completed=False))
if pending:
    labels = {f"{t.due_date} {t.time} - {t.pet_name}: {t.description}": t for t in pending}
    choice = st.selectbox("Pending task", list(labels))
    if st.button("Mark complete"):
        nxt = scheduler.mark_task_complete(labels[choice])
        msg = "Task completed!"
        if nxt:
            msg += f" Next {nxt.frequency} occurrence scheduled for {nxt.due_date}."
        st.success(msg)
else:
    st.caption("Nothing pending.")

st.subheader("Browse all tasks")
col1, col2 = st.columns(2)
pet_filter = col1.selectbox("Pet", ["All"] + [p.name for p in owner.pets])
status_filter = col2.selectbox("Status", ["All", "Pending", "Completed"])
shown = scheduler.sort_by_time(scheduler.filter_tasks(
    pet_name=None if pet_filter == "All" else pet_filter,
    completed={"All": None, "Pending": False, "Completed": True}[status_filter]))
if shown:
    st.table([{"Date": str(t.due_date), "Time": t.time, "Pet": t.pet_name,
               "Task": t.description, "Repeats": t.frequency,
               "Done": "✅" if t.completed else "⬜"} for t in shown])
else:
    st.caption("No tasks match.")
