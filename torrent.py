import os
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter.ttk import Progressbar
import bencodepy

DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

class TorrentDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Torrent Downloader (WebTorrent CLI)")
        self.root.geometry("600x400")
        self.process = None

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Paste Magnet Link:").pack(pady=5)
        self.magnet_input = tk.Entry(self.root, width=80)
        self.magnet_input.pack(padx=10)

        self.progress = Progressbar(self.root, orient='horizontal', length=500, mode='determinate')
        self.progress.pack(pady=10)

        self.download_btn = tk.Button(self.root, text="⬇️ Download", bg='green', fg='white', command=self.start_download)
        self.download_btn.pack(pady=5)

        self.stop_btn = tk.Button(self.root, text="⏹ Stop", bg='red', fg='white', command=self.stop_download, state=tk.DISABLED)
        self.stop_btn.pack(pady=5)

        self.log_text = tk.Text(self.root, height=10, bg="black", fg="white")
        self.log_text.pack(padx=10, pady=10, fill="both", expand=True)

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def start_download(self):
        magnet = self.magnet_input.get().strip()
        if not magnet or not magnet.startswith("magnet:"):
            messagebox.showerror("Invalid Link", "Please enter a valid magnet link!")
            return

        self.log(f"🚀 Starting download: {magnet[:60]}...")
        self.download_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress["value"] = 0

        cmd = f"webtorrent download \"{magnet}\" --out \"{DOWNLOAD_DIR}\""
        self.process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        threading.Thread(target=self.monitor_output, daemon=True).start()

    def monitor_output(self):
        while self.process and self.process.poll() is None:
            line = self.process.stdout.readline()
            if line:
                self.log(line.strip())
                if "%" in line:
                    try:
                        pct = float(line.split("%")[0].split()[-1])
                        self.progress["value"] = pct
                    except:
                        pass
        self.download_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.log("✅ Download Complete or Terminated!")

    def stop_download(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.log("⏹ Download stopped by user.")
            self.stop_btn.config(state=tk.DISABLED)
            self.download_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = TorrentDownloaderApp(root)
    root.mainloop()
