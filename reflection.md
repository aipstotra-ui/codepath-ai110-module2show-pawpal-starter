# PawPal+ Reflection

## 1. System Design

### 1a. Initial design

My first step was figuring out what a pet owner actually needs to do in the app. I settled on three core actions:

1. **Add a pet** to the owner's profile (name and species).
2. **Schedule a task** (feeding, walk, medication, appointment) for one of those pets at a certain time, once or repeating.
3. **See today's schedule** across all pets, in time order, with a warning if two things collide.

From those I picked four classes:

- **Task** (dataclass): one activity. It holds a description, a time, a frequency and a completed flag, and it can mark itself complete.
- **Pet** (dataclass): holds the pet's name and species plus its own list of tasks.
- **Owner**: holds the pets and exposes one method that returns every pet's tasks together, so nothing else has to dig through pets by hand.
- **Scheduler**: the "brain". It takes an Owner and does the organizing: today's schedule, sorting and conflict checks. It never stores tasks itself, it only reads them through the Owner.

I used dataclasses for Task and Pet because they are mostly data, and kept Scheduler as a normal class because it is mostly behavior.

### 1b. Design changes

After I wrote the skeleton I asked my AI assistant to review it for missing relationships. It pointed out three things, and I made all three changes:

1. **Tasks had no due date.** With only "HH:MM" I couldn't say *which day* a task was for, and recurring tasks need a date to move forward. I added `due_date` to `Task`.
2. **A task didn't know which pet it belonged to.** The scheduler gets a flat list from `Owner.get_all_tasks()`, so a task in that list couldn't be shown with its pet's name or added back to the right pet after recurring. `Pet.add_task` now stamps `pet_name` on the task.
3. **The scheduler needed to be the one completing tasks.** Completing a recurring task has to create a new task on the pet, which `Task` alone can't do, so I added `Scheduler.mark_task_complete` and kept `Task.next_occurrence` as a small helper.

I also added `Owner.get_pet(name)` so the UI and scheduler don't loop over pets by hand.

## 2. Scheduling Logic

### 2a. Constraints and priorities

The scheduler considers date, time, completion status, and frequency. Time matters most, since a schedule is mainly "what happens when", then completion (done tasks drop out of today's view), then recurrence. I did not add task priority levels because for a first version I decided a clean time-ordered plan was more useful than a weighting system.

### 2b. Tradeoffs

The conflict detector only flags tasks at the **exact same date and time**. It does not know that a 30-minute walk at 08:00 overlaps a feeding at 08:15. I kept it that way because tasks don't have a duration, and adding durations would complicate the form, the data model and the tests. For a pet owner's daily routine, an exact-match warning catches the most obvious double-booking and is easy to read and verify. The cost is that it can miss real overlaps.

A second smaller tradeoff: I compare "HH:MM" strings instead of parsing them into `time` objects. This works because the format is zero-padded and fixed width, and it keeps the sort a one-line `lambda`, but it relies on the UI always producing that format.

## 3. AI Collaboration

### 3a. How I used AI

I used my AI coding assistant for brainstorming the four classes and the Mermaid diagram, generating the skeleton and then the full implementation, drafting tests, and reviewing my skeleton for gaps. The most effective features were agent mode editing several files at once (for example when recurrence touched both `Task` and `Scheduler`) and asking for a review of code I had already written, which is what surfaced the missing `due_date` and `pet_name`.

### 3b. Judgment and verification

One suggestion I simplified: it is tempting to store tasks in both the `Pet` and a separate list on the `Scheduler`. I kept a single source of truth (each `Pet` owns its tasks, and the `Scheduler` reads through `Owner.get_all_tasks()`) so the two lists can never drift apart. I also kept the conflict check as a plain loop that groups tasks into a dictionary instead of a more compact nested comprehension, because I can read the loop and explain it.

I verified everything by running `python main.py` and reading the output, by the pytest suite, and by driving the Streamlit app with Streamlit's `AppTest` to confirm that adding a pet, adding two same-time tasks and completing a task all work and the conflict warning appears.

### 3c. Separate chat sessions

Treating each phase as its own piece of work (design, core, algorithms, tests, UI) kept my context small: when I was working on tests I only had to think about behavior, not layout. My commit history follows the same phases, which also makes it easy to see what changed when.

## 4. Testing and Verification

### 4a. What I tested

I tested the behaviors that would hurt most if wrong: chronological sorting, daily/weekly/one-off recurrence, conflict detection (same pet, different pets, and no false alarms for different times or completed tasks), filtering, and the empty-pet edge case. These matter because the whole point of the app is a trustworthy plan for the day.

### 4b. Confidence

I'm at about 4 out of 5. All 14 tests pass. With more time I would test tasks that cross midnight, weekly recurrence across month ends, invalid time strings, and duplicate pet names (right now `get_pet` returns the first match).

## 5. Reflection

### 5a. What went well

Building the logic layer first and proving it in the terminal made the Streamlit step almost trivial. The UI is a thin layer over methods that were already tested.

### 5b. What I would improve

I would add task durations and overlap-based conflict detection, priorities, and saving to JSON so data survives a restart. Right now closing the app loses everything.

### 5c. Lead architect takeaway

The AI is quick at producing code, but it doesn't decide what the system should be. I had to choose the classes, the single source of truth for tasks, and which tradeoffs were acceptable (exact-match conflicts, no priorities). The most useful habit was asking the AI to review my design before building more on top of it, and then deciding for myself which feedback to accept.
