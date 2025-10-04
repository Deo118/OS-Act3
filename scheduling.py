# CPU Scheduling Algorithms Simulator
# Algorithms: FCFS, SJF (Non-preemptive), Priority (Non-preemptive), Round Robin

from collections import deque

# Class to represent a process
class Process:
    def __init__(self, pid, at, bt, priority=0):
        self.pid = pid          # Process ID
        self.at = at            # Arrival Time
        self.bt = bt            # Burst Time
        self.priority = priority # Priority value
        self.wt = 0             # Waiting Time (calculated later)
        self.tat = 0            # Turnaround Time (calculated later)

# Helper function to print results in table form
def print_table(processes, avg_wt, avg_tat):
    print("\nProcess\tAT\tBT\tWT\tTAT")
    for p in processes:
        print(f"{p.pid}\t{p.at}\t{p.bt}\t{p.wt}\t{p.tat}")
    print(f"Average WT = {avg_wt:.2f}")
    print(f"Average TAT = {avg_tat:.2f}")

# Helper function to print Gantt chart order
def gantt_chart(order):
    print("\nGantt Chart:")
    print(" | ".join(order))

# ---------- FCFS ----------
def fcfs(processes):
    processes.sort(key=lambda x: x.at)  # Sort by arrival time
    time = 0
    order = []
    for p in processes:
        if time < p.at:  # CPU idle until process arrives
            time = p.at
        p.wt = time - p.at
        time += p.bt
        p.tat = p.wt + p.bt
        order.append(p.pid)

    avg_wt = sum(p.wt for p in processes) / len(processes)
    avg_tat = sum(p.tat for p in processes) / len(processes)
    gantt_chart(order)
    print_table(processes, avg_wt, avg_tat)

# ---------- SJF (Non-preemptive) ----------
def sjf(processes):
    processes.sort(key=lambda x: (x.at, x.bt))
    n, completed, time, order = len(processes), 0, 0, []
    ready, done = [], [False] * n
    
    while completed < n:
        # Add arrived processes to ready list
        for i, p in enumerate(processes):
            if p.at <= time and not done[i] and (p.bt, i) not in ready:
                ready.append((p.bt, i))
        if ready:
            ready.sort()            # Pick shortest burst time
            bt, idx = ready.pop(0)
            p = processes[idx]
            p.wt = time - p.at
            time += p.bt
            p.tat = p.wt + p.bt
            done[idx] = True
            completed += 1
            order.append(p.pid)
        else:
            time += 1               # CPU idle

    avg_wt = sum(p.wt for p in processes) / n
    avg_tat = sum(p.tat for p in processes) / n
    gantt_chart(order)
    print_table(processes, avg_wt, avg_tat)

# ---------- Priority (Non-preemptive) ----------
def priority_scheduling(processes):
    processes.sort(key=lambda x: (x.at, x.priority))
    n, completed, time, order = len(processes), 0, 0, []
    ready, done = [], [False] * n
    
    while completed < n:
        # Add arrived processes to ready list
        for i, p in enumerate(processes):
            if p.at <= time and not done[i] and (p.priority, i) not in ready:
                ready.append((p.priority, i))
        if ready:
            ready.sort()            # Pick highest priority (lowest number)
            pr, idx = ready.pop(0)
            p = processes[idx]
            p.wt = time - p.at
            time += p.bt
            p.tat = p.wt + p.bt
            done[idx] = True
            completed += 1
            order.append(p.pid)
        else:
            time += 1               # CPU idle

    avg_wt = sum(p.wt for p in processes) / n
    avg_tat = sum(p.tat for p in processes) / n
    gantt_chart(order)
    print_table(processes, avg_wt, avg_tat)

# ---------- Round Robin ----------
def round_robin(processes, quantum):
    n, time, order = len(processes), 0, []
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
        order.append(p.pid)

        if remaining_bt[idx] > quantum:   # Needs more than quantum
            time += quantum
            remaining_bt[idx] -= quantum
        else:                             # Finishes in this slice
            time += remaining_bt[idx]
            tat[idx] = time - p.at
            wt[idx] = tat[idx] - p.bt
            remaining_bt[idx] = 0
            completed[idx] = True
        
        # Add any new arrivals
        while i < n and processes[i].at <= time:
            queue.append(i); i += 1
        if not completed[idx]:
            queue.append(idx)  # Re-queue unfinished process
        if not queue and i < n:  # Jump if CPU idle
            time = processes[i].at
            queue.append(i); i += 1
    
    # Save calculated WT and TAT
    for j in range(n):
        processes[j].wt, processes[j].tat = wt[j], tat[j]
    
    avg_wt = sum(wt) / n
    avg_tat = sum(tat) / n
    gantt_chart(order)
    print_table(processes, avg_wt, avg_tat)

# ---------- MAIN ----------
if __name__ == "__main__":
    print("Choose Algorithm:")
    print("1. FCFS")
    print("2. SJF (Non-preemptive)")
    print("3. Priority (Non-preemptive)")
    print("4. Round Robin")
    choice = int(input("Enter choice: "))

    n = int(input("\nEnter number of processes: "))
    processes = []
    for i in range(n):
        at = int(input(f"Enter Arrival Time of P{i+1}: "))
        bt = int(input(f"Enter Burst Time of P{i+1}: "))
        if choice == 3:  # Only ask priority if Priority Scheduling
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
        priority_scheduling(processes.copy())
    elif choice == 4:
        quantum = int(input("Enter Quantum: "))
        round_robin(processes.copy(), quantum)
    else:
        print("Invalid choice!")
