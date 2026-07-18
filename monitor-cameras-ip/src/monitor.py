import platform
import subprocess
import threading
import time

class CameraMonitor:
    def __init__(self, db, callback=None, interval=10):
        self.db = db
        self.callback = callback
        self.interval = interval
        self.running = False
        self.thread = None

    def ping(self, ip):
        try:
            if platform.system().lower() == "windows":
                cmd = ["ping", "-n", "1", "-w", "1500", ip]
            else:
                cmd = ["ping", "-c", "1", "-W", "2", ip]

            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=4
            )
            return result.returncode == 0
        except Exception:
            return False

    def check_all_once(self):
        threading.Thread(target=self._check_all, daemon=True).start()

    def _check_all(self):
        cameras = self.db.get_cameras()

        for cam in cameras:
            online = self.ping(cam["ip"])
            status = "ONLINE" if online else "OFFLINE"
            self.db.update_status(cam["id"], status)

        if self.callback:
            try:
                self.callback()
            except Exception:
                pass

    def _loop(self):
        while self.running:
            self._check_all()
            for _ in range(self.interval):
                if not self.running:
                    break
                time.sleep(1)

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
