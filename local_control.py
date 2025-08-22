import json
import socket
import tinytuya


device_config = json.load(open("device_info.json"))
DEVICE_ID = device_config["DEVICE_ID"]
DEVICE_IP = device_config["DEVICE_IP"]
LOCAL_KEY = device_config["LOCAL_KEY"]

VERSION = 3.3  

def is_alive(ip, port=6668, timeout=1):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((ip, port))
        s.close()
        return result == 0
    except:
        return False

if not is_alive(DEVICE_IP):
    print(f"Device at {DEVICE_IP} is not reachable. Updating Device IP....")
    local_devices = tinytuya.deviceScan()
    DEVICE_IP = list(local_devices.values())[0]['ip']
    device_config["DEVICE_IP"] = DEVICE_IP
    json.dump(device_config, open("device_info.json", "w"), indent=4)
    print(f"Updated DEVICE_IP to {DEVICE_IP}")
    
device = tinytuya.OutletDevice(
    dev_id=DEVICE_ID,
    address=DEVICE_IP,
    local_key=LOCAL_KEY,
    version=VERSION
)

status = device.status()
print("Full Status:", status)

# Current Status: {'dps': {'1': True, '2': 0, '4': 94, '5': True, '11': 'memory', '13': True}}

FAN_DP = "1"       
FAN_SPEED_DP = "4" 
FAN_COUNTDOWN_DP = "2"  
LIGHT_DP = "5"     
BACKLIGHT_DP = "13" 

# device.set_value(BACKLIGHT_DP, True)

def control_light(state):
    """Control the light switch"""
    device.set_value(LIGHT_DP, state)
    print(f"Light turned {'ON' if state else 'OFF'}")

def control_fan(state):
    """Control the fan switch"""
    device.set_value(FAN_DP, state)
    print(f"Fan turned {'ON' if state else 'OFF'}")

def set_fan_speed(speed):
    """Control fan speed (if available)"""
    device.set_value(FAN_SPEED_DP, speed)
    print(f"Fan speed set to {speed}")

set_fan_speed(40)