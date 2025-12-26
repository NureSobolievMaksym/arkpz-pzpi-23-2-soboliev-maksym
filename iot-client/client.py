import time
import json
import random
import requests
import os
from datetime import datetime

CONFIG_FILE = "config.json"

class ConfigManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.config = self.load_config()

    def load_config(self):
        if not os.path.exists(self.filepath):
            default_config = {
                "server_url": "http://localhost:8000",
                "device_id": 1,
                "update_interval": 5,
                "simulation_mode": True
            }
            self.save_config(default_config)
            return default_config
        with open(self.filepath, "r") as f:
            return json.load(f)

    def save_config(self, new_config):
        with open(self.filepath, "w") as f:
            json.dump(new_config, f, indent=4)
        self.config = new_config

    def update_setting(self, key, value):
        self.config[key] = value
        self.save_config(self.config)

class SensorManager:
    def __init__(self):
        self.temp = 20.0
        self.hum = 50.0

    def read_data(self):
        self.temp += random.uniform(-0.5, 0.5)
        self.hum += random.uniform(-1, 1)
        
        self.temp = max(-10, min(40, self.temp))
        self.hum = max(0, min(100, self.hum))
        
        return round(self.temp, 2), round(self.hum, 2)

class IoTClient:
    def __init__(self):
        self.config_manager = ConfigManager(CONFIG_FILE)
        self.sensor_manager = SensorManager()
        self.config = self.config_manager.config

    def send_data(self, temp, hum):
        url = f"{self.config['server_url']}/measurements/"
        payload = {
            "device_id": self.config['device_id'],
            "temperature": temp,
            "humidity": hum,
            "co2_level": 400.0
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                print(f"[{datetime.now()}] Data sent: {payload} | Response: {response.json()}")
            else:
                print(f"[{datetime.now()}] Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[{datetime.now()}] Connection failed: {e}")

    def run_setup(self):
        print("--- IoT Client Setup ---")
        print(f"Current Server: {self.config['server_url']}")
        print(f"Current Device ID: {self.config['device_id']}")
        
        choice = input("Do you want to change settings? (y/n): ")
        if choice.lower() == 'y':
            new_url = input("Enter Server URL: ")
            new_id = input("Enter Device ID: ")
            self.config_manager.update_setting("server_url", new_url)
            self.config_manager.update_setting("device_id", int(new_id))
            self.config = self.config_manager.config
            print("Settings updated.")
        print("Starting client...")

    def start(self):
        self.run_setup()
        print(f"Client started. Sending data every {self.config['update_interval']} seconds.")
        try:
            while True:
                temp, hum = self.sensor_manager.read_data()
                self.send_data(temp, hum)
                time.sleep(self.config['update_interval'])
        except KeyboardInterrupt:
            print("\nClient stopped.")

if __name__ == "__main__":
    client = IoTClient()
    client.start()