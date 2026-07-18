import tkinter as tk
from tkinter import ttk, messagebox
from src.database import Database
from src.monitor import CameraMonitor

APP_TITLE = "Monitor de Câmeras IP - Versão 1.0"

class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1180x650")
        self.root.minsize(980, 560)

        self.db = Database()
        self.monitor = CameraMonitor(self.db, callback=self.refresh_table, interval=10)

        self.create_ui()
        self.refresh_table()
        self.monitor.start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_ui(self):
        header = ttk.Frame(self.root, padding=10)
        header.pack(fill="x")

        ttk.Label(header, text=APP_TITLE, font=("Segoe UI", 18, "bold")).pack(side="left")

        self.lbl_total = ttk.Label(header, text="Total: 0")
        self.lbl_total.pack(side="right", padx=8)
        self.lbl_offline = ttk.Label(header, text="Offline: 0")
        self.lbl_offline.pack(side="right", padx=8)
        self.lbl_online = ttk.Label(header, text="Online: 0")
        self.lbl_online.pack(side="right", padx=8)

        toolbar = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        toolbar.pack(fill="x")

        ttk.Button(toolbar, text="Cadastrar câmera", command=self.open_add_window).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Editar", command=self.edit_selected).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Excluir", command=self.delete_selected).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Atualizar agora", command=self.monitor.check_all_once).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Histórico", command=self.open_history).pack(side="left", padx=4)

        filter_frame = ttk.Frame(toolbar)
        filter_frame.pack(side="right")

        ttk.Label(filter_frame, text="Filtrar NVR:").pack(side="left")
        self.nvr_filter = ttk.Combobox(
            filter_frame,
            values=["Todos", "NVR 1", "NVR 2", "NVR 3", "NVR 4"],
            state="readonly",
            width=10
        )
        self.nvr_filter.set("Todos")
        self.nvr_filter.pack(side="left", padx=5)
        self.nvr_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        columns = ("id", "nvr", "canal", "nome", "ip", "local", "status", "ultima_mudanca")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")

        widths = {
            "id": 45, "nvr": 80, "canal": 60, "nome": 180, "ip": 130,
            "local": 200, "status": 90, "ultima_mudanca": 160
        }

        headings = {
            "id": "ID", "nvr": "NVR", "canal": "Canal", "nome": "Nome",
            "ip": "IP", "local": "Local", "status": "Status",
            "ultima_mudanca": "Última mudança"
        }

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.tree.tag_configure("online", background="#d9fdd3")
        self.tree.tag_configure("offline", background="#ffd6d6")
        self.tree.tag_configure("unknown", background="#f3f3f3")

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        cameras = self.db.get_cameras()
        selected_nvr = self.nvr_filter.get() if hasattr(self, "nvr_filter") else "Todos"

        online = 0
        offline = 0

        for cam in cameras:
            if selected_nvr != "Todos" and cam["nvr"] != selected_nvr:
                continue

            status = cam["status"] or "DESCONHECIDO"
            if status == "ONLINE":
                online += 1
                tag = "online"
            elif status == "OFFLINE":
                offline += 1
                tag = "offline"
            else:
                tag = "unknown"

            self.tree.insert(
                "",
                "end",
                values=(
                    cam["id"], cam["nvr"], cam["canal"], cam["nome"],
                    cam["ip"], cam["local"], status, cam["ultima_mudanca"] or ""
                ),
                tags=(tag,)
            )

        total = len(cameras)
        self.lbl_total.config(text=f"Total: {total}")
        self.lbl_online.config(text=f"Online: {sum(1 for c in cameras if c['status'] == 'ONLINE')}")
        self.lbl_offline.config(text=f"Offline: {sum(1 for c in cameras if c['status'] == 'OFFLINE')}")

    def open_add_window(self):
        self.camera_form()

    def camera_form(self, camera=None):
        win = tk.Toplevel(self.root)
        win.title("Cadastrar câmera" if camera is None else "Editar câmera")
        win.geometry("420x380")
        win.resizable(False, False)

        fields = {}

        def add_field(label, row, values=None):
            ttk.Label(win, text=label).grid(row=row, column=0, padx=12, pady=8, sticky="w")
            if values:
                widget = ttk.Combobox(win, values=values, state="readonly", width=28)
            else:
                widget = ttk.Entry(win, width=31)
            widget.grid(row=row, column=1, padx=12, pady=8)
            fields[label] = widget

        add_field("NVR", 0, ["NVR 1", "NVR 2", "NVR 3", "NVR 4"])
        add_field("Canal", 1)
        add_field("Nome", 2)
        add_field("IP", 3)
        add_field("Local", 4)

        if camera:
            fields["NVR"].set(camera["nvr"])
            fields["Canal"].insert(0, camera["canal"])
            fields["Nome"].insert(0, camera["nome"])
            fields["IP"].insert(0, camera["ip"])
            fields["Local"].insert(0, camera["local"])
        else:
            fields["NVR"].set("NVR 1")

        def save():
            nvr = fields["NVR"].get().strip()
            canal = fields["Canal"].get().strip()
            nome = fields["Nome"].get().strip()
            ip = fields["IP"].get().strip()
            local = fields["Local"].get().strip()

            if not all([nvr, canal, nome, ip, local]):
                messagebox.showwarning("Atenção", "Preencha todos os campos.")
                return

            if camera is None:
                self.db.add_camera(nvr, canal, nome, ip, local)
            else:
                self.db.update_camera(camera["id"], nvr, canal, nome, ip, local)

            win.destroy()
            self.refresh_table()
            self.monitor.check_all_once()

        ttk.Button(win, text="Salvar", command=save).grid(row=5, column=0, columnspan=2, pady=20)

    def get_selected_camera(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Atenção", "Selecione uma câmera.")
            return None
        values = self.tree.item(selection[0], "values")
        return self.db.get_camera(int(values[0]))

    def edit_selected(self):
        camera = self.get_selected_camera()
        if camera:
            self.camera_form(camera)

    def delete_selected(self):
        camera = self.get_selected_camera()
        if camera and messagebox.askyesno("Confirmar", f"Excluir a câmera '{camera['nome']}'?"):
            self.db.delete_camera(camera["id"])
            self.refresh_table()

    def open_history(self):
        win = tk.Toplevel(self.root)
        win.title("Histórico de status")
        win.geometry("850x450")

        cols = ("camera", "ip", "status", "data_hora")
        tree = ttk.Treeview(win, columns=cols, show="headings")

        tree.heading("camera", text="Câmera")
        tree.heading("ip", text="IP")
        tree.heading("status", text="Status")
        tree.heading("data_hora", text="Data/Hora")

        tree.column("camera", width=220)
        tree.column("ip", width=160)
        tree.column("status", width=100, anchor="center")
        tree.column("data_hora", width=180, anchor="center")

        for row in self.db.get_history():
            tree.insert("", "end", values=(row["nome"], row["ip"], row["status"], row["data_hora"]))

        tree.pack(fill="both", expand=True, padx=10, pady=10)

    def on_close(self):
        self.monitor.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()
