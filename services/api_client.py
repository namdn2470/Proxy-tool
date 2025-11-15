import requests

class ApiClient:
    def __init__(self, api_url='https://api.example.com/proxies'):
        self.api_url = api_url

    def fetch_proxies(self):
        try:
            response = requests.get(self.api_url)
            if response.status_code == 200:
                return response.json()  # assume list of "ip:port"
            return []
        except:
            return []
