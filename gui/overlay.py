import asyncio
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext

class Overlay:
    def __init__(self, brain, context):
        self.brain, self.context = brain, context
        self.root = tk.Tk()
        self.root.title("Neura Assistant")
        self.root.geometry("760x600")
        self.status = tk.StringVar(value="Sẵn sàng")
        frame = ttk.Frame(self.root, padding=14); frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="NEURA ASSISTANT", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(frame, textvariable=self.status).pack(anchor="w", pady=6)
        self.chat = scrolledtext.ScrolledText(frame, state="disabled", wrap="word"); self.chat.pack(fill="both", expand=True)
        row = ttk.Frame(frame); row.pack(fill="x", pady=10)
        self.entry = ttk.Entry(row); self.entry.pack(side="left", fill="x", expand=True); self.entry.bind("<Return>", lambda _: self.submit())
        ttk.Button(row, text="Gửi", command=self.submit).pack(side="left", padx=6)
        ttk.Button(row, text="EMERGENCY STOP", command=self.stop).pack(side="left")
        self.root.bind_all("<Control-Shift-F12>", lambda _: self.stop())

    def write(self, who, text):
        self.chat.configure(state="normal"); self.chat.insert("end", f"{who}: {text}\n\n"); self.chat.see("end"); self.chat.configure(state="disabled")

    def submit(self):
        text = self.entry.get().strip()
        if not text: return
        self.entry.delete(0, "end"); self.write("Bạn", text); self.status.set("Đang xử lý...")
        threading.Thread(target=self.worker, args=(text,), daemon=True).start()

    def worker(self, text):
        reply, _ = asyncio.run(self.brain.handle(text, self.context))
        self.root.after(0, lambda: (self.status.set("Sẵn sàng"), self.write("Neura", reply)))

    def stop(self):
        self.context.safety.emergency_stop(); self.status.set("🛑 EMERGENCY STOP")
        self.write("Neura", "Đã kích hoạt dừng khẩn cấp.")

    def run(self):
        self.root.mainloop()
