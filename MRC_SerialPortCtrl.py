import sys
import time
import threading
import re
import csv

# --- 1. VERIFICACIÓN DE DEPENDENCIAS ---
def check_dependencies():
    dependencies = {
        "serial": "pyserial",
        "pandas": "pandas",
        "openpyxl": "openpyxl"
    }
    missing = []
    for lib, package in dependencies.items():
        try:
            __import__(lib)
        except ImportError:
            missing.append(package)
    
    if missing:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        install_cmd = f"pip install {' '.join(missing)}"
        messagebox.showerror("Librerías Faltantes", 
                             f"No se encontraron: {', '.join(missing)}\n\nEjecuta en consola:\n{install_cmd}")
        sys.exit()

check_dependencies()

# --- 2. IMPORTACIONES TRAS VERIFICACIÓN ---
import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class SerialPyInterface(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Variables de control
        self.serial_object = None
        self.stop_event = threading.Event()
        self.buffer = ''
        self.data_history = [] 
        self.csv_file = None
        self.csv_writer = None
        self.file_path = None
        
        # Variables de Interfaz
        self.show_hex_var = tk.BooleanVar(value=True)
        self.enable_log_var = tk.BooleanVar(value=False)
        self.export_format = tk.StringVar(value="CSV")
        
        # Variables de columnas
        self.data_column_name = tk.StringVar(value="DatoRecibidoCompleto") 
        self.csv_column_names = tk.StringVar(value="Col1,Col2,Col3,Col4")

        self.title("MRC SerialPortCtrl")
        self.geometry('900x850')
        self.create_widgets()
        self.after(100, self.list_ports)

    def create_widgets(self):
        # --- SECCIÓN 1: CONEXIÓN ---
        frame_config = ttk.LabelFrame(self, text="Configuración de Conexión", padding="10")
        frame_config.pack(padx=10, pady=5, fill="x")

        ttk.Label(frame_config, text="Puerto:").grid(row=0, column=0, padx=5)
        self.port_combobox = ttk.Combobox(frame_config, width=15)
        self.port_combobox.grid(row=0, column=1, padx=5)

        ttk.Label(frame_config, text="Bauds:").grid(row=0, column=2, padx=5)
        self.baud_combobox = ttk.Combobox(frame_config, width=10, values=["9600", "115200"])
        self.baud_combobox.set("115200")
        self.baud_combobox.grid(row=0, column=3, padx=5)
        
        self.connect_button = ttk.Button(frame_config, text="Conectar", command=self.toggle_connection)
        self.connect_button.grid(row=0, column=4, padx=20)

        # --- SECCIÓN 2: LOGGING ---
        self.frame_log = ttk.LabelFrame(self, text="Registro de Datos", padding="10")
        self.frame_log.pack(padx=10, pady=5, fill="x")

        ttk.Checkbutton(self.frame_log, text="Habilitar Exportación", 
                        variable=self.enable_log_var, command=self.toggle_log_options).grid(row=0, column=0, sticky="w")

        self.log_options_container = ttk.Frame(self.frame_log)
        
        # Fila 1: Formato y Selecciona Archivo (Posición solicitada)
        ttk.Label(self.log_options_container, text="Formato:").grid(row=0, column=0, padx=5, pady=5)
        ttk.OptionMenu(self.log_options_container, self.export_format, "CSV", "CSV", "Excel").grid(row=0, column=1, padx=5)
        
        self.path_button = ttk.Button(self.log_options_container, text="Seleccionar Archivo", command=self.select_file_path)
        self.path_button.grid(row=0, column=2, padx=10)

        # Fila 2: Títulos de columnas
        ttk.Label(self.log_options_container, text="Título Dato Completo:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Entry(self.log_options_container, textvariable=self.data_column_name, width=20).grid(row=1, column=1, padx=5)

        ttk.Label(self.log_options_container, text="Sub-Columnas:").grid(row=1, column=2, padx=5)
        ttk.Entry(self.log_options_container, textvariable=self.csv_column_names, width=35).grid(row=1, column=3, padx=5, sticky="ew")

        # --- SECCIÓN 3: ENVIAR ---
        frame_send = ttk.LabelFrame(self, text="Envio de Datos", padding="10")
        frame_send.pack(padx=10, pady=5, fill="x")
        self.send_entry = ttk.Entry(frame_send, state=tk.DISABLED)
        self.send_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.send_entry.bind('<Return>', lambda e: self.send_data())
        self.send_button = ttk.Button(frame_send, text="Enviar", command=self.send_data, state=tk.DISABLED)
        self.send_button.pack(side="left", padx=5)

        # --- SECCIÓN 4: MONITOR ---
        self.frame_visual = ttk.LabelFrame(self, text="Monitor de Datos", padding="10")
        self.frame_visual.pack(padx=10, pady=5, fill="both", expand=True)

        ctrl_frame = ttk.Frame(self.frame_visual)
        ctrl_frame.pack(fill="x")
        ttk.Checkbutton(ctrl_frame, text="Ver Hexadecimal", variable=self.show_hex_var, command=self.refresh_ui_layout).pack(side="left")
        ttk.Button(ctrl_frame, text="Limpiar Terminal", command=self.clear_terminal).pack(side="right")

        self.panes = ttk.Panedwindow(self.frame_visual, orient=tk.HORIZONTAL)
        self.panes.pack(fill="both", expand=True)

        self.ascii_frame = ttk.LabelFrame(self.panes, text="ASCII")
        self.serial_text_ascii = tk.Text(self.ascii_frame, height=12, state='disabled', wrap='none')
        self.serial_text_ascii.pack(side="left", fill="both", expand=True)
        self.panes.add(self.ascii_frame)

        self.hex_frame = ttk.LabelFrame(self.panes, text="Hexadecimal")
        self.serial_text_hex = tk.Text(self.hex_frame, height=12, state='disabled', wrap='none', fg="blue")
        self.serial_text_hex.pack(side="left", fill="both", expand=True)
        self.panes.add(self.hex_frame)

    def select_file_path(self):
        fmt = self.export_format.get()
        ext = ".csv" if fmt == "CSV" else ".xlsx"
        default_name = f"MRCLog_{time.strftime('%Y%m%d_%H%M')}{ext}"
        path = filedialog.asksaveasfilename(initialfile=default_name, defaultextension=ext,
                                            filetypes=[("Archivos de datos", f"*{ext}")])
        if path:
            self.file_path = path
            self.path_button.config(text="✔ Archivo Listo")

    def toggle_log_options(self):
        if self.enable_log_var.get():
            self.log_options_container.grid(row=1, column=0, columnspan=4, sticky="ew", pady=5)
        else:
            self.log_options_container.grid_forget()

    def setup_csv_file(self):
        try:
            self.csv_file = open(self.file_path, mode='a', newline='', encoding='utf-8')
            self.csv_writer = csv.writer(self.csv_file)
            if self.csv_file.tell() == 0:
                sub_cols = [c.strip() for c in self.csv_column_names.get().split(',')]
                header = ["Timestamp"] + sub_cols + [self.data_column_name.get()]
                self.csv_writer.writerow(header)
        except Exception as e:
            messagebox.showerror("Error CSV", str(e))

    def save_excel_file(self):
        try:
            import pandas as pd
            df = pd.DataFrame(self.data_history)
            vals_df = df['Values'].apply(pd.Series)
            user_cols = [c.strip() for c in self.csv_column_names.get().split(',')]
            if len(user_cols) < len(vals_df.columns):
                user_cols += [f"Dato_{i}" for i in range(len(user_cols), len(vals_df.columns))]
            vals_df.columns = user_cols[:len(vals_df.columns)]
            final_df = pd.concat([df[['Timestamp']], vals_df, df[['Raw']]], axis=1)
            final_df.rename(columns={'Raw': self.data_column_name.get()}, inplace=True)
            final_df.to_excel(self.file_path, index=False)
            messagebox.showinfo("Excel", "Guardado exitosamente.")
            self.data_history = []
        except Exception as e:
            messagebox.showerror("Error Excel", f"Error al guardar: {str(e)}")

    def toggle_connection(self):
        if self.serial_object and self.serial_object.is_open:
            self.disconnect()
        else:
            self.connect()

    def connect(self):
        if self.enable_log_var.get():
            if not self.file_path: return messagebox.showwarning("Archivo", "Selecciona un archivo.")
            if self.export_format.get() == "CSV": self.setup_csv_file()
        try:
            self.serial_object = serial.Serial(self.port_combobox.get(), int(self.baud_combobox.get()), timeout=0.1)
            self.stop_event.clear()
            self.update_ui_state(True)
            threading.Thread(target=self.receive_thread, daemon=True).start()
        except Exception as e: messagebox.showerror("Error", str(e))

    def disconnect(self, silent=True):
        self.stop_event.set()
        if self.serial_object: self.serial_object.close()
        if self.enable_log_var.get() and self.export_format.get() == "Excel" and self.data_history: self.save_excel_file()
        if self.csv_file: self.csv_file.close(); self.csv_file = None
        self.update_ui_state(False)

    def receive_thread(self):
        while not self.stop_event.is_set():
            try:
                if self.serial_object.in_waiting > 0:
                    data = self.serial_object.read(self.serial_object.in_waiting).decode('utf-8', errors='replace')
                    self.buffer += data
                    while '\n' in self.buffer:
                        line, self.buffer = self.buffer.split('\n', 1)
                        self.after(0, self.process_line, line.strip())
            except: self.after(0, lambda: self.disconnect(silent=False)); break
            time.sleep(0.01)

    def process_line(self, line):
        if not line: return
        ts = time.strftime("%H:%M:%S")
        self.update_terminal(self.serial_text_ascii, f"[{ts}] {line}\n")
        if self.show_hex_var.get():
            h_line = ' '.join([f'{ord(c):02X}' for c in line])
            self.update_terminal(self.serial_text_hex, f"[{ts}] {h_line}\n")
        if self.enable_log_var.get():
            nums = self.extract_numbers(line)
            if self.export_format.get() == "CSV" and self.csv_writer:
                self.csv_writer.writerow([ts] + nums + [line])
                self.csv_file.flush()
            else:
                self.data_history.append({'Timestamp': ts, 'Raw': line, 'Values': nums})

    def extract_numbers(self, data):
        parts = data.split(',')
        extracted = []
        for p in parts:
            match = re.search(r"[-+]?\d*\.?\d+", p)
            extracted.append(match.group(0) if match else "")
        return extracted

    def update_ui_state(self, connected):
        state = tk.NORMAL if connected else tk.DISABLED
        self.send_entry.config(state=state)
        self.send_button.config(state=state)
        self.connect_button.config(text="Desconectar" if connected else "Conectar")
        self.title(f"MRC SerialPortCtrl - {'Conectado' if connected else 'Desconectado'}")

    def send_data(self):
        if self.serial_object and self.serial_object.is_open:
            msg = self.send_entry.get()
            if msg:
                try:
                    self.serial_object.write((msg + '\n').encode('utf-8'))
                    self.send_entry.delete(0, 'end')
                except Exception as e: messagebox.showerror("Error de Envío", str(e))

    def update_terminal(self, widget, text):
        widget.config(state='normal'); widget.insert('end', text); widget.see('end'); widget.config(state='disabled')

    def refresh_ui_layout(self):
        if self.show_hex_var.get():
            if str(self.hex_frame) not in self.panes.panes(): self.panes.add(self.hex_frame)
        else:
            if str(self.hex_frame) in self.panes.panes(): self.panes.forget(self.hex_frame)

    def list_ports(self):
        ports = serial.tools.list_ports.comports()
        self.port_combobox['values'] = [p.device for p in ports]
        if ports: self.port_combobox.set(ports[0].device)

    def clear_terminal(self):
        for w in [self.serial_text_ascii, self.serial_text_hex]:
            w.config(state='normal'); w.delete('1.0', 'end'); w.config(state='disabled')

if __name__ == "__main__":
    app = SerialPyInterface()
    app.mainloop()
