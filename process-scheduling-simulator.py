import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import copy
import random
import csv
from datetime import datetime

class ProcessSchedulingSimulator:
    def __init__(self, master):
        self.master = master
        self.master.title("Advanced Process Scheduling Simulator")
        self.master.geometry("1500x600")
        
        # Tooltips for algorithms
        self.algorithm_tooltips = {
            'FCFS': "First-Come, First-Served: Processes are executed in the order they arrive.",
            'SPN': "Shortest Process Next: Selects the process with the shortest CPU burst time.",
            'HRRN': "Highest Response Ratio Next: Prioritizes processes based on waiting time and burst time.",
            'RR': "Round Robin: Allocates CPU to processes in a cyclic manner with a time quantum.",
            'SRTF': "Shortest Remaining Time First: Preemptive version of SPN, switches to shortest remaining job."
        }
        
        self.processes = []
        self.algorithms = ['FCFS', 'SPN', 'HRRN', 'RR', 'SRTF']
        self.create_ui()

    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input frame with time quantum
        input_frame = ttk.LabelFrame(main_frame, text="Process Input", padding="10")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

        # Process input labels and entries
        labels = ["Process ID:", "CPU Burst Time:", "Arrival Time:"]
        self.entries = []
        for i, label_text in enumerate(labels):
            ttk.Label(input_frame, text=label_text).grid(row=0, column=i*2, sticky=tk.W)
            entry = ttk.Entry(input_frame, width=15)
            entry.grid(row=0, column=i*2+1, padx=5, pady=5)
            self.entries.append(entry)

        # Buttons frame
        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.grid(row=0, column=6, padx=10, sticky=tk.W)

        # Add Process Button
        ttk.Button(buttons_frame, text="Add Process", command=self.add_process, takefocus=0).grid(row=0, column=0, padx=5)
        
        # Clear Processes Button
        ttk.Button(buttons_frame, text="Clear Processes", command=self.clear_processes, takefocus=0).grid(row=0, column=1, padx=5)
        
        # Random Process Generation Button
        ttk.Button(buttons_frame, text="Generate Random", command=self.generate_random_processes, takefocus=0).grid(row=0, column=2, padx=5)

        #append one random process Generation Button
        ttk.Button(buttons_frame, text="add one Random", command=self.add_one_random, takefocus=0).grid(row=0, column=3, padx=5)


        # Process Table with Edit and Delete capabilities
        self.process_table = ttk.Treeview(main_frame, columns=('PID', 'CBT', 'AT'), show='headings', takefocus=0)
        self.process_table.heading('PID', text='Process ID')
        self.process_table.heading('CBT', text='CPU Burst Time')
        self.process_table.heading('AT', text='Arrival Time')
        self.process_table.grid(row=1, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

        # Right-click context menu for process table
        self.context_menu = tk.Menu(self.master, tearoff=0)
        self.context_menu.add_command(label="Edit Process", command=self.edit_process)
        self.context_menu.add_command(label="Delete Process", command=self.delete_process)
        self.process_table.bind("<Button-3>", self.show_context_menu)

        # Time Quantum Input
        ttk.Label(input_frame, text="Time Quantum (for RR/SRTF):").grid(row=1, column=0, columnspan=2, sticky=tk.W)
        self.time_quantum_entry = ttk.Entry(input_frame, width=15)
        self.time_quantum_entry.grid(row=1, column=2, padx=5, pady=5)
        self.time_quantum_entry.insert(0, "2")

        # Time Context switching Input
        ttk.Label(input_frame, text="Context switching:").grid(row=1, column=3, columnspan=2, sticky=tk.W)
        self.time_Context_switching = ttk.Entry(input_frame, width=15)
        self.time_Context_switching.grid(row=1, column=4, padx=5, pady=5)
        self.time_Context_switching.insert(0, "0.5")  

        
        # Simulate and Help Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Simulate All Algorithms", 
                   command=self.simulate_all_algorithms, takefocus=0).grid(row=0, column=0, padx=5)
        
        ttk.Button(button_frame, text="Help", command=self.show_help, takefocus=0).grid(row=0, column=1, padx=5)
        
        ttk.Button(button_frame, text="Export Results", command=self.export_results, takefocus=0).grid(row=0, column=2, padx=5)

        # Algorithm Tooltips
        self.create_algorithm_tooltips()

    def create_algorithm_tooltips(self):
        # Function to show tooltips when hovering over algorithm names
        def show_tooltip(event, algorithm):
            tooltip_window = tk.Toplevel(self.master)
            tooltip_window.wm_overrideredirect(True)
            tooltip_window.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip_window, text=self.algorithm_tooltips[algorithm], 
                             background="#ffffe0", relief="solid", borderwidth=1)
            label.pack()
            
            def remove_tooltip(event):
                tooltip_window.destroy()
            
            tooltip_window.bind("<Leave>", remove_tooltip)

    def add_process(self):
        try:
            pid = self.entries[0].get()
            cbt = int(self.entries[1].get())
            at = int(self.entries[2].get())
            
            if cbt <= 0 or at < 0:
                raise ValueError("CPU Burst Time must be positive, Arrival Time non-negative")
            
            # Check for duplicate process ID
            if any(p['pid'] == pid for p in self.processes):
                messagebox.showerror("Error", f"Process ID {pid} already exists")
                return
            
            process = {
                'pid': pid, 
                'cbt': cbt, 
                'at': at, 
                'remaining_time': cbt, 
                'waiting_time': 0, 
                'turnaround_time': 0,  
                'response_time': -1
            }
            
            self.processes.append(process)
            self.process_table.insert('', 'end', values=(pid, cbt, at))
            
            # Clear entries
            for entry in self.entries:
                entry.delete(0, tk.END)
        
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def clear_processes(self):
        self.processes.clear()
        for item in self.process_table.get_children():
            self.process_table.delete(item)

    def add_one_random(self):
        num = len(self.processes)+1
        pid = "random"+str(num)
        cbt = random.randint(1, 20)  # CPU burst time between 1-20
        at = random.randint(0, 10)   # Arrival time between 0-10
        process = {
            'pid': pid, 
            'cbt': cbt, 
            'at': at, 
            'remaining_time': cbt, 
            'waiting_time': 0, 
            'turnaround_time': 0, 
            'response_time': -1
        }
        
        self.processes.append(process)
        self.process_table.insert('', 'end', values=(pid, cbt, at))

    def generate_random_processes(self):
        # Generate 5-10 random processes
        num_processes = random.randint(5, 10)
        self.clear_processes()
        
        for i in range(num_processes):
            pid = f"random{i+1}"
            cbt = random.randint(1, 20)  # CPU burst time between 1-20
            at = random.randint(0, 10)   # Arrival time between 0-10
            
            process = {
                'pid': pid, 
                'cbt': cbt, 
                'at': at, 
                'remaining_time': cbt, 
                'waiting_time': 0, 
                'turnaround_time': 0, 
                'response_time': -1
            }
            
            self.processes.append(process)
            self.process_table.insert('', 'end', values=(pid, cbt, at))

    def show_context_menu(self, event):
        # Right-click context menu for process table
        item = self.process_table.identify_row(event.y)
        if item:
            self.process_table.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def edit_process(self):
        # Edit selected process
        selected_item = self.process_table.selection()
        if not selected_item:
            messagebox.showerror("Error", "Select a process to edit")
            return

        # Get current process details
        item_values = self.process_table.item(selected_item[0])['values']
        pid, cbt, at = item_values

        # Create edit dialog
        edit_window = tk.Toplevel(self.master)
        edit_window.title("Edit Process")

        # Labels and entries
        labels = ["Process ID:", "CPU Burst Time:", "Arrival Time:"]
        entries = []

        for i, (label_text, value) in enumerate(zip(labels, [pid, cbt, at])):
            ttk.Label(edit_window, text=label_text).grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(edit_window)
            entry.insert(0, str(value))
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries.append(entry)

        def save_changes():
            try:
                new_pid = entries[0].get()
                new_cbt = int(entries[1].get())
                new_at = int(entries[2].get())

                # Update process in list
                for process in self.processes:
                    if process['pid'] == pid:
                        process['pid'] = new_pid
                        process['cbt'] = new_cbt
                        process['at'] = new_at
                        process['remaining_time'] = new_cbt
                        break

                # Update table
                self.process_table.item(selected_item[0], values=(new_pid, new_cbt, new_at))
                edit_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid input")

        ttk.Button(edit_window, text="Save", command=save_changes).grid(row=3, column=0, columnspan=2, pady=10)

    def delete_process(self):
        # Delete selected process
        selected_item = self.process_table.selection()
        if not selected_item:
            messagebox.showerror("Error", "Select a process to delete")
            return

        item_values = self.process_table.item(selected_item[0])['values']
        pid = item_values[0]

        # Remove from processes list
        self.processes = [p for p in self.processes if p['pid'] != pid]
        
        # Remove from table
        self.process_table.delete(selected_item[0])

    def simulate_all_algorithms(self):
        if not self.processes:
            messagebox.showerror("Error", "Please add processes first")
            return
        
        try:
            time_quantum = int(self.time_quantum_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid time quantum")
            return
        try:
            time_Context_switching = float(self.time_Context_switching.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid time Context switching")
            return

        fig, axs = plt.subplots(len(self.algorithms), 1, figsize=(12, 16), dpi=75)
        fig.suptitle("Process Scheduling Algorithms Comparison", fontsize=14)

        results = {}
        all_waiting_time = {}
        all_turnaround_time = {}
        all_response_time = {}
        for i, algorithm in enumerate(self.algorithms):
            # Deep copy processes to prevent modification
            algo_processes = copy.deepcopy(self.processes)
            
            # Choose scheduling method
            if algorithm == 'FCFS':
                gantt_data, metrics = self.fcfs_scheduling(algo_processes,time_Context_switching)
            elif algorithm == 'SPN':
                gantt_data, metrics = self.spn_scheduling(algo_processes,time_Context_switching)
            elif algorithm == 'HRRN':
                gantt_data, metrics = self.hrrn_scheduling(algo_processes,time_Context_switching)
            elif algorithm == 'RR':
                gantt_data, metrics = self.rr_scheduling(algo_processes,time_Context_switching, time_quantum)
            elif algorithm == 'SRTF':
                gantt_data, metrics = self.srtf_scheduling(algo_processes,time_Context_switching,time_quantum)
            
            # Store results
            results[algorithm] = {'gantt_data': gantt_data, 'metrics': metrics}
            all_waiting_time[algorithm] = metrics["all_waiting_time"]
            all_turnaround_time[algorithm] = metrics["all_turnaround_time"]
            all_response_time[algorithm] = metrics["all_response_time"]
            # Plot Gantt Chart
            self.plot_gantt_chart(axs[i], gantt_data, algorithm)
            
            metrics_text = f"Avg WT: {metrics['avg_waiting_time']:.2f}\n" \
                        f"Avg TT: {metrics['avg_turnaround_time']:.2f}\n" \
                        f"Avg RT: {metrics['avg_response_time']:.2f}"
            axs[i].text(1.02, 0.5, metrics_text, transform=axs[i].transAxes, 
                        verticalalignment='center')

        self.plot_comparison_table(all_waiting_time, all_turnaround_time, all_response_time)

        #self.animate_scheduling(results)

    def show_help(self):
        help_window = tk.Toplevel(self.master)
        help_window.title("Process Scheduling Simulator Help")
        help_window.geometry("600x500")

        help_text = """
        Process Scheduling Simulator - Help Guide

        1. Adding Processes
        - Enter Process ID, CPU Burst Time, and Arrival Time
        - Click "Add Process" to add to the simulation
        - Use "Clear Processes" to reset all processes
        - "Generate Random" creates sample processes

        2. Scheduling Algorithms
        FCFS: First-Come, First-Served
        - Processes executed in order of arrival
        - Simple, but can lead to long waiting times

        SPN: Shortest Process Next
        - Selects process with shortest CPU burst time
        - Minimizes average waiting time

        HRRN: Highest Response Ratio Next
        - Balances waiting time and burst time
        - Prevents starvation of long processes

        RR: Round Robin
        - Allocates CPU in fixed time quantum
        - Provides fair sharing of processor time

        SRTF: Shortest Remaining Time First
        - Preemptive version of SPN
        - Always switches to shortest remaining job

        3. Simulation
        - Set Time Quantum for RR and SRTF
        - Click "Simulate All Algorithms"
        - View Gantt charts and performance metrics
        """

        help_label = tk.Text(help_window, wrap=tk.WORD, font=("Arial", 10))
        help_label.insert(tk.END, help_text)
        help_label.config(state=tk.DISABLED)
        help_label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def export_results(self):
        # Export simulation results to CSV
        if not hasattr(self, 'last_simulation_results'):
            messagebox.showerror("Error", "Run simulation first")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"scheduling_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                
                # Headers
                csv_writer.writerow([
                    "Algorithm", 
                    "Average Waiting Time", 
                    "Average Turnaround Time", 
                    "Average Response Time"
                ])

                # Write results
                for algo, results in self.last_simulation_results.items():
                    csv_writer.writerow([
                        algo, 
                        results['avg_waiting_time'], 
                        results['avg_turnaround_time'], 
                        results['avg_response_time']
                    ])

            messagebox.showinfo("Export Successful", f"Results exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))
    def plot_comparison_table(self, all_waiting_time, all_turnaround_time, all_response_time):
        fig, ax = plt.subplots(figsize=(12, 6), dpi=100)
        fig.suptitle("Process comparison Algorithms table", fontsize=16)

        headers = ["Algorithm", "Waiting Times", "Turnaround Times", "Response Times"]
        rows = []

        for algo in self.algorithms:
            rows.append([
                algo,
                ", ".join(map(str, all_waiting_time[algo])),
                ", ".join(map(str, all_turnaround_time[algo])),
                ", ".join(map(str, all_response_time[algo])),
            ])

        ax.axis('tight')
        ax.axis('off')
        table = ax.table(cellText=rows, colLabels=headers, cellLoc='center', loc='center')

        # Adjust layout for better visuals
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.auto_set_column_width(col=list(range(len(headers))))
        
        # Set table title
        ax.set_title("Comparison of Scheduling Metrics", fontsize=14, pad=10)

        plt.tight_layout()
        plt.show()


    def plot_gantt_chart(self, ax, gantt_data, algorithm):
        ax.clear()
        ax.set_title(f'{algorithm} Scheduling')
        ax.set_xlabel('Time')
        ax.set_ylabel('Processes')

        # Assign unique colors to each process ID
        process_ids = {pid for pid, _, _ in gantt_data}  # Extract unique process IDs
        colors = list(mcolors.TABLEAU_COLORS.values())  # Use Tableau colors
        color_map = {pid: colors[i % len(colors)] for i, pid in enumerate(sorted(process_ids))}

        # Sort data by start time
        gantt_data.sort(key=lambda x: x[1])
        
        for pid, start, end in gantt_data:
            ax.barh(pid, end - start, left=start, height=0.5, 
                    align='center', edgecolor='black', color=color_map[pid])
            ax.text(start + (end - start)/2, pid, f'{pid}', 
                    ha='center', va='center', fontsize=10, color="white")
        
        ax.grid(axis='x', linestyle='--', alpha=0.7)

    def fcfs_scheduling(self, processes,time_Context_switching):
        # Sort by arrival time
        processes.sort(key=lambda x: x['at'])
        
        current_time = 0
        gantt_data = []
        all_waiting_time=[]
        all_turnaround_time=[]
        all_response_time =[]
        total_waiting_time = 0
        total_turnaround_time = 0
        total_response_time = 0

        for process in processes:
            # Wait if process hasn't arrived
            if current_time < process['at']:
                current_time = process['at']

            # Record start time for response time
            if process['response_time'] == -1:
                process['response_time'] = current_time - process['at']

            # Process execution
            start_time = current_time
            end_time = current_time + process['cbt']
            gantt_data.append((process['pid'], start_time, end_time))

            # Calculate metrics
            process['waiting_time'] = start_time - process['at']
            process['turnaround_time'] = end_time - process['at']
            
            total_waiting_time += process['waiting_time']
            all_waiting_time.append(process['waiting_time'])

            total_turnaround_time += process['turnaround_time']
            all_response_time.append(process['turnaround_time'])

            total_response_time += process['response_time']
            all_turnaround_time.append(process['response_time'])

            current_time = end_time + time_Context_switching

        metrics = {
            'avg_waiting_time': total_waiting_time / len(processes),
            'avg_turnaround_time': total_turnaround_time / len(processes),
            'avg_response_time': total_response_time / len(processes),
            "all_waiting_time" : all_waiting_time,
            "all_turnaround_time":all_turnaround_time,
            "all_response_time": all_response_time
        }

        return gantt_data, metrics

    def spn_scheduling(self, processes,time_Context_switching):
        # Create a copy of original processes for metric calculation
        original_processes = processes.copy()
        
        current_time = 0
        gantt_data = []
        all_waiting_time=[]
        all_turnaround_time=[]
        all_response_time =[]
        total_waiting_time = 0
        total_turnaround_time = 0
        total_response_time = 0

        while processes:
            eligible = [p for p in processes if p['at'] <= current_time]
            
            if not eligible:
                current_time += 1
                continue

            # Select shortest process
            selected = min(eligible, key=lambda x: x['cbt'])
            processes.remove(selected)

            if selected['response_time'] == -1:
                selected['response_time'] = current_time - selected['at']

            start_time = current_time
            end_time = current_time + selected['cbt']
            gantt_data.append((selected['pid'], start_time, end_time))

            selected['waiting_time'] = start_time - selected['at']
            selected['turnaround_time'] = end_time - selected['at']
            
            total_waiting_time += selected['waiting_time']
            all_waiting_time.append(selected['waiting_time'])

            total_turnaround_time += selected['turnaround_time']
            all_response_time.append(selected['turnaround_time'])

            total_response_time += selected['response_time']
            all_turnaround_time.append(selected['response_time'])

            current_time = end_time+time_Context_switching

        metrics = {
            'avg_waiting_time': total_waiting_time / len(original_processes),
            'avg_turnaround_time': total_turnaround_time / len(original_processes),
            'avg_response_time': total_response_time / len(original_processes),
            "all_waiting_time" : all_waiting_time,
            "all_turnaround_time":all_turnaround_time,
            "all_response_time": all_response_time
        }

        return gantt_data, metrics

    def hrrn_scheduling(self, processes,time_Context_switching):
        current_time = 0
        gantt_data = []
        all_waiting_time=[]
        all_turnaround_time=[]
        all_response_time =[]
        total_waiting_time = 0
        total_turnaround_time = 0
        total_response_time = 0
        len_processes =len(processes)
        while processes:
            eligible = [p for p in processes if p['at'] <= current_time]            
            if not eligible:
                current_time += 1
                continue

            # Calculate Response Ratio
            for p in eligible:
                waiting_time = current_time - p['at']
                response_ratio = (waiting_time + p['cbt']) / p['cbt']
                p['response_ratio'] = response_ratio

            # Select highest response ratio process
            selected = max(eligible, key=lambda x: x['response_ratio'])
            processes.remove(selected)

            # Record start time for response time
            if selected['response_time'] == -1:
                selected['response_time'] = current_time - selected['at']

            # Process execution
            start_time = current_time
            end_time = current_time + selected['cbt']
            gantt_data.append((selected['pid'], start_time, end_time))

            selected['waiting_time'] = start_time - selected['at']
            selected['turnaround_time'] = end_time - selected['at']
            
            total_waiting_time += selected['waiting_time']
            all_waiting_time.append(selected['waiting_time'])

            total_turnaround_time += selected['turnaround_time']
            all_response_time.append(selected['turnaround_time'])

            total_response_time += selected['response_time']
            all_turnaround_time.append(selected['response_time'])
        
            current_time = end_time+time_Context_switching
        metrics = {
            'avg_waiting_time': total_waiting_time / len_processes,
            'avg_turnaround_time': total_turnaround_time / len_processes,
            'avg_response_time': total_response_time / len_processes,
            "all_waiting_time" : all_waiting_time,
            "all_turnaround_time":all_turnaround_time,
            "all_response_time": all_response_time
        }

        return gantt_data, metrics

    def rr_scheduling(self, processes,time_Context_switching, time_quantum):
        if time_quantum <= 0:
            raise ValueError("Time quantum must be greater than 0.")

        current_time = 0
        gantt_data = []
        all_waiting_time=[]
        all_turnaround_time=[]
        all_response_time =[]
        total_waiting_time = 0
        total_turnaround_time = 0
        total_response_time = 0
        len_processes = len(processes)

        # Ensure all processes have required keys
        for process in processes:
            process.setdefault('remaining_time', process['cbt'])
            process.setdefault('response_time', -1)

        # Queue to manage processes
        process_queue = [p for p in processes if p['at'] <= current_time]
        processes = [p for p in processes if p['at'] > current_time]

        while process_queue or processes:
            if not process_queue and processes:
                # Advance time to the next process arrival
                current_time = processes[0]['at']
                process_queue.append(processes.pop(0))

            current_process = process_queue.pop(0)

            # Record response time first time
            if current_process['response_time'] == -1:
                current_process['response_time'] = current_time - current_process['at']

            # Determine execution time
            execution_time = min(time_quantum, current_process['remaining_time'])
            start_time = current_time
            end_time = current_time + execution_time

            gantt_data.append((current_process['pid'], start_time, end_time))

            # Update remaining time
            current_process['remaining_time'] -= execution_time
            current_time = end_time+time_Context_switching

            # Add newly arrived processes
            while processes and processes[0]['at'] <= current_time:
                process_queue.append(processes.pop(0))

            # If process not complete, add back to queue
            if current_process['remaining_time'] > 0:
                process_queue.append(current_process)
            else:
                current_process['turnaround_time'] = current_time - current_process['at']
                current_process['waiting_time'] = current_process['turnaround_time'] - current_process['cbt']

                total_waiting_time += current_process['waiting_time']
                all_waiting_time.append(current_process['waiting_time'])

                total_turnaround_time += current_process['turnaround_time']
                all_response_time.append(current_process['turnaround_time'])

                total_response_time += current_process['response_time']
                all_turnaround_time.append(current_process['response_time'])

        metrics = {
            'avg_waiting_time': total_waiting_time / len_processes if len_processes > 0 else 0,
            'avg_turnaround_time': total_turnaround_time / len_processes if len_processes > 0 else 0,
            'avg_response_time': total_response_time / len_processes if len_processes > 0 else 0,
            "all_waiting_time" : all_waiting_time,
            "all_turnaround_time":all_turnaround_time,
            "all_response_time": all_response_time
        }

        return gantt_data, metrics

    def srtf_scheduling(self, processes,time_Context_switching, time_quantum):
        current_time = 0
        gantt_data = []
        total_waiting_time = 0
        total_turnaround_time = 0
        total_response_time = 0
        completed = []
        all_waiting_time=[]
        all_turnaround_time=[]
        all_response_time =[]  
        len_processes = len(processes)
        
        while processes or any(p['remaining_time'] > 0 for p in completed):
            # Select eligible processes
            eligible = [p for p in processes if p['at'] <= current_time]
            
            if not eligible:
                current_time = min(p['at'] for p in processes)
                continue

            # Select the process with the shortest remaining time
            selected = min(eligible, key=lambda x: x['remaining_time'])

            # Record response time if this is the first time the process is selected
            if selected['response_time'] == -1:
                selected['response_time'] = current_time - selected['at']

            # Determine execution time
            execution_time = min(time_quantum, selected['remaining_time'])
            start_time = current_time
            end_time = current_time + execution_time

            # Add to Gantt chart
            gantt_data.append((selected['pid'], start_time, end_time))

            # Update process
            selected['remaining_time'] -= execution_time
            current_time = end_time+time_Context_switching

            # Process completion
            if selected['remaining_time'] == 0:
                selected['turnaround_time'] = current_time - selected['at']
                selected['waiting_time'] = selected['turnaround_time'] - selected['cbt']
                
                total_waiting_time += selected['waiting_time']
                all_waiting_time.append(selected['waiting_time'])

                total_turnaround_time += selected['turnaround_time']
                all_response_time.append(selected['turnaround_time'])

                total_response_time += selected['response_time']
                all_turnaround_time.append(selected['response_time'])

                completed.append(selected)
                processes.remove(selected)

        # Calculate average metrics
        metrics = {
            'avg_waiting_time': total_waiting_time / len_processes,
            'avg_turnaround_time': total_turnaround_time / len_processes,
            'avg_response_time': total_response_time / len_processes,
            "all_waiting_time" : all_waiting_time,
            "all_turnaround_time":all_turnaround_time,
            "all_response_time": all_response_time
            
        }

        return gantt_data, metrics


    def animate_scheduling(self, results):
        animation_window = tk.Toplevel(self.master)
        animation_window.title("Progressive CPU Scheduling Timeline")
        animation_window.geometry("1400x900")

        # Matplotlib figure for animation
        fig, axs = plt.subplots(len(self.algorithms), 1, figsize=(14, 8), dpi=100)
        fig.suptitle("Process Scheduling Algorithms", fontsize=16)

        # Find max time across all algorithms
        max_time = max(
            (max((p[2] for p in results[algo]['gantt_data']), default=0) for algo in self.algorithms), 
            default=0
        )

        # Animation state variables
        current_time = tk.DoubleVar(value=0)
        is_running = tk.BooleanVar(value=False)

        def update_progressive_timeline(time_point):
            time_point = float(time_point)
            
            for i, algorithm in enumerate(self.algorithms):
                data = results[algorithm]['gantt_data']
                data.sort(key=lambda x: x[1])
                axs[i].clear()
                axs[i].set_title(f'{algorithm} Scheduling')
                axs[i].set_xlabel('Time')
                axs[i].set_ylabel('Processes')
                
                # Color processes completed before current time
                completed_processes = [p for p in data if p[2] <= time_point]
                for pid, start, end in completed_processes:
                    axs[i].barh(pid, end - start, left=start, height=0.5, 
                                align='center', edgecolor='black', color='green', alpha=0.7)

                # Color processes currently running at this time
                running_processes = [p for p in data if p[1] <= time_point < p[2]]
                for pid, start, end in running_processes:
                    axs[i].barh(pid, end - start, left=start, height=0.5, 
                                align='center', edgecolor='black', color='red', alpha=0.9)

                # Add moving blue line
                axs[i].axvline(x=time_point, color='blue', linestyle='--', linewidth=2)

                # Set x-axis limits
                axs[i].set_xlim(0, max_time)
                axs[i].grid(axis='x', linestyle='--', alpha=0.5)

            plt.tight_layout()
            canvas.draw()

        def start_timeline():
            if not is_running.get():
                is_running.set(True)
                start_button.config(text="Pause", command=pause_timeline)
                animate_timeline()

        def pause_timeline():
            is_running.set(False)
            start_button.config(text="Start", command=start_timeline)

        def animate_timeline():
            if is_running.get():
                current_val = current_time.get()
                if current_val < max_time:
                    new_val = min(current_val + 0.5, max_time)
                    current_time.set(new_val)
                    timeline_slider.set(new_val)     
                    update_progressive_timeline(new_val)
                    
                    # Schedule next update
                    animation_window.after(500, animate_timeline)
                else:
                    pause_timeline()

        def reset_timeline():
            current_time.set(0)
            timeline_slider.set(0)
            update_progressive_timeline(0)
            pause_timeline()

        canvas = FigureCanvasTkAgg(fig, master=animation_window)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        control_frame = ttk.Frame(animation_window)
        control_frame.pack(pady=10)

        timeline_slider = ttk.Scale(
            control_frame, 
            from_=0, 
            to=max_time, 
            orient=tk.HORIZONTAL, 
            length=800,
            variable=current_time,
            command=update_progressive_timeline
        )
        timeline_slider.pack(side=tk.LEFT, padx=10)

        start_button = ttk.Button(
            control_frame, 
            text="Start", 
            command=start_timeline
        )
        start_button.pack(side=tk.LEFT, padx=5)

        reset_button = ttk.Button(
            control_frame, 
            text="Reset", 
            command=reset_timeline
        )
        reset_button.pack(side=tk.LEFT, padx=5)
        time_label = ttk.Label(control_frame, text="Time: 0.00")
        time_label.pack(side=tk.LEFT, padx=5)

        def update_time_label(event=None):
            time_label.config(text=f"Time: {current_time.get():.2f}")

        current_time.trace_add('write', update_time_label)
        update_progressive_timeline(0)
        update_time_label(0)
def main():
    root = tk.Tk()
    app = ProcessSchedulingSimulator(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Program interrupted by user.")

if __name__ == '__main__':
    main()