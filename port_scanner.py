import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def h_theme(style):
    style.theme_use('clam')

    style.configure(".",
        background="#050505",
        foreground="#00ff9c",
        fieldbackground="#0b0b0b",
        font=("Consolas", 10)
    )

    style.configure("TLabel",
        background="#050505",
        foreground="#00ff9c",
        font=("Consolas", 11)
    )

    style.configure("Header.TLabel",
        font=("Consolas", 22, "bold"),
        foreground="#39ff14"
    )

    style.configure("TButton",
        background="#00ff9c",
        foreground="black",
        padding=6,
        relief="flat"
    )

    style.map("TButton",
        background=[("active", "#00ffaa")],
        foreground=[("active", "black")]
    )

    style.configure("TLabelframe",
        background="#050505",
        foreground="#39ff14",
        borderwidth=2
    )

    style.configure("TLabelframe.Label",
        background="#050505",
        foreground="#39ff14",
        font=("Consolas", 12, "bold")
    )

    style.configure("TEntry",
        fieldbackground="#0b0b0b",
        foreground="#39ff14",
        insertcolor="#39ff14"
    )

    style.configure("Horizontal.TProgressbar",
        troughcolor="#0b0b0b",
        background="#39ff14",
        thickness=12
    )


class PortScannerApp:

    def __init__(self, root):
        self.root = root
        self.root.title("⚡ PORT SCANNER ⚡")
        self.root.geometry("650x600")
        self.root.configure(bg="#050505", padx=20, pady=20)

        self.is_scanning = False
        self.setup_ui()

    def setup_ui(self):

        header = ttk.Label(self.root,
                           text="⚡ PORT SCANNER ⚡",
                           style="Header.TLabel")
        header.pack(pady=10)

        main = ttk.LabelFrame(self.root, text="SCAN CONFIGURATION", padding=15)
        main.pack(fill=tk.X, pady=10)

        frame1 = ttk.Frame(main)
        frame1.pack(fill=tk.X, pady=5)

        ttk.Label(frame1, text="TARGET").pack(side=tk.LEFT)
        self.target_entry = ttk.Entry(frame1, font=("Consolas", 11))
        self.target_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.target_entry.insert(0, "127.0.0.1")

        frame2 = ttk.Frame(main)
        frame2.pack(fill=tk.X, pady=5)

        ttk.Label(frame2, text="START PORT").pack(side=tk.LEFT)
        self.start_entry = ttk.Entry(frame2, width=8)
        self.start_entry.pack(side=tk.LEFT, padx=10)
        self.start_entry.insert(0, "1")

        ttk.Label(frame2, text="END PORT").pack(side=tk.LEFT)
        self.end_entry = ttk.Entry(frame2, width=8)
        self.end_entry.pack(side=tk.LEFT)
        self.end_entry.insert(0, "1024")

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.scan_btn = ttk.Button(btn_frame,
                                   text="▶ START SCAN",
                                   command=self.toggle_scan,
                                   width=20)
        self.scan_btn.pack(side=tk.LEFT, padx=10)

        self.clear_btn = ttk.Button(btn_frame,
                                    text="✖ CLEAR LOG",
                                    command=self.clear)
        self.clear_btn.pack(side=tk.LEFT)

        self.progress = ttk.Progressbar(self.root,
                                        style="Horizontal.TProgressbar",
                                        length=500,
                                        mode="determinate")
        self.progress.pack(pady=10)

        self.status = ttk.Label(self.root,
                                text="IDLE",
                                font=("Consolas", 11, "bold"))
        self.status.pack()

        frame3 = ttk.Frame(self.root)
        frame3.pack(fill=tk.BOTH, expand=True, pady=10)

        self.text = tk.Text(frame3,
                            bg="#000000",
                            fg="#39ff14",
                            font=("Consolas", 11, "bold"),
                            insertbackground="#39ff14",
                            relief="flat",
                            padx=15,
                            pady=15,
                            state=tk.DISABLED)

        scroll = ttk.Scrollbar(frame3, command=self.text.yview)
        self.text.configure(yscrollcommand=scroll.set)

        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.text.tag_config("open", foreground="#39ff14")
        self.text.tag_config("info", foreground="#00eaff")
        self.text.tag_config("error", foreground="#ff003c")

        self.log("[ SYSTEM INITIALIZED ]", "info")
        self.log("[ WAITING FOR TARGET ]", "info")

    def log(self, msg, tag=None):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, msg + "\n", tag)
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def clear(self):
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        self.text.config(state=tk.DISABLED)
        self.progress["value"] = 0

    def toggle_scan(self):
        if not self.is_scanning:
            threading.Thread(target=self.scan).start()
        else:
            self.is_scanning = False

    def scan_port(self, target, port):
        try:
            s = socket.socket()
            s.settimeout(0.4)
            result = s.connect_ex((target, port))
            s.close()
            return result == 0
        except:
            return False

    def scan(self):
        target = self.target_entry.get()
        start = int(self.start_entry.get())
        end = int(self.end_entry.get())

        self.is_scanning = True
        self.progress["maximum"] = end - start + 1
        self.progress["value"] = 0

        self.status.config(text="SCANNING...")

        self.log(f"[*] TARGET → {target}", "info")
        self.log(f"[*] PORT RANGE → {start}-{end}", "info")

        start_time = time.time()
        open_ports = 0

        with ThreadPoolExecutor(max_workers=120) as exe:
            futures = {exe.submit(self.scan_port, target, p): p for p in range(start, end+1)}

            done = 0
            for f in as_completed(futures):

                if not self.is_scanning:
                    break

                port = futures[f]
                done += 1

                if f.result():
                    open_ports += 1
                    try:
                        service = socket.getservbyport(port)
                    except:
                        service = "unknown"

                    self.root.after(0, self.log,
                                    f"[+] PORT {port} OPEN | SERVICE → {service}",
                                    "open")

                self.root.after(0, self.update_progress, done)

        end_time = time.time()

        self.root.after(0, self.log,
                        f"\n[✓] SCAN COMPLETED IN {round(end_time-start_time,2)} sec",
                        "info")

        self.root.after(0, self.log,
                        f"[✓] TOTAL OPEN PORTS → {open_ports}",
                        "info")

        self.is_scanning = False
        self.root.after(0, self.status.config, {"text": "FINISHED"})

    def update_progress(self, val):
        self.progress["value"] = val


if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    h_theme(style)

    app = PortScannerApp(root)
    root.mainloop()