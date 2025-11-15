import requests

class ProxyChecker:
    def __init__(self, timeout=5):
        self.timeout = timeout

    def check_proxy(self, proxy):
        # proxy format: "ip:port"
        try:
            proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=self.timeout)
            if response.status_code == 200:
                return True, response.json()['origin']
            return False, None
        except:
            return False, None
