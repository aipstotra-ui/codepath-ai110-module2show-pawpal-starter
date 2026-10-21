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
