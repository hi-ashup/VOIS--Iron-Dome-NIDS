import tkinter as tk
from tkinter import ttk, font, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import seaborn as sns
from engine import NIDSEngine
import datetime
import os

# --- CONFIGURATION ---
COLOR_BG = "#141414"
COLOR_CARD = "#1f1f1f"
COLOR_ACCENT = "#E50914"    # Netflix Red
COLOR_IMPERIAL = "#ED2939"  # Imperial Red
COLOR_YELLOW = "#FFD700"    # Gold/Yellow
COLOR_TEXT = "#FFFFFF"
COLOR_SUBTEXT = "#B3B3B3"
COLOR_TERMINAL = "#00FF00"

# --- HIGH DPI FIX ---
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

class RoundedButton(tk.Canvas):
    """
    A Custom Button created using Canvas to achieve the 'Pill/Rounded' shape.
    Now includes cursor="hand2" for the hover effect.
    """
    def __init__(self, parent, text, command, bg, fg, width=150, height=40, corner_radius=20):
        # FIX: Added cursor="hand2" here to change pointer on hover
        super().__init__(parent, borderwidth=0, highlightthickness=0, bg=parent["bg"], cursor="hand2")
        self.command = command
        self.bg_color = bg
        self.fg_color = fg
        self.width = width
        self.height = height
        self.corner_radius = corner_radius

        self.config(width=self.width, height=self.height)

        self.rect = self._draw_rounded_rect()
        self.text = self.create_text(self.width/2, self.height/2, text=text, 
                                     fill=self.fg_color, font=("Segoe UI", 10, "bold"))

        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)

    def _draw_rounded_rect(self):
        r = self.corner_radius
        w = self.width
        h = self.height
        shape = self.create_polygon(
            r, 0, w-r, 0, w, 0, w, r, w, h-r, w, h, w-r, h, r, h, 0, h, 0, h-r, 0, r, 0, 0,
            smooth=True, fill=self.bg_color, outline=""
        )
        return shape

    def _on_click(self, event):
        if self.command:
            self.command()

    def _on_hover(self, event):
        # Optional: Add brightness effect here if desired
        pass 

    def _on_leave(self, event):
        pass

    def config_text(self, text):
        self.itemconfig(self.text, text=text)

