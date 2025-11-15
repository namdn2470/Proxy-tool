import os

class Storage:
    def __init__(self, txt_path='proxies.txt'):
        self.txt_path = txt_path
        self.proxies = self.load_proxies()

    def load_proxies(self):
        """Load proxies from TXT file"""
        proxies = []

        if os.path.exists(self.txt_path):
            try:
                with open(self.txt_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and ':' in line:
                            proxies.append({
                                'proxy': line,
                                'type': 'Unknown',
                                'status': 'Unknown',
                                'external_ip': None,
                                'response_time': None
                            })
            except Exception as e:
                print(f"⚠️ Error loading proxies: {e}")

        return proxies

    def save_proxies(self):
        """Save proxies to TXT file"""
        try:
            with open(self.txt_path, 'w', encoding='utf-8') as f:
                for proxy_data in self.proxies:
                    if isinstance(proxy_data, dict):
                        proxy_str = proxy_data.get('proxy', '')
                    else:
                        proxy_str = proxy_data
                    
                    if proxy_str:
                        f.write(f"{proxy_str}\n")
        except Exception as e:
            print(f"⚠️ Error saving proxies: {e}")

    def add_proxy(self, proxy):
        if proxy not in self.proxies:
            self.proxies.append(proxy)
            self.save_proxies()

    def remove_proxy(self, proxy):
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            self.save_proxies()
    
    def remove_proxies(self, proxy_list):
        """Remove multiple proxies at once"""
        removed_count = 0
        for proxy_str in proxy_list:
            # Find and remove matching proxy
            for proxy_data in self.proxies[:]:  # Use slice to avoid modification during iteration
                if isinstance(proxy_data, dict):
                    # Match full proxy or just ip:port
                    stored_proxy = proxy_data.get('proxy', '')
                    if stored_proxy == proxy_str:
                        self.proxies.remove(proxy_data)
                        removed_count += 1
                        break
                    # Also check if proxy_str matches just ip:port
                    stored_parts = stored_proxy.split(':')
                    proxy_parts = proxy_str.split(':')
                    if len(stored_parts) >= 2 and len(proxy_parts) >= 2:
                        if f"{stored_parts[0]}:{stored_parts[1]}" == f"{proxy_parts[0]}:{proxy_parts[1]}":
                            self.proxies.remove(proxy_data)
                            removed_count += 1
                            break
                elif proxy_data == proxy_str:
                    self.proxies.remove(proxy_data)
                    removed_count += 1
                    break
        
        if removed_count > 0:
            self.save_proxies()
        
        return removed_count

    def get_proxies(self):
        return self.proxies
