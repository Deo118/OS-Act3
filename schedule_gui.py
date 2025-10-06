import customtkinter as ctk
from tkinter import messagebox
from collections import deque
import random

class Process:
    def __init__(self, pid, at, bt, priority=0):
        self.pid = pid
        self.at = at
        self.bt = bt
        self.priority = priority
        self.wt = 0
        self.tat = 0

def fcfs(processes):
    processes.sort(key=lambda x: x.at)
    time, order, timeline = 0, [], []
    for p in processes:
        if time < p.at:
            time = p.at
        start = time
        p.wt = time - p.at
        time += p.bt
        finish = time
        p.tat = p.wt + p.bt
        order.append(p.pid)
        timeline.append((p.pid, start, finish))
    return order, timeline

def sjf(processes):
    processes.sort(key=lambda x: (x.at, x.bt))
    n, completed, time, order, timeline = len(processes), 0, 0, [], []
    done = [False]*n
    while completed < n:
        ready = [i for i, p in enumerate(processes) if p.at <= time and not done[i]]
        if ready:
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
            time += 1
    return order, timeline

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

def priority_scheduling(processes):
    n, completed, time, order, timeline = len(processes), 0, 0, [], []
    done = [False]*n
    while completed < n:
        ready = [i for i, p in enumerate(processes) if p.at <= time and not done[i]]
        if ready:
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
            time += 1
    return order, timeline

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

def round_robin(processes, quantum):
    n, time, order = len(processes), 0, []
    queue = deque()
    remaining_bt = [p.bt for p in processes]
    tat, wt, completed = [0] * n, [0] * n, [False] * n
    processes.sort(key=lambda x: x.at)
    timeline = []
    i = 0
    while i < n and processes[i].at <= time:
        queue.append(i)
        i += 1
    last_pid, start_time = None, 0
    while queue:
        idx = queue.popleft()
        p = processes[idx]
        if last_pid != p.pid:
            if last_pid is not None:
                timeline.append((last_pid, start_time, time))
            start_time, last_pid = time, p.pid
        order.append(p.pid)
        if remaining_bt[idx] > quantum:
            time += quantum
            remaining_bt[idx] -= quantum
        else:
            time += remaining_bt[idx]
            tat[idx] = time - p.at
            wt[idx] = tat[idx] - p.bt
            remaining_bt[idx] = 0
            completed[idx] = True
        while i < n and processes[i].at <= time:
            queue.append(i)
            i += 1
        if not completed[idx]:
            queue.append(idx)
        if not queue and i < n:
            time = processes[i].at
            queue.append(i)
            i += 1
    timeline.append((last_pid, start_time, time))
    for j in range(n):
        processes[j].wt, processes[j].tat = wt[j], tat[j]
    return [pid for pid, _, _ in timeline], timeline

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
            pr = int(entries[i][2].get()) if algo == "Priority" else 0
            processes.append(Process(f"P{i + 1}", at, bt, pr))
        except:
            messagebox.showerror("Error", f"Invalid input in Process {i + 1}")
            return

    if algo == "FCFS":
        order, timeline = fcfs(processes)
    elif algo == "SJF (Non-Preemptive)":
        order, timeline = sjf(processes)
    elif algo == "SJF (Preemptive)":
        order, timeline = sjf_preemptive(processes)
    elif algo == "Priority (Non-Preemptive)":
        order, timeline = priority_scheduling(processes)
    elif algo == "Priority (Preemptive)":
        order, timeline = priority_preemptive(processes)
    elif algo == "Round Robin":
        try:
            q = int(entry_q.get())
            order, timeline = round_robin(processes, q)
        except:
            messagebox.showerror("Error", "Enter a valid quantum")
            return

    avg_wt = sum(p.wt for p in processes) / n
    avg_tat = sum(p.tat for p in processes) / n

    result_text.configure(state="normal")
    result_text.delete("1.0", "end")

    #Gantt Chart Output
    result_text.insert("end", "Gantt Chart:\n")

    label_timeline = "Process Timeline:"
    label_finish = "Finish Time:"

    pad = max(len(label_timeline), len(label_finish))
    label_timeline = label_timeline.ljust(pad)
    label_finish = label_finish.ljust(pad)

    segments = [f"| {pid} " for pid, s, f in timeline]
    widths = [len(seg) for seg in segments]

    #Top row
    top_row = label_timeline + "  " + "".join(segments) + "|\n"
    result_text.insert("end", label_timeline)
    for pid, s, f in timeline:
        result_text.insert("end", f"| {pid} ")
    result_text.insert("end", "|\n")
    #Bottom row
    bottom_row = label_finish + "  "
    for (pid, s, f), w in zip(timeline, widths):
        bottom_row += str(s).ljust(w)
    result_text.insert("end", label_finish)
    for pid, s, f in timeline:
        result_text.insert("end", f"{s}".ljust(len(pid)+3))
    result_text.insert("end", f"{timeline[-1][2]}\n\n")
    bottom_row += str(timeline[-1][2]) + "\n\n"

    

    #Process Table Output
    header = f"{'Process':<10}{'AT':<10}{'BT':<10}{'WT':<10}{'TAT':<10}\n"
    result_text.insert("end", header)
    result_text.insert("end", "-" * (10*5) + "\n")
    for p in processes:
        row = f"{p.pid:<10}{p.at:<10}{p.bt:<10}{p.wt:<10}{p.tat:<10}\n"
        result_text.insert("end", row)
    
    result_text.insert("end", f"\nAverage Waiting Time = {avg_wt:.2f}\n")
    result_text.insert("end", f"Average TurnAround Time = {avg_tat:.2f}\n")
    result_text.configure(state="disabled")

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

