import socket
import ipaddress
import threading
import subprocess
import queue
import time
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from tkinter import scrolledtext

class PortScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Kali Linux Network Port Scanner v1.8")
        self.root.geometry("900x550") # Slightly wider for more status info
        self.root.configure(bg="#1e1e1e")
        
        self.result_queue = queue.Queue()
        self.is_scanning = False  
        
        # Progress Tracking Variables
        self.total_ips = 0
        self.processed_ips = 0
        self.alive_count = 0 # New variable for alive host count
        self.start_time = 0
        
        # --- UI Layout ---
        input_frame = tk.Frame(root, bg="#2d2d2d", pady=10)
        input_frame.pack(fill="x")

        tk.Label(input_frame, text="IP Range:", fg="white", bg="#2d2d2d").grid(row=0, column=0, padx=5)
        self.ip_entry = tk.Entry(input_frame, width=30)
        self.ip_entry.insert(0, "10.3.200.0-10.3.230.255")
        self.ip_entry.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Ports:", fg="white", bg="#2d2d2d").grid(row=0, column=2, padx=5)
        self.port_entry = tk.Entry(input_frame, width=30)
        self.port_entry.insert(0, "80,8080,2020,2024") # Updated default display
        self.port_entry.grid(row=0, column=3, padx=5)

        # Button Colors initialized
        self.scan_btn = tk.Button(input_frame, text="START SCAN", bg="#2ecc71", fg="black", width=10, command=self.start_scan_thread)
        self.scan_btn.grid(row=0, column=4, padx=5)

        self.stop_btn = tk.Button(input_frame, text="STOP", bg="#555555", fg="#ffffff", width=10, state="disabled", command=self.stop_scan)
        self.stop_btn.grid(row=0, column=5, padx=5)

        display_frame = tk.Frame(root, bg="#1e1e1e")
        display_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.log_area = scrolledtext.ScrolledText(display_frame, width=60, bg="#000000", fg="#ffffff", font=("Courier", 10))
        self.log_area.pack(side="left", fill="both", expand=True, padx=5)
        
        self.active_area = scrolledtext.ScrolledText(display_frame, width=40, bg="#000000", fg="#2ecc71", font=("Courier", 10, "bold"))
        self.active_area.pack(side="right", fill="both", expand=True, padx=5)

        # Status Bar
        self.status_var = tk.StringVar(value="Status: Idle")
        status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#2d2d2d", fg="white", font=("Arial", 9))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.log_area.tag_config("open", foreground="#2ecc71")
        self.log_area.tag_config("alive", foreground="#3498db")
        self.log_area.tag_config("closed", foreground="#e74c3c")

        self.root.after(100, self.process_queue)

    def is_host_alive(self, ip):
        if not self.is_scanning: return False
        try:
            output = subprocess.run(['ping', '-c', '1', '-W', '1', str(ip)], 
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return output.returncode == 0
        except:
            return False

    def scan_task(self, ip, ports):
        if not self.is_scanning: return

        if self.is_host_alive(ip):
            self.result_queue.put(("alive_found", None, None)) # Notify GUI an alive host was found
            self.result_queue.put(("log", f"[!] Host Alive: {ip}\n", "alive"))
            for port in ports:
                if not self.is_scanning: break 
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.4)
                    result = sock.connect_ex((str(ip), int(port)))
                    if result == 0:
                        self.result_queue.put(("log", f"   [+] {ip}:{port} - PORT OPEN\n", "open"))
                        self.result_queue.put(("active", f"http://{ip}:{port}/\n", ""))
                    else:
                        self.result_queue.put(("log", f"   [-] {ip}:{port} - PORT CLOSED\n", "closed"))
                    sock.close()
                except:
                    pass
        else:
            self.result_queue.put(("log", f"[x] Host Dead: {ip}\n", "closed"))
        
        self.result_queue.put(("progress", None, None))

    def process_queue(self):
        while not self.result_queue.empty():
            msg_type, text, tag = self.result_queue.get()
            if msg_type == "log":
                self.log_area.insert(tk.END, text, tag)
                self.log_area.see(tk.END)
            elif msg_type == "active":
                self.active_area.insert(tk.END, text)
                self.active_area.see(tk.END)
            elif msg_type == "alive_found":
                self.alive_count += 1 # Increment local counter
            elif msg_type == "progress":
                self.processed_ips += 1
                self.update_status_time()
                
        self.root.after(100, self.process_queue)

    def update_status_time(self):
        if not self.is_scanning or self.processed_ips == 0:
            return

        elapsed_time = time.time() - self.start_time
        ips_remaining = self.total_ips - self.processed_ips
        avg_time_per_ip = elapsed_time / self.processed_ips
        etr_seconds = avg_time_per_ip * ips_remaining
        
        etr_str = time.strftime("%H:%M:%S", time.gmtime(etr_seconds))
        progress_pct = (self.processed_ips / self.total_ips) * 100
        
        # Added Total Alive to the status string
        self.status_var.set(f"Status: Scanning... {progress_pct:.1f}% | Alive Hosts: {self.alive_count} | Processed: {self.processed_ips}/{self.total_ips} | Time Remaining: {etr_str}")

    def stop_scan(self):
        self.is_scanning = False
        self.status_var.set("Status: Stopping... Please wait for threads to exit.")
        self.result_queue.put(("log", "\n[!!!] STOPPING SCAN...\n", "closed"))

    def run_scan(self):
        self.is_scanning = True
        self.processed_ips = 0
        self.alive_count = 0
        self.start_time = time.time()
        
        try:
            ip_input = self.ip_entry.get().split('-')
            start_ip = ipaddress.IPv4Address(ip_input[0].strip())
            end_ip = ipaddress.IPv4Address(ip_input[1].strip())
            
            # --- Modified Port Parsing Logic ---
            port_input_parts = self.port_entry.get().split(',')
            ports = []
            for part in port_input_parts:
                part = part.strip()
                if '-' in part:
                    # Handle range like 1111-9999
                    p_start, p_end = map(int, part.split('-'))
                    ports.extend(range(p_start, p_end + 1))
                else:
                    # Handle single port like 80
                    if part:
                        ports.append(part)
            
            ips = []
            curr = start_ip
            while curr <= end_ip:
                ips.append(curr)
                curr += 1
            
            self.total_ips = len(ips)
            self.status_var.set(f"Status: Starting scan on {self.total_ips} IPs...")

            with ThreadPoolExecutor(max_workers=50) as executor:
                for ip in ips:
                    if not self.is_scanning: break
                    executor.submit(self.scan_task, ip, ports)
        
        except Exception as e:
            self.result_queue.put(("log", f"Error: {e}\n", "closed"))
        
        while self.processed_ips < self.total_ips and self.is_scanning:
            time.sleep(0.1)
            
        self.is_scanning = False
        self.status_var.set(f"Status: Idle / Finished | Alive Hosts: {self.alive_count} | Total Time: {time.strftime('%H:%M:%S', time.gmtime(time.time() - self.start_time))}")
        self.root.after(0, self.reset_ui)

    def reset_ui(self):
        """Sets Start button to Green and Stop button to Gray when idle."""
        self.scan_btn.config(state="normal", bg="#2ecc71", fg="black")
        self.stop_btn.config(state="disabled", bg="#555555", fg="#ffffff")

    def start_scan_thread(self):
        """Sets Start button to Gray and Stop button to Red when scanning."""
        self.log_area.delete('1.0', tk.END)
        self.active_area.delete('1.0', tk.END)
        
        self.scan_btn.config(state="disabled", bg="#555555", fg="#ffffff")
        self.stop_btn.config(state="normal", bg="#ff1800", fg="#ffffff")
        
        threading.Thread(target=self.run_scan, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = PortScannerGUI(root)
    root.mainloop()
