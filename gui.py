import tkinter as tk
from tkinter import ttk
import json
import socket
import tinytuya
import threading

class SmartDeviceController:
    def __init__(self):
        try:
            self.device_config = json.load(open("device_info.json"))
            self.DEVICE_ID = self.device_config["DEVICE_ID"]
            self.DEVICE_IP = self.device_config["DEVICE_IP"]
            self.LOCAL_KEY = self.device_config["LOCAL_KEY"]
            self.VERSION = 3.3
        except FileNotFoundError:
            print("device_info.json not found!")
            return
        
        self.FAN_DP = "1"
        self.FAN_SPEED_DP = "4"
        self.LIGHT_DP = "5"
        
        self.setup_device()
        
        self.create_gui()
        
        self.update_status()
    
    def is_alive(self, ip, port=6668, timeout=1):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            result = s.connect_ex((ip, port))
            s.close()
            return result == 0
        except:
            return False
    
    def setup_device(self):
        if not self.is_alive(self.DEVICE_IP):
            print(f"Device at {self.DEVICE_IP} is not reachable. Updating Device IP....")
            try:
                local_devices = tinytuya.deviceScan()
                if local_devices:
                    self.DEVICE_IP = list(local_devices.values())[0]['ip']
                    self.device_config["DEVICE_IP"] = self.DEVICE_IP
                    json.dump(self.device_config, open("device_info.json", "w"), indent=4)
                    print(f"Updated DEVICE_IP to {self.DEVICE_IP}")
            except Exception as e:
                print(f"Error scanning for devices: {e}")
        
        self.device = tinytuya.OutletDevice(
            dev_id=self.DEVICE_ID,
            address=self.DEVICE_IP,
            local_key=self.LOCAL_KEY,
            version=self.VERSION
        )
    
    def create_gui(self):
        self.root = tk.Tk()
        self.root.title("Smart Device Control")
        self.root.geometry("250x200")
        self.root.resizable(False, False)
        
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - 270  
        y = screen_height - 250 
        self.root.geometry(f"250x200+{x}+{y}")
        
        self.root.attributes('-topmost', True)
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        light_frame = ttk.LabelFrame(main_frame, text="Light Control", padding="5")
        light_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.light_button = tk.Button(
            light_frame, 
            text="Light OFF", 
            bg="red", 
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.toggle_light,
            width=15
        )
        self.light_button.pack()
        fan_frame = ttk.LabelFrame(main_frame, text="Fan Control", padding="5")
        fan_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.fan_button = tk.Button(
            fan_frame, 
            text="Fan OFF", 
            bg="red", 
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.toggle_fan,
            width=15
        )
        self.fan_button.pack(pady=(0, 5))
        speed_frame = ttk.Frame(fan_frame)
        speed_frame.pack(fill=tk.X)
        
        ttk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT)
        
        self.speed_var = tk.IntVar(value=50)
        self.speed_scale = ttk.Scale(
            speed_frame, 
            from_=1, 
            to=100, 
            variable=self.speed_var,
            orient=tk.HORIZONTAL,
            command=self.on_speed_change
        )
        self.speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        
        self.speed_label = ttk.Label(speed_frame, text="50")
        self.speed_label.pack(side=tk.RIGHT)
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(status_frame, text="Status: Connecting...", font=("Arial", 8))
        self.status_label.pack()
        
        self.light_state = False
        self.fan_state = False
        self.current_speed = 50
    
    def toggle_light(self):
        try:
            self.light_state = not self.light_state
            self.device.set_value(self.LIGHT_DP, self.light_state)
            self.update_light_button()
            self.status_label.config(text=f"Light {'ON' if self.light_state else 'OFF'}")
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)[:30]}...")
    
    def toggle_fan(self):
        try:
            self.fan_state = not self.fan_state
            self.device.set_value(self.FAN_DP, self.fan_state)
            self.update_fan_button()
            self.status_label.config(text=f"Fan {'ON' if self.fan_state else 'OFF'}")
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)[:30]}...")
    
    def on_speed_change(self, value):
        speed = int(float(value))
        self.speed_label.config(text=str(speed))
        if hasattr(self, 'speed_timer'):
            self.root.after_cancel(self.speed_timer)
        
        self.speed_timer = self.root.after(500, lambda: self.set_fan_speed(speed))
    
    def set_fan_speed(self, speed):
        try:
            self.device.set_value(self.FAN_SPEED_DP, speed)
            self.current_speed = speed
            self.status_label.config(text=f"Fan speed: {speed}%")
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)[:30]}...")
    
    def update_light_button(self):
        if self.light_state:
            self.light_button.config(text="Light ON", bg="green")
        else:
            self.light_button.config(text="Light OFF", bg="red")
    
    def update_fan_button(self):
        if self.fan_state:
            self.fan_button.config(text="Fan ON", bg="green")
        else:
            self.fan_button.config(text="Fan OFF", bg="red")
    
    def update_status(self):
        def get_status():
            try:
                status = self.device.status()
                if status and 'dps' in status:
                    dps = status['dps']
                    if self.LIGHT_DP in dps:
                        self.light_state = dps[self.LIGHT_DP]
                        self.root.after(0, self.update_light_button)
                    
                    if self.FAN_DP in dps:
                        self.fan_state = dps[self.FAN_DP]
                        self.root.after(0, self.update_fan_button)
                    
                    if self.FAN_SPEED_DP in dps:
                        speed = dps[self.FAN_SPEED_DP]
                        self.current_speed = speed
                        self.root.after(0, lambda: self.speed_var.set(speed))
                        self.root.after(0, lambda: self.speed_label.config(text=str(speed)))
                    
                    self.root.after(0, lambda: self.status_label.config(text="Connected"))
                else:
                    self.root.after(0, lambda: self.status_label.config(text="No response"))
            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(text=f"Error: {str(e)[:20]}..."))
        threading.Thread(target=get_status, daemon=True).start()
    
    def run(self):
        def periodic_update():
            self.update_status()
            self.root.after(5000, periodic_update)
        
        self.root.after(1000, periodic_update)  # Start after 1 second
        self.root.mainloop()

if __name__ == "__main__":
    app = SmartDeviceController()
    app.run()