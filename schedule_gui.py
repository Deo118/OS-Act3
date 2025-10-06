import customtkinter as ctk
from tkinter import messagebox
from collections import deque
import random

# ---------------- Process Class ----------------
class Process:
    def __init__(self, pid, at, bt, priority=0):
        self.pid = pid # process ID 
        self.at = at # arrival time
        self.bt = bt # burst time
        self.priority = priority # priority value 
        self.wt = 0 # waiting time 
        self.tat = 0 # turnaround time 

# ---------------- CPU Scheduling Functions ----------------

# First Come First Serve
def fcfs(processes):
    processes.sort(key=lambda x: x.at)   # Sort processes by arrival time
    time, order, timeline = 0, [], []
    for p in processes:
        if time < p.at:   # If CPU is idle, jump to process arrival time
            time = p.at
        start = time                    # Start time of process
        p.wt = time - p.at              # Waiting time = start time - arrival
        time += p.bt                    # Advance time by burst
        finish = time                   # Finish time of process
        p.tat = p.wt + p.bt             # Turnaround = waiting + burst
        order.append(p.pid)             # Record execution order
        timeline.append((p.pid, start, finish))
    return order, timeline

# Shortest Job First (Non-preemptive)
def sjf(processes):
    processes.sort(key=lambda x: (x.at, x.bt))  # Sort by arrival, then burst
    n, completed, time, order, timeline = len(processes), 0, 0, [], []
    done = [False]*n
    while completed < n:
        # Collect ready processes (arrived and not done)
        ready = [i for i, p in enumerate(processes) if p.at <= time and not done[i]]
        if ready:
            # Choose the one with smallest burst time
            idx = min(ready, key=lambda i: processes[i].bt)
            p = processes[idx]
            start = time
            p.wt = time - p.at
            time += p.bt
            finish = time
            p.tat = p.wt + p.bt
            done[idx] = True
            completed += 1
            order.append(p.pid)
            timeline.append((p.pid, start, finish))
        else:
            time += 1  # CPU idle, move forward
    return order, timeline

# SJF Preemptive 
def sjf_preemptive(processes):
    n, time, completed = len(processes), 0, 0
    remaining = [p.bt for p in processes]
    timeline, last_pid, start_time = [], None, 0
    while completed < n:
        ready = [i for i, p in enumerate(processes) if p.at <= time and remaining[i] > 0]
        if ready:
            idx = min(ready, key=lambda i: remaining[i])
            p = processes[idx]
            if last_pid != p.pid:
                if last_pid is not None:
                    timeline.append((last_pid, start_time, time))
                start_time, last_pid = time, p.pid
            remaining[idx] -= 1
            time += 1
            if remaining[idx] == 0:
                completed += 1
                p.tat = time - p.at
                p.wt = p.tat - p.bt
        else:
            time += 1
    timeline.append((last_pid, start_time, time))
    return [pid for pid, _, _ in timeline], timeline

# Priority Scheduling (Non-preemptive)
def priority_scheduling(processes):
    n, completed, time, order, timeline = len(processes), 0, 0, [], []
    done = [False]*n
    while completed < n:
        # Collect ready processes
        ready = [i for i, p in enumerate(processes) if p.at <= time and not done[i]]
        if ready:
            # Choose process with smallest priority value 
            idx = min(ready, key=lambda i: processes[i].priority)
            p = processes[idx]
            start = time
            p.wt = time - p.at
            time += p.bt
            finish = time
            p.tat = p.wt + p.bt
            done[idx] = True
            completed += 1
            order.append(p.pid)
            timeline.append((p.pid, start, finish))
        else:
            time += 1  # CPU idle
    return order, timeline

# Priority Preemptive
def priority_preemptive(processes):
    n, time, completed = len(processes), 0, 0
    remaining = [p.bt for p in processes]
    timeline, last_pid, start_time = [], None, 0
    while completed < n:
        ready = [i for i, p in enumerate(processes) if p.at <= time and remaining[i] > 0]
        if ready:
            idx = min(ready, key=lambda i: processes[i].priority)
            p = processes[idx]
            if last_pid != p.pid:
                if last_pid is not None:
                    timeline.append((last_pid, start_time, time))
                start_time, last_pid = time, p.pid
            remaining[idx] -= 1
            time += 1
            if remaining[idx] == 0:
                completed += 1
                p.tat = time - p.at
                p.wt = p.tat - p.bt
        else:
            time += 1
    timeline.append((last_pid, start_time, time))
    return [pid for pid, _, _ in timeline], timeline

