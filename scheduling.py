# CPU Scheduling Algorithms Simulator
# Algorithms: FCFS, SJF (Non-preemptive), Priority (Non-preemptive), Round Robin

from collections import deque

# Class to represent a process
class Process:
    def __init__(self, pid, at, bt, priority=0):
        self.pid = pid           # Process ID
        self.at = at             # Arrival Time
        self.bt = bt             # Burst Time
        self.priority = priority # Priority value 
        self.wt = 0              # Waiting Time 
        self.tat = 0             # Turnaround Time 

# Print results in table form after scheduling
def print_table(processes, avg_wt, avg_tat):
    print("\nProcess\tAT\tBT\tWT\tTAT")
    for p in processes:
        print(f"{p.pid}\t{p.at}\t{p.bt}\t{p.wt}\t{p.tat}")
    print(f"Average WT = {avg_wt:.2f}")
    print(f"Average TAT = {avg_tat:.2f}")

# Print Gantt chart using timeline info
def gantt_chart(timeline):
    print("\nGantt Chart:")
    # Top bar
    for pid, s, f in timeline:
        print(f"| {pid} ", end="")
    print("|")
    # Bottom 
    for pid, s, f in timeline:
        print(f"{s}".ljust(len(pid)+3), end="")
    print(f"{timeline[-1][2]}")

# ---------- FCFS ----------
def fcfs(processes):
    processes.sort(key=lambda x: x.at)  # Sort processes by arrival time
    time, timeline = 0, []
    for p in processes:
        if time < p.at:  # idle until process arrives
            time = p.at
        start = time
        p.wt = time - p.at
        time += p.bt
        finish = time
        p.tat = p.wt + p.bt
        timeline.append((p.pid, start, finish))

    avg_wt = sum(p.wt for p in processes) / len(processes)
    avg_tat = sum(p.tat for p in processes) / len(processes)
    gantt_chart(timeline)
    print_table(processes, avg_wt, avg_tat)

# ---------- SJF (Non-preemptive) ----------
def sjf(processes):
    processes.sort(key=lambda x: (x.at, x.bt))
    n, completed, time, timeline = len(processes), 0, 0, []
    ready, done = [], [False] * n
    
    while completed < n:
        # Collect processes that have arrived
        for i, p in enumerate(processes):
            if p.at <= time and not done[i] and (p.bt, i) not in ready:
                ready.append((p.bt, i))
        if ready:
            ready.sort()   # Pick process with smallest burst time
            bt, idx = ready.pop(0)
            p = processes[idx]
            start = time
            p.wt = time - p.at
            time += p.bt
            finish = time
            p.tat = p.wt + p.bt
            done[idx] = True
            completed += 1
            timeline.append((p.pid, start, finish))
        else:
            time += 1  # No process available, idle

    avg_wt = sum(p.wt for p in processes) / n
    avg_tat = sum(p.tat for p in processes) / n
    gantt_chart(timeline)
    print_table(processes, avg_wt, avg_tat)

# ---------- SJF (Preemptive: Shortest Remaining Time First) ----------
def sjf_preemptive(processes):
    n = len(processes)
    time, completed = 0, 0
    remaining = [p.bt for p in processes]  # track remaining burst times
    timeline = []
    last_pid, start_time = None, 0

    while completed < n:
        # Collect all arrived processes that are not finished
        ready = [i for i, p in enumerate(processes) if p.at <= time and remaining[i] > 0]
        if ready:
            # Pick process with shortest remaining time
            idx = min(ready, key=lambda i: remaining[i])
            p = processes[idx]
            if last_pid != p.pid:  # context switch
                if last_pid is not None:
                    timeline.append((last_pid, start_time, time))
                start_time = time
                last_pid = p.pid
            remaining[idx] -= 1
            time += 1
            if remaining[idx] == 0:  # process completed
                completed += 1
                p.tat = time - p.at
                p.wt = p.tat - p.bt
        else:
            time += 1  # CPU idle

    timeline.append((last_pid, start_time, time))
    avg_wt = sum(p.wt for p in processes) / n
    avg_tat = sum(p.tat for p in processes) / n
    gantt_chart(timeline)
    print_table(processes, avg_wt, avg_tat)