def auto_generate():
    try:
        n = int(entry_n.get())
    except:
        messagebox.showerror("Error", "Enter a valid number of processes first")
        return
    if not entries or len(entries) != n:
        create_entries()
    for i in range(n):
        at = random.randint(0, 10)
        bt = random.randint(1, 10)
        entries[i][0].delete(0, "end")
        entries[i][0].insert(0, str(at))
        entries[i][1].delete(0, "end")
        entries[i][1].insert(0, str(bt))
        if algo_choice.get() == "Priority":
            pr = random.randint(1, 5)
            entries[i][2].delete(0, "end")
            entries[i][2].insert(0, str(pr))

def center_window(root, width=1200, height=700):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")

def show_hide_quantum(choice):
    if choice == "Round Robin":
        quantum_frame.grid()
    else:
        quantum_frame.grid_remove()
    create_entries()

def main():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    global algo_choice, entry_n, entry_q, frame_inputs, result_text, quantum_frame, entries

    root = ctk.CTk()
    root.title("CPU Scheduling Simulator")
    center_window(root, 1200, 700)
    root.resizable(False, False)

    root.bind("<Return>", lambda event: run_algorithm())

    left_frame = ctk.CTkFrame(root, width=600, height=700)
    left_frame.pack(side="left")
    left_frame.pack_propagate(False)

    controls_frame = ctk.CTkFrame(left_frame)
    controls_frame.pack(pady=10, fill="x")

    ctk.CTkLabel(controls_frame, text="Choose Algorithm:").grid(row=0, column=0, padx=45, pady=(0, 5))
    algo_choice = ctk.CTkOptionMenu(
        controls_frame,
        values=["FCFS (First-Come-First-Serve)", "SJF (Non-Preemptive)", "SJF (Preemptive)",  "Priority (Non-Preemptive)","Priority (Preemptive)",  "Round Robin"],
        command=show_hide_quantum,
        width=140
    )
    algo_choice.grid(row=1, column=0, padx=10, pady=(0, 10))
    algo_choice.set("FCFS")
    ctk.CTkButton(controls_frame, text="Auto Generate", command=auto_generate, width=140).grid(row=2, column=0, padx=10, pady=(0, 10))

    ctk.CTkLabel(controls_frame, text="Number of Processes:").grid(row=0, column=1, padx=45, pady=(0, 5))
    entry_n = ctk.CTkEntry(controls_frame, width=140, justify="center")
    entry_n.grid(row=1, column=1, padx=10, pady=(0, 5))
    ctk.CTkButton(controls_frame, text="Set Processes", command=create_entries, width=140).grid(row=2, column=1, padx=10, pady=(0, 10))

    quantum_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
    ctk.CTkLabel(quantum_frame, text="Quantum (for RR):").pack(pady=(0, 5))
    entry_q = ctk.CTkEntry(quantum_frame, width=140, justify="center")
    entry_q.pack()
    quantum_frame.grid(row=0, column=2, rowspan=3, padx=10, pady=5)
    quantum_frame.grid_remove()

    frame_inputs = ctk.CTkScrollableFrame(left_frame, width=580, height=500)
    frame_inputs.pack(pady=10, padx=10, fill="both", expand=False)

    ctk.CTkButton(left_frame, text="Run Simulation", command=run_algorithm).pack(pady=10)

    right_frame = ctk.CTkFrame(root, width=600, height=700)
    right_frame.pack(side='right')
    right_frame.pack_propagate(False)

    ctk.CTkLabel(right_frame, text='OUTPUT', font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))

    textbox_frame = ctk.CTkFrame(right_frame, width=550, height=630)
    textbox_frame.pack(pady=5)
    textbox_frame.pack_propagate(False)

    result_text = ctk.CTkTextbox(textbox_frame, width=530, height=630, wrap="none")
    result_text.pack(side="left", fill="both", expand=True)
    result_text.configure(font=("Courier New", 15))

    v_scrollbar = ctk.CTkScrollbar(textbox_frame, orientation="vertical", command=result_text.yview)
    v_scrollbar.pack(side="right", fill="y")
    result_text.configure(yscrollcommand=v_scrollbar.set)

    h_scrollbar = ctk.CTkScrollbar(right_frame, orientation="horizontal", command=result_text.xview)
    h_scrollbar.pack(side="bottom", fill="x", padx=5)
    result_text.configure(xscrollcommand=h_scrollbar.set)

    result_text.configure(state="disabled")

    root.mainloop()

if __name__ == "__main__":
    main()