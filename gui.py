import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque

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

# ---------------- GUI Functions ----------------

# Called when algorithm selection changes
# Shows quantum input only if Round Robin is selected
def on_algo_change(event):
    algo = algo_choice.get()
    if algo_choice.get() == "Round Robin":
        lbl_q.pack(before=btn_run)
        entry_q.pack(before=btn_run)
        lbl_mode.pack_forget()
        mode_choice.pack_forget()
    elif algo in ["SJF", "Priority"]:
        lbl_mode.pack(before=btn_run)
        mode_choice.pack(before=btn_run)
        lbl_q.pack_forget()
        entry_q.pack_forget()
    else:
        lbl_q.pack_forget()
        entry_q.pack_forget()
        lbl_mode.pack_forget()
        mode_choice.pack_forget()

# Run the selected scheduling algorithm
def run_algorithm():
    algo = algo_choice.get()
    try:
        n = int(entry_n.get())
    except:
        messagebox.showerror("Error", "Enter valid number of processes")
        return
    
    # Collect process inputs from entry fields
    processes = []
    for i in range(n):
        try:
            at = int(entries[i][0].get())
            bt = int(entries[i][1].get())
            if algo == "Priority":
                pr = int(entries[i][2].get())
            else:
                pr = 0
            processes.append(Process(f"P{i+1}", at, bt, pr))
        except:
            messagebox.showerror("Error", f"Invalid input in Process {i+1}")
            return
    
    # Run chosen algorithm
    if algo == "FCFS":
        order, timeline = fcfs(processes)
    elif algo == "SJF":
        if mode_choice.get() == "Non-preemptive":
            order, timeline = sjf(processes)
        else:
            order, timeline = sjf_preemptive(processes)
    elif algo == "Priority":
        if mode_choice.get() == "Non-preemptive":
            order, timeline = priority_scheduling(processes)
        else:
            order, timeline = priority_preemptive(processes)
    elif algo == "Round Robin":
        try:
            q = int(entry_q.get())
            order, timeline = round_robin(processes, q)
        except:
            messagebox.showerror("Error", "Enter valid quantum")
            return
    
    # Calculate averages
    avg_wt = sum(p.wt for p in processes) / n
    avg_tat = sum(p.tat for p in processes) / n
    
    # Display results in text widget
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, "Gantt Chart:\n")

    # Labels for gantt chart
    label_timeline = "Process Timeline: "
    label_finish   = "Finish Times:     " 

    # Top bar (process timeline)
    result_text.insert(tk.END, label_timeline)
    for pid, s, f in timeline:
        result_text.insert(tk.END, f"| {pid} ")
    result_text.insert(tk.END, "|\n")

    # Bottom bar (finish times)
    result_text.insert(tk.END, label_finish)
    for pid, s, f in timeline:
        result_text.insert(tk.END, f"{s}".ljust(len(pid)+3))
    result_text.insert(tk.END, f"{timeline[-1][2]}\n\n")

    # Process table
    result_text.insert(tk.END, "Process\tAT\tBT\tWT\tTAT\n")
    for p in processes:
        result_text.insert(tk.END, f"{p.pid}\t{p.at}\t{p.bt}\t{p.wt}\t{p.tat}\n")
    result_text.insert(tk.END, f"\nAverage WT = {avg_wt:.2f}\n")
    result_text.insert(tk.END, f"Average TAT = {avg_tat:.2f}\n")

# Creates entry fields for each process (after user enters number of processes)
def create_entries():
    for widget in frame_inputs.winfo_children():  # Clear old widgets
        widget.destroy()
    try:
        n = int(entry_n.get())
    except:
        return
    global entries
    entries = []
    for i in range(n):
        # Arrival time entry
        tk.Label(frame_inputs, text=f"P{i+1} AT:").grid(row=i, column=0)
        at_entry = tk.Entry(frame_inputs, width=5)
        at_entry.grid(row=i, column=1)
        
        # Burst time entry
        tk.Label(frame_inputs, text="BT:").grid(row=i, column=2)
        bt_entry = tk.Entry(frame_inputs, width=5)
        bt_entry.grid(row=i, column=3)
        
        # Priority entry (only shown if Priority scheduling chosen)
        if algo_choice.get() == "Priority":
            tk.Label(frame_inputs, text="Priority:").grid(row=i, column=4)
            pr_entry = tk.Entry(frame_inputs, width=5)
            pr_entry.grid(row=i, column=5)
        else:
            pr_entry = tk.Entry(frame_inputs, width=5)  # Dummy entry
        
        entries.append((at_entry, bt_entry, pr_entry))

# ---------------- Main Window ----------------
root = tk.Tk()
root.title("CPU Scheduling Simulator")

# Algorithm selection
tk.Label(root, text="Choose Algorithm:").pack()
algo_choice = ttk.Combobox(root, values=["FCFS", "SJF", "Priority", "Round Robin"])
algo_choice.current(0)
algo_choice.pack()

lbl_mode = tk.Label(root, text ="Mode (for SJF / Priority Scheduling):")
mode_choice = ttk.Combobox(root, values=["Non-preemptive", "Preemptive"])
mode_choice.current(0)

# Bind algorithm dropdown to show/hide Quantum field
algo_choice.bind("<<ComboboxSelected>>", on_algo_change)

# Quantum input for Round Robin 
lbl_q = tk.Label(root, text="Quantum (for RR):")
entry_q = tk.Entry(root)

# Number of processes
tk.Label(root, text="Number of Processes:").pack()
entry_n = tk.Entry(root)
entry_n.pack()

# Button to create process entry fields
btn_set = tk.Button(root, text="Set Processes", command=create_entries)
btn_set.pack()

# Frame where process entries will appear
frame_inputs = tk.Frame(root)
frame_inputs.pack()

# Run button
btn_run = tk.Button(root, text="Run Simulation", command=run_algorithm)
btn_run.pack()

# Text area to show results (Gantt chart, table, averages)
result_text = tk.Text(root, height=15, width=50)
result_text.pack()

root.mainloop()
