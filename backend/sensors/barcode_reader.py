import threading
import sys

class BarcodeScanner(threading.Thread):
    def __init__(self, callback):
        super().__init__()
        self.daemon = True
        self.callback = callback

    def run(self):
        print("[System] Barcode Scanner Active (waiting for keyboard HID input)")
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break # EOF
                line = line.strip()
                if line:
                    self.callback(line)
            except Exception as e:
                pass
