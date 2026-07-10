import customtkinter as ctk
import psutil
import threading
from tkinter import messagebox
from tkinter import filedialog
import time
from ..utils import format_size

class DashboardGUI:
    def __init__(self, app_core):
        self.app_core = app_core
        self.config = app_core.config
        self.db = app_core.db

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Assistente de Organização de Arquivos")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

        self._build_ui()
        
        self.running = True
        self.update_thread = threading.Thread(target=self._update_metrics_loop, daemon=True)
        self.update_thread.start()

    def show_window(self):
        self.root.after(0, self.root.deiconify)

    def hide_window(self):
        self.root.withdraw()

    def _build_ui(self):
        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        self.tab_dash = self.tabview.add("Dashboard")
        self.tab_config = self.tabview.add("Configurações")
        self.tab_history = self.tabview.add("Histórico")

        self._build_dash_tab()
        self._build_config_tab()
        self._build_history_tab()

    def _build_dash_tab(self):
        metrics_frame = ctk.CTkFrame(self.tab_dash)
        metrics_frame.pack(fill="x", padx=10, pady=10)

        self.lbl_files_org = ctk.CTkLabel(metrics_frame, text="Arquivos Organizados:\n0", font=("Arial", 16, "bold"))
        self.lbl_files_org.pack(side="left", expand=True, padx=10, pady=10)

        self.lbl_size_freed = ctk.CTkLabel(metrics_frame, text="Tamanho Processado:\n0 B", font=("Arial", 16, "bold"))
        self.lbl_size_freed.pack(side="left", expand=True, padx=10, pady=10)

        self.lbl_cpu = ctk.CTkLabel(metrics_frame, text="CPU: 0%", font=("Arial", 16))
        self.lbl_cpu.pack(side="left", expand=True, padx=10, pady=10)

        self.lbl_ram = ctk.CTkLabel(metrics_frame, text="RAM: 0%", font=("Arial", 16))
        self.lbl_ram.pack(side="left", expand=True, padx=10, pady=10)

        ctrl_frame = ctk.CTkFrame(self.tab_dash)
        ctrl_frame.pack(fill="x", padx=10, pady=20)

        self.btn_scan = ctk.CTkButton(ctrl_frame, text="Forçar Varredura Agora", command=self.force_scan)
        self.btn_scan.pack(side="left", padx=20, pady=20)
        
        self.btn_undo = ctk.CTkButton(ctrl_frame, text="Desfazer Última Ação", command=self.undo_last, fg_color="darkred")
        self.btn_undo.pack(side="right", padx=20, pady=20)

    def _build_config_tab(self):
        self.lbl_folders = ctk.CTkLabel(self.tab_config, text="Pastas Monitoradas:", font=("Arial", 14, "bold"))
        self.lbl_folders.pack(anchor="w", padx=10, pady=(10, 0))

        self.textbox_folders = ctk.CTkTextbox(self.tab_config, height=100)
        self.textbox_folders.pack(fill="x", padx=10, pady=5)
        self._refresh_folders_textbox()

        btn_add = ctk.CTkButton(self.tab_config, text="Adicionar Pasta", command=self.add_folder)
        btn_add.pack(padx=10, pady=5, anchor="w")

    def _refresh_folders_textbox(self):
        self.textbox_folders.delete("1.0", "end")
        for f in self.config.get_monitored_folders():
            self.textbox_folders.insert("end", f + "\n")

    def add_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.config.add_monitored_folder(folder)
            self.app_core.watcher.update_folders()
            self._refresh_folders_textbox()

    def _build_history_tab(self):
        self.history_textbox = ctk.CTkTextbox(self.tab_history)
        self.history_textbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        btn_refresh = ctk.CTkButton(self.tab_history, text="Atualizar", command=self.refresh_history)
        btn_refresh.pack(pady=5)
        self.refresh_history()

    def refresh_history(self):
        self.history_textbox.delete("1.0", "end")
        records = self.db.get_recent_history(50)
        for r in records:
            self.history_textbox.insert("end", f"[{r.date} {r.time}] {r.filename} -> {r.category}\n")

    def force_scan(self):
        self.app_core.worker.scan_directories_now()
        messagebox.showinfo("Aviso", "Varredura iniciada em segundo plano.")

    def undo_last(self):
        record = self.db.undo_last_operation()
        if record:
            try:
                import shutil
                shutil.move(record.destination, record.origin)
                messagebox.showinfo("Desfazer", f"Arquivo {record.filename} retornado para {record.origin}")
                self.refresh_history()
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao desfazer: {e}")
        else:
            messagebox.showinfo("Info", "Nenhum histórico recente.")

    def _update_metrics_loop(self):
        while self.running:
            try:
                cpu = psutil.cpu_percent(interval=1)
                ram = psutil.virtual_memory().percent
                
                org_count = self.db.get_total_files_organized()
                size_freed = self.db.get_total_size_freed()
                
                self.root.after(0, self._update_labels, cpu, ram, org_count, size_freed)
                time.sleep(2)
            except Exception:
                time.sleep(2)

    def _update_labels(self, cpu, ram, count, size):
        self.lbl_cpu.configure(text=f"CPU: {cpu}%")
        self.lbl_ram.configure(text=f"RAM: {ram}%")
        self.lbl_files_org.configure(text=f"Arquivos Organizados:\n{count}")
        self.lbl_size_freed.configure(text=f"Tamanho Processado:\n{format_size(size)}")

    def run(self):
        self.root.mainloop()
