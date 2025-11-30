from datetime import datetime, timedelta

# --- Configuration ---
DAY_START = datetime.strptime("08:00", "%H:%M")
DAY_END   = datetime.strptime("21:00", "%H:%M")
RESOLUTION = timedelta(minutes=30)
TITLE_WIDTH = 20

# --- Example tasks ---
# List of tuples: (start_datetime, end_datetime, title)
tasks = [
    (datetime.strptime("11:00", "%H:%M"), datetime.strptime("11:30", "%H:%M"), "Standup"),
    (datetime.strptime("11:15", "%H:%M"), datetime.strptime("12:00", "%H:%M"), "Dentist"),
    (datetime.strptime("15:00", "%H:%M"), datetime.strptime("16:00", "%H:%M"), "Deep Work"),
]

# --- Helper functions ---
def format_title(title):
    if len(title) > TITLE_WIDTH - 1:
        return title[:TITLE_WIDTH-1] + "…"
    return title.ljust(TITLE_WIDTH)

def generate_time_slots(start, end, resolution):
    slots = []
    current = start
    while current < end:
        slots.append(current)
        current += resolution
    return slots

def overlaps(slot_start, slot_end, task_start, task_end):
    return slot_start < task_end and task_start < slot_end

# --- Assign horizontal positions (stacking) ---
def assign_task_indices(slots, tasks):
    # For each slot, find which tasks occupy it
    slot_task_map = []
    ongoing_tasks = []
    for slot_start in slots:
        slot_end = slot_start + RESOLUTION
        occupying_tasks = []
        # Remove tasks that have ended
        ongoing_tasks = [t for t in ongoing_tasks if t[1] > slot_start]
        # Add new tasks starting before slot_end
        for idx, (s, e, t) in enumerate(tasks):
            if overlaps(slot_start, slot_end, s, e) and (s, e, t, idx) not in ongoing_tasks:
                ongoing_tasks.append((s, e, t, idx))
        # Determine horizontal positions
        positions = [None] * len(ongoing_tasks)
        for i, t in enumerate(ongoing_tasks):
            positions[i] = t
        slot_task_map.append(positions.copy())
    return slot_task_map

# --- Build planner ---
def build_planner(day_title, slots, slot_task_map):
    lines = [f"# {day_title}\n"]
    max_columns = max(len(slot) for slot in slot_task_map)
    
    for slot_start, slot_tasks in zip(slots, slot_task_map):
        slot_end = slot_start + RESOLUTION
        time_str = f"{slot_start.strftime('%H:%M')}–{slot_end.strftime('%H:%M')}"
        line = f"{time_str} |"
        
        for col in range(max_columns):
            if col < len(slot_tasks):
                s, e, title, idx = slot_tasks[col]
                if slot_start >= s and slot_end <= e:
                    # Full slot inside task
                    content = format_title(title)
                elif slot_start > s and slot_end <= e:
                    # Middle slot continuation
                    content = format_title("(…)")
                elif slot_start >= s and slot_start < e:
                    # Task ends mid-slot
                    content = format_title(f"{title} ({e.strftime('%H:%M')})")
                elif slot_end > s and slot_start < s:
                    # Task starts mid-slot
                    content = format_title(f"{title} ({s.strftime('%H:%M')})")
                else:
                    content = format_title("")
            else:
                content = format_title("")
            line += content + "|"
        lines.append(line)
    return "\n".join(lines)

# --- Main ---
slots = generate_time_slots(DAY_START, DAY_END, RESOLUTION)
slot_task_map = assign_task_indices(slots, tasks)
planner_md = build_planner("Sun 30 Nov", slots, slot_task_map)

with open("planner.md", "w") as f:
    f.write(planner_md)

print("planner.md generated!")
