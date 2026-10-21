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
tasks = scheduler.get_todays_schedule()
if tasks:
    st.table([{"Time": t.time, "Pet": t.pet_name, "Task": t.description,
               "Repeats": t.frequency} for t in tasks])
else:
    st.info("No tasks for today yet.")
