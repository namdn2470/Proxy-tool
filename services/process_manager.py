import subprocess

class ProcessManager:
    def __init__(self):
        self.processes = {}

    def start_proxy_process(self, proxy: str, command: list[str]):
        # command example: ['python', 'some_script.py', proxy]
        try:
            proc = subprocess.Popen(command)
            self.processes[proxy] = proc
            return True
        except:
            return False

    def stop_proxy_process(self, proxy):
        if proxy in self.processes:
            self.processes[proxy].terminate()
            del self.processes[proxy]

    def get_running_processes(self):
        return list(self.processes.keys())
