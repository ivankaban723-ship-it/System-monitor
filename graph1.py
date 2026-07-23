import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import re
import threading
from datetime import datetime

class SystemMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Системний Монітор")
        self.root.geometry("1100x650")
        self.root.configure(bg='#1a1a2e')
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Custom.Treeview", background='#0f3460', foreground='#e0e0e0', fieldbackground='#0f3460', rowheight=25)
        style.map('Custom.Treeview', background=[('selected', '#2196F3')])
        style.configure("Custom.Treeview.Heading", background='#1a4a7a', foreground='#4fc3f7', font=('Segoe UI', 10, 'bold'))
        style.configure("Custom.TButton", background='#2196F3', foreground='white', borderwidth=0)
        
        self.create_widgets()
        self.auto_refresh = True
        # Запуск фонового процесу C++
        threading.Thread(target=self.run_backend, daemon=True).start()

    def create_widgets(self):
        top_frame = tk.LabelFrame(self.root, text="📊 Системна інформація", bg='#16213e', fg='#4fc3f7', font=('Segoe UI', 11, 'bold'))
        top_frame.pack(fill=tk.X, padx=10, pady=5)
         
        info_frame = tk.Frame(top_frame, bg='#16213e')
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        self.temp_label = tk.Label(info_frame, text="🌡️ Температура: 0°C", bg='#16213e', fg='#e0e0e0', font=('Segoe UI', 12, 'bold'))
        self.temp_label.pack(side=tk.LEFT, padx=20)
        self.count_label = tk.Label(info_frame, text="📋 Процесів: 0", bg='#16213e', fg='#e0e0e0', font=('Segoe UI', 12, 'bold'))
        self.count_label.pack(side=tk.LEFT)

        btn_frame = tk.Frame(self.root, bg='#1a1a2e')
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(btn_frame, text="❌ Завершити процес", style="Custom.TButton", command=self.kill_process).pack(side=tk.LEFT)

        columns = ('PID', 'Назва', 'RAM (MB)', 'Температура')
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings', style="Custom.Treeview")
        for col in columns: self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def run_backend(self):
    
        process = subprocess.Popen(['./system'], stdout=subprocess.PIPE, text=True)
        buffer = []
        while True:
            line = process.stdout.readline()
            if not line: break
            
            # Парсинг твого формату C++
            match = re.search(r'Name:\s*([^\|]+)\s*\|\s*RAM:\s*(\d+)\s*MB\s*\|\s*PID:\s*(\d+)\s*\|\s*SysTemp:\s*(\d+)C', line)
            if match:
                buffer.append((match.group(3), match.group(1).strip(), match.group(2), match.group(4)))
            
            if "System Monitor" in line and buffer:
                self.root.after(0, self.update_table, list(buffer))
                buffer = []

    def update_table(self, data):
        for item in self.tree.get_children(): self.tree.delete(item)
        for row in data: self.tree.insert('', 'end', values=row)
        self.temp_label.config(text=f"🌡️ Температура: {data[0][3]}°C")
        self.count_label.config(text=f"📋 Процесів: {len(data)}")

    def kill_process(self):
        selected = self.tree.selection()
        if not selected: return
        pid = self.tree.item(selected)['values'][0]
        if messagebox.askyesno("Увага", f"Вбити процес {pid}?"):
            subprocess.run(['kill', '-9', str(pid)])

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemMonitor(root)
    root.mainloop()