# Round Robin Scheduling
def round_robin(processes, quantum):
    n, time, order, timeline = len(processes), 0, [], []
    queue = deque()                       # Ready queue
    remaining_bt = [p.bt for p in processes]  # Remaining burst times
    tat, wt, completed = [0]*n, [0]*n, [False]*n
    processes.sort(key=lambda x: x.at)    # Sort by arrival time

    # Load initial processes that have arrived at time 0
    i = 0
    while i < n and processes[i].at <= time:
        queue.append(i); i += 1

    while queue:
        idx = queue.popleft()
        p = processes[idx]
        order.append(p.pid)   # Record execution order
        start = time          

        if remaining_bt[idx] > quantum:   # If needs more than quantum
            time += quantum
            remaining_bt[idx] -= quantum
            finish = time         
        else:                             # If finishes within quantum
            time += remaining_bt[idx]
            finish = time 
            tat[idx] = time - p.at        # Turnaround time
            wt[idx] = tat[idx] - p.bt     # Waiting time
            remaining_bt[idx] = 0
            completed[idx] = True
        
        timeline.append((p.pid, start, finish)) # record slice in gantt chart

        # Add new arrivals that came during this time
        while i < n and processes[i].at <= time:
            queue.append(i); i += 1

        # If process not finished, put it back in queue
        if not completed[idx]:
            queue.append(idx)

        # If queue empty but there are still processes left, jump to next arrival
        if not queue and i < n:
            time = processes[i].at
            queue.append(i); i += 1

    # Save calculated WT and TAT back into process objects
    for j in range(n):
        processes[j].wt, processes[j].tat = wt[j], tat[j]

    return order, timeline

# ---------------- Animation Functions ----------------

#Animate auto generated entries
def animate_entry(entry, final_value, delay=50, steps=10, min_val=0, max_val=15):
    def step(count):
        if count > 0:
            entry.delete(0, "end")
            entry.insert(0, str(random.randint(min_val, max_val)))
            entry.after(delay, step, count -1)
        else:
            entry.delete(0, "end")
            entry.insert(0, str(final_value))
    step(steps)

# ---------------- Run Algorithm and Output Functions ----------------