class NIDS_GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.engine = NIDSEngine()
        self.selected_csv_path = None 
        self.latest_metrics = None 
        
        self.title("NIDS | IRON DOME PROTOTYPE")
        self.geometry("1400x950")
        self.configure(bg=COLOR_BG)
        
        # Fonts
        self.font_hero = font.Font(family="Segoe UI", size=32, weight="bold")
        self.font_h2 = font.Font(family="Segoe UI", size=16, weight="bold")
        self.font_body = font.Font(family="Segoe UI", size=11)
        self.font_bold = font.Font(family="Segoe UI", size=11, weight="bold")
        self.font_mono = font.Font(family="Consolas", size=10)

        # Style Configuration for Dropdown
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TCombobox", 
                             fieldbackground="white", 
                             background="white", 
                             foreground="black",
                             arrowcolor="black")
        self.style.map('TCombobox', fieldbackground=[('readonly', 'white')],
                                    selectbackground=[('readonly', 'lightblue')],
                                    selectforeground=[('readonly', 'black')])

        self._init_layout_structure()

    def _init_layout_structure(self):
        main_container = tk.Frame(self, bg=COLOR_BG)
        main_container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(main_container, bg=COLOR_BG, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(main_container, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.content_frame = tk.Frame(self.canvas, bg=COLOR_BG)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")

        self.content_frame.bind('<Configure>', self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.bind_all("<MouseWheel>", self._on_mousewheel)

        self._build_centered_layout()

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _build_centered_layout(self):
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=8)
        self.content_frame.grid_columnconfigure(2, weight=1)

        main_stage = tk.Frame(self.content_frame, bg=COLOR_BG)
        main_stage.grid(row=0, column=1, sticky="nsew", pady=20)
        main_stage.grid_columnconfigure(0, weight=1)

        self._build_navbar(main_stage)
        
        # Split main stage for Left/Right columns
        split_frame = tk.Frame(main_stage, bg=COLOR_BG)
        split_frame.pack(fill=tk.BOTH, expand=True)
        split_frame.grid_columnconfigure(0, weight=1, uniform="group1")
        split_frame.grid_columnconfigure(1, weight=1, uniform="group1")

        left_col = tk.Frame(split_frame, bg=COLOR_BG)
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        right_col = tk.Frame(split_frame, bg=COLOR_BG)
        right_col.grid(row=0, column=1, sticky="nsew", padx=(15, 0))

        # Left Widgets
        self._build_hero(left_col)
        self._create_card(left_col, "Configuration", self._build_controls)
        self._create_card(left_col, "Performance Metrics", self._build_metrics)

        # Right Widgets
        self.viz_frame = self._create_card(right_col, "Visual Diagnostics", None)
        self._create_card(right_col, "Live Packet Injection Stimulation", self._build_simulator)

        self._build_terminal(main_stage)

    def _build_navbar(self, parent):
        nav_frame = tk.Frame(parent, bg=COLOR_BG, height=60)
        nav_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(nav_frame, text="NIDS", font=("Impact", 28), fg=COLOR_ACCENT, bg=COLOR_BG).pack(side=tk.LEFT)
        tk.Label(nav_frame, text=" |  Network Defense System", font=self.font_h2, fg=COLOR_SUBTEXT, bg=COLOR_BG).pack(side=tk.LEFT, padx=10, pady=5)

        self.btn_report = RoundedButton(nav_frame, text="⇩ REPORT", bg="white", fg="black", command=self.generate_pdf_report, width=120, height=35)
        self.btn_report.pack(side=tk.RIGHT, padx=10)

    def _build_hero(self, parent):
        hero_frame = tk.Frame(parent, bg=COLOR_CARD, height=280)
        hero_frame.pack(fill=tk.X, pady=(0, 20))
        hero_frame.pack_propagate(False)
        
        inner = tk.Frame(hero_frame, bg=COLOR_CARD)
        inner.place(relx=0.03, rely=0.1, relwidth=0.94, relheight=0.85)

        tk.Label(inner, text="#1 Trending in Cyber Defense", font=("Segoe UI", 10, "bold"), fg=COLOR_ACCENT, bg=COLOR_CARD).pack(anchor="w")
        tk.Label(inner, text="SYSTEM STATUS: WAITING", font=self.font_hero, fg=COLOR_TEXT, bg=COLOR_CARD).pack(anchor="w", pady=(5,0))
        tk.Label(inner, text="Select Data Source and Initialize Model to begin traffic analysis.", 
                 font=self.font_body, fg=COLOR_SUBTEXT, bg=COLOR_CARD).pack(anchor="w", pady=(5, 15))
        
        btn_row = tk.Frame(inner, bg=COLOR_CARD)
        btn_row.pack(anchor="w", pady=(5, 0))

        self.train_btn = RoundedButton(btn_row, text="INITIALIZE MODEL", command=self.run_training,
                                       bg=COLOR_YELLOW, fg="black", width=180, height=45)
        self.train_btn.pack(side=tk.LEFT, padx=(0, 20))

        self.clear_btn = RoundedButton(btn_row, text="CLEAR SYSTEM", command=self.reset_system,
                                       bg="white", fg="black", width=150, height=45)
        self.clear_btn.pack(side=tk.LEFT)

    def _build_terminal(self, parent):
        term_label = tk.Label(parent, text="SYSTEM LOGS", font=self.font_bold, fg=COLOR_SUBTEXT, bg=COLOR_BG)
        term_label.pack(anchor="w", pady=(10, 5))
        self.terminal_text = tk.Text(parent, height=8, bg="black", fg=COLOR_TERMINAL, 
                                     font=self.font_mono, borderwidth=0, insertbackground="white")
        self.terminal_text.pack(fill=tk.X, pady=(0, 20))
        self.log("NIDS KERNEL INITIALIZED... WAITING FOR TRAINING COMMAND.")

    def _create_card(self, parent, title, widget_builder):
        card = tk.Frame(parent, bg=COLOR_CARD)
        card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        header = tk.Label(card, text=title, font=self.font_h2, fg=COLOR_TEXT, bg=COLOR_CARD)
        header.pack(anchor="w", padx=20, pady=(20, 10))
        content = tk.Frame(card, bg=COLOR_CARD)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        if widget_builder: widget_builder(content)
        return content

    def _build_controls(self, parent):
        tk.Label(parent, text="DATA SOURCE", fg=COLOR_SUBTEXT, bg=COLOR_CARD, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        
        self.source_var = tk.StringVar(value="Synthetic Simulation")
        self.source_cb = ttk.Combobox(parent, textvariable=self.source_var, state="readonly", font=("Segoe UI", 10))
        self.source_cb['values'] = ("Synthetic Simulation", "Real Dataset (CIC-IDS2017 CSV)")
        self.source_cb.pack(fill=tk.X, pady=(5, 15))

        self.source_cb.bind("<<ComboboxSelected>>", self._on_source_selected)

        self.split_var = tk.IntVar(value=80)
        self.tree_var = tk.IntVar(value=100)
        self._slider(parent, "Training Split (%)", 50, 90, self.split_var)
        self._slider(parent, "Random Forest Trees", 10, 200, self.tree_var)

    def _on_source_selected(self, event):
        selection = self.source_var.get()
        if selection == "Real Dataset (CIC-IDS2017 CSV)":
            file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
            if file_path:
                self.selected_csv_path = file_path
                self.log(f"File Selected: {os.path.basename(file_path)}")
            else:
                self.source_var.set("Synthetic Simulation")
                self.selected_csv_path = None
                self.log("Selection Cancelled. Reverting to Synthetic.")
        else:
            self.selected_csv_path = None

    def _slider(self, parent, label, min_v, max_v, var):
        tk.Label(parent, text=label, fg=COLOR_SUBTEXT, bg=COLOR_CARD, font=self.font_body).pack(anchor="w")
        s = tk.Scale(parent, from_=min_v, to=max_v, orient=tk.HORIZONTAL, variable=var, 
                     bg=COLOR_CARD, fg=COLOR_TEXT, troughcolor="#333", highlightthickness=0, length=250)
        s.pack(fill=tk.X, pady=(5, 15))

    def _build_metrics(self, parent):
        self.lbl_acc = tk.Label(parent, text="Accuracy: --", fg=COLOR_TEXT, bg=COLOR_CARD, font=("Segoe UI", 22))
        self.lbl_acc.pack(anchor="w")
        self.lbl_threats = tk.Label(parent, text="Threats Detected: --", fg=COLOR_ACCENT, bg=COLOR_CARD, font=("Segoe UI", 22, "bold"))
        self.lbl_threats.pack(anchor="w", pady=(5, 0))

    def _build_simulator(self, parent):
        inputs_frame = tk.Frame(parent, bg=COLOR_CARD)
        inputs_frame.pack(fill=tk.X)
        self.e_dur = self._entry(inputs_frame, "Duration (ms)", 500, 0, 0)
        self.e_pkt = self._entry(inputs_frame, "Total Packets", 100, 0, 1)
        self.e_len = self._entry(inputs_frame, "Length (Mean)", 500, 1, 0)
        self.e_act = self._entry(inputs_frame, "Active Time", 50, 1, 1)
        
        btn = RoundedButton(parent, text="INJECT PACKET", command=self.simulate_attack,
                           bg=COLOR_IMPERIAL, fg="white", width=250, height=45)
        btn.pack(pady=(25, 0))

    def _entry(self, parent, label, default, row, col):
        f = tk.Frame(parent, bg=COLOR_CARD)
        f.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)
        tk.Label(f, text=label, fg=COLOR_SUBTEXT, bg=COLOR_CARD, font=("Segoe UI", 9)).pack(anchor="w")
        e = tk.Entry(f, bg="#333", fg=COLOR_TEXT, insertbackground="white", relief=tk.FLAT, font=self.font_bold)
        e.insert(0, str(default))
        e.pack(fill=tk.X, ipady=5)
        return e

    def log(self, message):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.terminal_text.insert(tk.END, f"[{ts}] root@nids:~$ {message}\n")
        self.terminal_text.see(tk.END)

    # --- ACTIONS ---
    def reset_system(self):
        self.engine = NIDSEngine()
        self.latest_metrics = None
        self.selected_csv_path = None
        self.source_var.set("Synthetic Simulation")
        
        self.lbl_acc.config(text="Accuracy: --")
        self.lbl_threats.config(text="Threats Detected: --")
        self.train_btn.config_text("INITIALIZE MODEL")
        
        for widget in self.viz_frame.winfo_children():
            widget.destroy()
            
        self.log("SYSTEM RESET. Awaiting new data configuration.")
        messagebox.showinfo("System Reset", "Model and Data have been cleared.\nReady for new experiment.")

    def run_training(self):
        source = self.source_var.get()
        file_path = self.selected_csv_path
        
        if source == "Real Dataset (CIC-IDS2017 CSV)" and not file_path:
            messagebox.showwarning("Missing File", "Please select a CSV file first.")
            return

        mode = 'csv' if source == "Real Dataset (CIC-IDS2017 CSV)" else 'synthetic'

        self.log(f"Loading data via [{mode.upper()}] engine...")
        self.update()
        
        try:
            count = self.engine.load_data(mode, file_path)
            self.log(f"Data Loaded: {count} records. Initializing Random Forest...")
            self.update()
            
            self.engine.train(self.split_var.get(), self.tree_var.get())
            
            self.latest_metrics = self.engine.get_metrics()
            
            self.lbl_acc.config(text=f"Accuracy: {self.latest_metrics['accuracy']*100:.2f}%")
            self.lbl_threats.config(text=f"Threats Detected: {self.latest_metrics['threats']}")
            self._plot_cm(self.latest_metrics['cm'])
            
            self.log(f"Training Complete. Accuracy: {self.latest_metrics['accuracy']*100:.2f}%")
            self.train_btn.config_text("RETRAIN MODEL")
            
        except Exception as e:
            self.log(f"CRITICAL ERROR: {str(e)}")
            messagebox.showerror("Error", str(e))

    def _plot_cm(self, cm):
        for widget in self.viz_frame.winfo_children(): 
            widget.destroy()
            
        fig = plt.Figure(figsize=(5, 5.5), dpi=100, facecolor=COLOR_CARD)
        ax = fig.add_subplot(111)
        ax.set_facecolor(COLOR_CARD)
        
        sns.heatmap(cm, annot=True, fmt='d', cmap='Reds', ax=ax, cbar=False,
                    annot_kws={"weight": "bold", "size": 12})
        
        ax.set_xlabel('Predicted Label', color='white', fontsize=10)
        ax.set_ylabel('Actual Label', color='white', fontsize=10)
        ax.tick_params(colors='white', labelsize=9)
        
        fig.subplots_adjust(bottom=0.20, top=0.92, left=0.15, right=0.95)
        
        canvas = FigureCanvasTkAgg(fig, self.viz_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        try:
            tn, fp, fn, tp = cm.ravel()
            summary_text = (
                f"✅ Safe Traffic Verified: {tn:,}   |   🛡️ Threats Blocked: {tp:,}\n"
                f"⚠️ False Alarms: {fp}   |   🚫 Missed Attacks: {fn}"
            )
            lbl_explain = tk.Label(self.viz_frame, text=summary_text, justify="center",
                                   bg=COLOR_CARD, fg=COLOR_SUBTEXT, font=("Segoe UI", 10))
            lbl_explain.pack(pady=(5, 0))
        except Exception:
            pass

    def simulate_attack(self):
        try:
            feats = [float(x.get()) for x in [self.e_dur, self.e_pkt, self.e_len, self.e_act]]
            res = self.engine.predict_single(feats)
            if res == -1:
                self.log("ERROR: Model not mounted. Train first.")
                return
            if res == 1:
                self.log("ALERT: MALICIOUS PACKET DROPPED.")
                messagebox.showwarning("NIDS ALERT", "High-severity threat detected!\n\nType: DoS/PortScan")
            else:
                self.log("Packet verified. Traffic benign.")
        except ValueError:
            self.log("Input error. Check numeric fields.")

    def generate_pdf_report(self):
        if not self.latest_metrics:
            messagebox.showwarning("Report Error", "Please train the model before generating a report.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", 
                                                 filetypes=[("PDF Documents", "*.pdf")],
                                                 initialfile="NIDS_Security_Report.pdf")
        if not file_path: return

        try:
            with PdfPages(file_path) as pdf:
                fig = plt.figure(figsize=(8.5, 11))
                fig.suptitle('NIDS Iron Dome - Security Audit Report', fontsize=20, weight='bold')
                
                report_text = (
                    f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Operator: Root\n"
                    f"Data Source: {self.source_var.get()}\n\n"
                    f"--- MODEL PERFORMANCE ---\n\n"
                    f"Total Records Analyzed: 5000+\n"
                    f"Model Accuracy: {self.latest_metrics['accuracy']*100:.2f}%\n"
                    f"Total Threats Intercepted: {self.latest_metrics['threats']}\n"
                    f"Algorithm: Random Forest Classifier\n"
                    f"Trees: {self.tree_var.get()} | Split: {self.split_var.get()}%\n\n"
                    f"--- STATUS ---\n"
                    f"System Status: ONLINE\n"
                    f"Threat Level: MODERATE\n"
                )
                
                fig.text(0.1, 0.6, report_text, fontsize=12, fontfamily='monospace')
                fig.text(0.5, 0.05, "Confidential - Internal Use Only", ha='center', fontsize=10, color='gray')
                pdf.savefig(fig)
                plt.close(fig)

                fig_cm = plt.figure(figsize=(8.5, 11))
                ax = fig_cm.add_subplot(211)
                
                sns.heatmap(self.latest_metrics['cm'], annot=True, fmt='d', cmap='Reds', ax=ax,
                            annot_kws={"weight": "bold", "size": 12})
                            
                ax.set_title("Confusion Matrix: Attack Detection Verification")
                ax.set_xlabel('Predicted Label')
                ax.set_ylabel('Actual Label')
                
                explanation_text = (
                    "GUIDE TO VISUAL DIAGNOSTICS (How to read this graph):\n"
                    "----------------------------------------------------\n"
                    "The Confusion Matrix compares the AI's predictions vs Reality.\n\n"
                    "1. Top-Left (0,0) - TRUE NEGATIVES:\n"
                    "   Safe traffic correctly identified as Safe.\n\n"
                    "2. Bottom-Right (1,1) - TRUE POSITIVES:\n"
                    "   Attacks correctly identified and blocked.\n\n"
                    "3. Top-Right (0,1) - FALSE ALARMS:\n"
                    "   Safe traffic mistakenly flagged as an attack.\n\n"
                    "4. Bottom-Left (1,0) - MISSED ATTACKS:\n"
                    "   Attacks that slipped past the system (False Negatives).\n\n"
                    "Note: High numbers in the diagonal (Top-Left to Bottom-Right)\n"
                    "indicate a healthy, accurate model."
                )
                
                fig_cm.text(0.1, 0.15, explanation_text, fontsize=11, fontfamily='monospace',
                            bbox=dict(facecolor='#f0f0f0', alpha=0.5))

                pdf.savefig(fig_cm)
                plt.close(fig_cm)

            self.log(f"Report generated successfully: {os.path.basename(file_path)}")
            messagebox.showinfo("Report Ready", "PDF Report saved successfully.")

        except Exception as e:
            self.log(f"Report Generation Failed: {e}")
            messagebox.showerror("Error", f"Could not save report: {e}")

if __name__ == "__main__":
    app = NIDS_GUI()
    app.mainloop()