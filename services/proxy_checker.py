import subprocess
import json
import time
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

class ProxyChecker:
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.test_urls = [
            "http://httpbin.org/ip",
            "http://ip-api.com/json",
            "https://api.ipify.org?format=json"
        ]
        self.connection_timeout = 5

    def check_proxy(self, proxy, username=None, password=None):
        """
        Check proxy type and status using curl
        Returns: (type, status, response_time, ip)
        - type: 'HTTP', 'HTTPS', 'SOCKS5', or 'Unknown'
        - status: 'LIVE', 'DIE', or 'TIMEOUT'
        - response_time: float (seconds) or None
        - ip: external IP or None
        """
        # Parse proxy format: ip:port or ip:port:user:pass
        parts = proxy.split(':')
        if len(parts) >= 2:
            ip = parts[0]
            port = parts[1]
            if len(parts) >= 4:
                username = parts[2]
                password = parts[3]
        else:
            return 'Unknown', 'DIE', None, None

        # First check if port is open
        if not self._check_port_open(ip, int(port)):
            return 'Unknown', 'DIE', None, 'Port Closed'

        # Build proxy string with auth if available
        if username and password:
            proxy_str = f"{username}:{password}@{ip}:{port}"
        else:
            proxy_str = f"{ip}:{port}"

        # Try different proxy types
        proxy_types = [
            ('SOCKS5', f'socks5://{proxy_str}'),
            ('HTTP', f'http://{proxy_str}'),
            ('HTTPS', f'https://{proxy_str}'),
        ]

        for proxy_type, proxy_url in proxy_types:
            result = self._test_proxy_curl(proxy_url)
            if result['status'] == 'LIVE':
                return proxy_type, result['status'], result['time'], result['ip']

        return 'Unknown', 'DIE', None, None

    def check_proxy_detailed(self, proxy):
        """
        Detailed check with full information
        Returns dict with:
        - proxy: original proxy string
        - type: proxy type
        - status: LIVE/DIE/TIMEOUT
        - response_time: response time in seconds
        - ip: external IP
        - country: country code (if available)
        - anonymity: anonymity level
        """
        proxy_type, status, response_time, ip = self.check_proxy(proxy)
        
        result = {
            'proxy': proxy,
            'type': proxy_type,
            'status': status,
            'response_time': response_time,
            'external_ip': ip,
            'country': None,
            'anonymity': 'Unknown'
        }
        
        # Get country info if proxy is live
        if status == 'LIVE' and ip:
            result['country'] = self._get_country_from_ip(ip)
            result['anonymity'] = self._check_anonymity(proxy)
        
        return result

    def _check_port_open(self, host, port):
        """Check if proxy port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.connection_timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False

    def _get_country_from_ip(self, ip):
        """Get country code from IP address"""
        try:
            cmd = ['curl', '-s', f'http://ip-api.com/json/{ip}']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout:
                data = json.loads(result.stdout)
                return data.get('countryCode', 'Unknown')
        except:
            pass
        return 'Unknown'

    def _check_anonymity(self, proxy):
        """Check proxy anonymity level"""
        # Simplified anonymity check
        # In real implementation, would check headers to determine elite/anonymous/transparent
        return 'Unknown'

    def _test_proxy_curl(self, proxy_url):
        """Test proxy using curl command"""
        try:
            start_time = time.time()
            
            cmd = [
                'curl',
                '-x', proxy_url,
                '-s',  # silent
                '--connect-timeout', str(self.connection_timeout),
                '--max-time', str(self.timeout),
                self.test_urls[0]  # Use first test URL
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout + 2
            )
            
            elapsed_time = time.time() - start_time
            
            if result.returncode == 0 and result.stdout:
                try:
                    data = json.loads(result.stdout)
                    external_ip = data.get('origin', 'Unknown')
                    return {
                        'status': 'LIVE',
                        'time': round(elapsed_time, 2),
                        'ip': external_ip
                    }
                except:
                    pass
            
            return {'status': 'DIE', 'time': None, 'ip': None}
            
        except subprocess.TimeoutExpired:
            return {'status': 'TIMEOUT', 'time': None, 'ip': None}
        except Exception as e:
            return {'status': 'DIE', 'time': None, 'ip': None}

    def check_multiple_proxies(self, proxies, max_workers=10):
        """
        Check multiple proxies concurrently
        Args:
            proxies: list of proxy strings
            max_workers: maximum number of concurrent checks
        Returns:
            list of dicts with check results
        """
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {executor.submit(self.check_proxy_detailed, proxy): proxy 
                             for proxy in proxies}
            
            for future in as_completed(future_to_proxy):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    proxy = future_to_proxy[future]
                    results.append({
                        'proxy': proxy,
                        'type': 'Unknown',
                        'status': 'DIE',
                        'response_time': None,
                        'external_ip': None,
                        'country': None,
                        'anonymity': 'Unknown',
                        'error': str(e)
                    })
        
        return results

    def is_proxy_live(self, proxy):
        """
        Quick check if proxy is live
        Returns: True if LIVE, False otherwise
        """
        _, status, _, _ = self.check_proxy(proxy)
        return status == 'LIVE'

    def filter_live_proxies(self, proxies, max_workers=10):
        """
        Filter list to only return live proxies
        Args:
            proxies: list of proxy strings
            max_workers: maximum number of concurrent checks
        Returns:
            list of live proxy strings
        """
        results = self.check_multiple_proxies(proxies, max_workers)
        return [r['proxy'] for r in results if r['status'] == 'LIVE']