# ---------- Priority (Non-preemptive) ----------
def priority_scheduling(processes):
    processes.sort(key=lambda x: (x.at, x.priority))
    n, completed, time, timeline = len(processes), 0, 0, []
    ready, done = [], [False] * n
    
    while completed < n:
        # Collect processes that have arrived
        for i, p in enumerate(processes):
            if p.at <= time and not done[i] and (p.priority, i) not in ready:
                ready.append((p.priority, i))
        if ready:
            ready.sort()   # Pick process with highest priority (lowest value)
            pr, idx = ready.pop(0)
            p = processes[idx]
            start = time
            p.wt = time - p.at
            time += p.bt
            finish = time
            p.tat = p.wt + p.bt
            done[idx] = True
            completed += 1
            timeline.append((p.pid, start, finish))
        else:
            time += 1  # No process available, idle

    avg_wt = sum(p.wt for p in processes) / n
    avg_tat = sum(p.tat for p in processes) / n
    gantt_chart(timeline)
    print_table(processes, avg_wt, avg_tat)

# ---------- Priority (Preemptive) ----------
def priority_preemptive(processes):
    n = len(processes)
    time, completed = 0, 0
    remaining = [p.bt for p in processes]  # track remaining burst times
    timeline = []
    last_pid, start_time = None, 0

    while completed < n:
        # Collect all arrived processes that are not finished
        ready = [i for i, p in enumerate(processes) if p.at <= time and remaining[i] > 0]
        if ready:
            # Pick process with highest priority (lowest priority value)
            idx = min(ready, key=lambda i: processes[i].priority)
            p = processes[idx]
            if last_pid != p.pid:  # context switch
                if last_pid is not None:
                    timeline.append((last_pid, start_time, time))
                start_time = time
                last_pid = p.pid
            remaining[idx] -= 1
            time += 1
            if remaining[idx] == 0:  # process completed
                completed += 1
                p.tat = time - p.at
                p.wt = p.tat - p.bt
        else:
            time += 1  # CPU idle

    timeline.append((last_pid, start_time, time))
    avg_wt = sum(p.wt for p in processes) / n
    avg_tat = sum(p.tat for p in processes) / n
    gantt_chart(timeline)
    print_table(processes, avg_wt, avg_tat)

# ---------- Round Robin ----------
def round_robin(processes, quantum):
    n, time, timeline = len(processes), 0, []
    queue = deque()
    remaining_bt = [p.bt for p in processes]   # Track remaining burst times
    completed, wt, tat = [False] * n, [0] * n, [0] * n
    
    processes.sort(key=lambda x: x.at)
    i = 0
    while i < n and processes[i].at <= time:
        queue.append(i); i += 1

    while queue:
        idx = queue.popleft()
        p = processes[idx]
        start = time

        if remaining_bt[idx] > quantum:   # Process runs for quantum, not finished
            time += quantum
            remaining_bt[idx] -= quantum
            finish = time
        else:                             # Process finishes in this slice
            time += remaining_bt[idx]
            finish = time
            tat[idx] = time - p.at
            wt[idx] = tat[idx] - p.bt
            remaining_bt[idx] = 0
            completed[idx] = True
        
        timeline.append((p.pid, start, finish))

        # Add newly arrived processes
        while i < n and processes[i].at <= time:
            queue.append(i); i += 1
        if not completed[idx]:
            queue.append(idx)  # Put back into queue if not finished
        if not queue and i < n:  # If CPU idle, jump to next arrival
            time = processes[i].at
            queue.append(i); i += 1
    
    # Save calculated WT and TAT into objects
    for j in range(n):
        processes[j].wt, processes[j].tat = wt[j], tat[j]
    
    avg_wt = sum(wt) / n
    avg_tat = sum(tat) / n
    gantt_chart(timeline)
    print_table(processes, avg_wt, avg_tat)

# ---------- MAIN ----------
if __name__ == "__main__":
    print("Choose Algorithm:")
    print("1. FCFS")
    print("2. SJF (Non-preemptive)")
    print("3. SJF (Preemptive)")
    print("4. Priority (Non-preemptive)")
    print("5. Priority (Preemptive)")
    print("6. Round Robin")
    choice = int(input("Enter choice: "))

    n = int(input("\nEnter number of processes: "))
    processes = []
    for i in range(n):
        at = int(input(f"Enter Arrival Time of P{i+1}: "))
        bt = int(input(f"Enter Burst Time of P{i+1}: "))
        if choice == 3:  # Priority scheduling needs priority input
            priority = int(input(f"Enter Priority of P{i+1} (lower = higher priority): "))
        else:
            priority = 0
        processes.append(Process(f"P{i+1}", at, bt, priority))

    # Call chosen algorithm
    if choice == 1:
        fcfs(processes.copy())
    elif choice == 2:
        sjf(processes.copy())
    elif choice == 3:
        sjf_preemptive(processes.copy())
    elif choice == 4:
        priority_scheduling(processes.copy())
    elif choice == 5:
        priority_preemptive(processes.copy())
    elif choice == 6:
        quantum = int(input("Enter Quantum: "))
        round_robin(processes.copy(), quantum)
    else:
        print("Invalid choice!")