# Run the selected scheduling algorithm
def run_algorithm():
    algo = algo_choice.get()
    try:
        n = int(entry_n.get())
    except:
        messagebox.showerror("Error", "Enter a valid number of processes")
        return

    processes = []
    for i in range(n):
        try:
            at = int(entries[i][0].get())
            bt = int(entries[i][1].get())
            pr = int(entries[i][2].get()) if "Priority" in algo else 0
            processes.append(Process(f"P{i + 1}", at, bt, pr))
        except:
            messagebox.showerror("Error", f"Invalid input in Process {i + 1}")
            return

    # Run chosen algorithm
    if algo.startswith("FCFS"):
        order, timeline = fcfs(processes)
    elif algo.startswith("SJF") and "Non" in algo:
        order, timeline = sjf(processes)
    elif algo.startswith("SJF") and "Preemptive" in algo:
        order, timeline = sjf_preemptive(processes)
    elif algo.startswith("Priority") and "Non" in algo:
        order, timeline = priority_scheduling(processes)
    elif algo.startswith("Priority") and "Preemptive" in algo:
        order, timeline = priority_preemptive(processes)
    elif algo.startswith("Round Robin"):
        try:
            q = int(entry_q.get())
            order, timeline = round_robin(processes, q)
        except:
            messagebox.showerror("Error", "Enter a valid quantum")
            return

    avg_wt = sum(p.wt for p in processes) / n
    avg_tat = sum(p.tat for p in processes) / n

    # Hide input window
    root.withdraw()

    # Create output window
    output_win = ctk.CTkToplevel()
    output_win.title("Simulation Results")
    center_window(output_win, 800, 600)

    ctk.CTkLabel(output_win, text="OUTPUT", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

    result_text = ctk.CTkTextbox(output_win, width=760, height=450, wrap="none")
    result_text.pack(padx=10, pady=10, fill="both", expand=True)
    result_text.configure(font=("Courier New", 14))

    #Gantt Chart 
    result_text.insert("end", "Gantt Chart:\n")

    label_timeline = "Process Timeline:"
    label_finish   = "Finish Times:"
    pad = max(len(label_timeline), len(label_finish))
    label_timeline = label_timeline.ljust(pad)
    label_finish   = label_finish.ljust(pad)

    segments = [f"| {pid} " for pid, _, _ in timeline]
    widths = [len(seg) for seg in segments]

    # Top row
    result_text.insert("end", label_timeline + "  ")
    for seg in segments:
        result_text.insert("end", seg)
    result_text.insert("end", "|\n")

    # Bottom row 
    result_text.insert("end", label_finish + "  ")
    for (pid, s, f), w in zip(timeline, widths):
        result_text.insert("end", str(s).ljust(w))  
    result_text.insert("end", str(timeline[-1][2]) + "\n\n")

    # Process Table 
    header = f"{'Process':<10}{'AT':<10}{'BT':<10}{'WT':<10}{'TAT':<10}\n"
    result_text.insert("end", header)
    result_text.insert("end", "-" * 50 + "\n")
    for p in processes:
        row = f"{p.pid:<10}{p.at:<10}{p.bt:<10}{p.wt:<10}{p.tat:<10}\n"
        result_text.insert("end", row)

    result_text.insert("end", f"\nAverage Waiting Time = {avg_wt:.2f}\n")
    result_text.insert("end", f"Average Turnaround Time = {avg_tat:.2f}\n")
    result_text.configure(state="disabled")

    # Back button
    def back_to_input():
        output_win.destroy()
        root.deiconify()

    ctk.CTkButton(output_win, text="Back to Input", command=back_to_input).pack(pady=15)


# ---------------- Entry Field Creation Functions ----------------

# Create entry fields for process input
def create_entries():
    for widget in frame_inputs.winfo_children():
        widget.destroy()
    try:
        n = int(entry_n.get())
    except:
        return
    global entries
    entries = []
    for i in range(n):
        ctk.CTkLabel(frame_inputs, text=f"P{i + 1} Arrival Time:").grid(row=i, column=0, padx=5, pady=2)
        at_entry = ctk.CTkEntry(frame_inputs, width=60, justify="center")
        at_entry.grid(row=i, column=1, padx=5)
        ctk.CTkLabel(frame_inputs, text="Burst Time:").grid(row=i, column=2, padx=5)
        bt_entry = ctk.CTkEntry(frame_inputs, width=60, justify="center")
        bt_entry.grid(row=i, column=3, padx=5)
        if algo_choice.get() == "Priority":
            ctk.CTkLabel(frame_inputs, text="Priority:").grid(row=i, column=4, padx=5)
            pr_entry = ctk.CTkEntry(frame_inputs, width=60, justify="center")
            pr_entry.grid(row=i, column=5, padx=5)
        else:
            pr_entry = ctk.CTkEntry(frame_inputs, width=60, justify="center")
        entries.append((at_entry, bt_entry, pr_entry))

# Auto-generate random process data
def auto_generate():
    try:
        n = int(entry_n.get())
    except:
        messagebox.showerror("Error", "Enter a valid number of processes first")
        return
    if not entries or len(entries) != n:
        create_entries()

    for i in range(n):
        at = random.randint(0, 15)
        bt = random.randint(1, 15)
        animate_entry(entries[i][0], at, min_val=0, max_val=15)
        animate_entry(entries[i][1], bt, min_val=1, max_val=15)
        if algo_choice.get() == "Priority":
            pr = random.randint(1, 5)
            animate_entry(entries[i][2], pr, min_val=1, max_val=5)

# ---------------- Utility Functions ----------------

# Center the main window on the screen
def center_window(root, width=1200, height=700):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")

# Show quantum input field only when RR is selected
def show_hide_quantum(choice):
    if choice == "Round Robin":
        quantum_frame.grid()
    else:
        quantum_frame.grid_remove()
    create_entries()

# ---------------- Main Window ----------------

def main():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    global algo_choice, entry_n, entry_q, frame_inputs, quantum_frame, entries, root

    root = ctk.CTk()
    root.title("CPU Scheduling Simulator")
    center_window(root, 600, 700)
    root.resizable(False, False)

    # Press Enter to run simulation
    root.bind("<Return>", lambda event: run_algorithm())

    # Left frame (input side)
    left_frame = ctk.CTkFrame(root)
    left_frame.pack(fill="both", padx=20, pady=20, expand=True, side="left")

    # Controls frame
    controls_frame = ctk.CTkFrame(left_frame)
    controls_frame.pack(pady=10, anchor="center")

    # Algorithm choice
    ctk.CTkLabel(controls_frame, text="Choose Algorithm:").grid(row=0, column=0, padx=45, pady=(0, 5))
    algo_choice = ctk.CTkOptionMenu(
        controls_frame,
        values=[
            "FCFS (First-Come-First-Serve)",
            "SJF (Non-Preemptive)", "SJF (Preemptive)",
            "Priority (Non-Preemptive)", "Priority (Preemptive)",
            "Round Robin"
        ],
        command=show_hide_quantum,
        width=140
    )
    algo_choice.grid(row=1, column=0, padx=10, pady=(0, 10))
    algo_choice.set("FCFS")
    ctk.CTkButton(controls_frame, text="Auto Generate", command=auto_generate, width=140).grid(row=2, column=0, padx=10, pady=(0, 10))

    # Number of processes
    ctk.CTkLabel(controls_frame, text="Number of Processes:").grid(row=0, column=1, padx=45, pady=(0, 5))
    entry_n = ctk.CTkEntry(controls_frame, width=140, justify="center")
    entry_n.grid(row=1, column=1, padx=10, pady=(0, 5))
    ctk.CTkButton(controls_frame, text="Set Processes", command=create_entries, width=140).grid(row=2, column=1, padx=10, pady=(0, 10))

    # Quantum (hidden unless Round Robin is selected)
    quantum_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
    ctk.CTkLabel(quantum_frame, text="Quantum (for RR):").pack(pady=(0, 5))
    entry_q = ctk.CTkEntry(quantum_frame, width=140, justify="center")
    entry_q.pack()
    quantum_frame.grid(row=0, column=2, rowspan=3, padx=10, pady=5)
    quantum_frame.grid_remove()

    # Scrollable frame for process inputs
    frame_inputs = ctk.CTkScrollableFrame(left_frame, width=580, height=300)
    frame_inputs.pack(pady=10, padx=10, fill="both", expand=True)

    # Run button
    btn_run = ctk.CTkButton(left_frame, text="Run Simulation", command=run_algorithm)
    btn_run.pack(pady=10, anchor="center")

    root.mainloop()


if __name__ == "__main__":
    main()