import json
import os

class Storage:
    def __init__(self, file_path='proxies.json'):
        self.file_path = file_path
        self.proxies = self.load_proxies()

    def load_proxies(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                return json.load(f)
        return []

    def save_proxies(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.proxies, f)

    def add_proxy(self, proxy):
        if proxy not in self.proxies:
            self.proxies.append(proxy)
            self.save_proxies()

    def remove_proxy(self, proxy):
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            self.save_proxies()

    def get_proxies(self):
        return self.proxies
