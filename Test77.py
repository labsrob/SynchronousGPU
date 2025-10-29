import tkinter as tk
from tkinter import ttk
import threading, time, random, math, os
from datetime import datetime
import numpy as np
import pandas as pd
from queue import Queue
from sqlalchemy import create_engine, text
import pygame
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.stats import norm


class collectiveEoP(ttk.Frame):
    def __init__(self, master=None, pWON="20251028"):
        super().__init__(master)
        self.place(x=10, y=10)
        self.running = False

        # ------------------------------------------
        # Visualization + Process Parameters
        # ------------------------------------------
        self.WIDTH, self.HEIGHT = 850, 450
        self.BASE_DIAMETER_PX = 150
        self.TAPE_THICKNESS_PX = 0.2
        self.PIXELS_PER_METER = 10
        self.PIPE_COLOR = (40, 40, 40)
        self.TAPE_COLORS = [(180, 180, 255), (120, 200, 255)]
        self.PIPE_LENGTH_METERS = 100
        self.WRAP_SPEED = 1.2
        self.SAMPLING_RESOLUTION = 0.25
        self.wrap_count, self.pipe_position, self.flow_phase, self.direction = 0, 0.0, 0.0, 1

        # ------------------------------------------
        # SQL Tables / Templates
        # ------------------------------------------
        self.QRP = f"XRP_{pWON}"
        self.QTT = f"XTT_{pWON}"
        self.QST = f"XST_{pWON}"

        self.dT1, self.dT2, self.dT3 = '[dbo].[18_EoPRP]', '[dbo].[19_EoPTT]', '[dbo].[20_EoPST]'

        # ------------------------------------------
        # SQL Connection Setup
        # ------------------------------------------
        self.SERVER = '10.0.3.172'
        self.DATABASE = "DAQ_sSPC"
        self.USERNAME = "TCP01"
        self.PASSWORD = "Testing27!"
        self.clone_rp, self.clone_tt, self.clone_st = '[dbo].[18_EoPRP]', '[dbo].[19_EoPTT]', '[dbo].[20_EoPST]'
        self.conn_str = f"mssql+pyodbc://{self.USERNAME}:{self.PASSWORD}@{self.SERVER}/{self.DATABASE}?driver=ODBC+Driver+17+for+SQL+Server"
        self.engine = create_engine(self.conn_str)

        # ------------------------------------------
        # Data & Thread Control
        # ------------------------------------------
        self.export_queue = Queue()
        self.data_lock = threading.Lock()
        self.running = True

        # Create / verify SQL tables
        self.create_table_from_template(
            self.engine, self.QRP, self.QTT, self.QST,
            self.dT1, self.dT2, self.dT3
        )

        # Initialize UI & simulation
        self.createEoPViz()

        # Start background threads
        threading.Thread(target=self.data_worker, daemon=True).start()
        threading.Thread(target=self.export_worker, daemon=True).start()

        # Start animation loop in Tkinter mainloop
        self.after(100, self.update_loop)

    # ======================================================================
    # Table verification and creation
    # ======================================================================
    def table_exists(self, engine, schema_name, table_name):
        try:
            with engine.begin() as conn:
                query = text("""
                    SELECT CASE 
                        WHEN EXISTS (
                            SELECT 1 
                            FROM INFORMATION_SCHEMA.TABLES 
                            WHERE TABLE_SCHEMA = :schema 
                              AND TABLE_NAME = :table
                        )
                        THEN 'Yes'
                        ELSE 'No'
                    END AS table_exists
                """)
                result = conn.execute(query, {"schema": schema_name, "table": table_name})
                return result.scalar()
        except Exception as e:
            print(f"[SQL] Error checking table: {e}")
            return None

    def create_table_from_template(self, engine, newT1, newT2, newT3, dT1, dT2, dT3):
        try:
            existsA = self.table_exists(engine, "dbo", newT1.replace("[dbo].[", "").replace("]", ""))
            existsB = self.table_exists(engine, "dbo", newT2.replace("[dbo].[", "").replace("]", ""))
            existsC = self.table_exists(engine, "dbo", newT3.replace("[dbo].[", "").replace("]", ""))
            print(f"[SQL] Exists -> RP:{existsA}, TT:{existsB}, ST:{existsC}")
        except Exception:
            print('[SQL] Table existence check failed')

        if existsA == 'No' or existsB == 'No' or existsC == 'No':
            try:
                with engine.begin() as conn:
                    conn.execute(text(f"SELECT TOP 0 * INTO {newT1} FROM {dT1}"))
                    conn.execute(text(f"SELECT TOP 0 * INTO {newT2} FROM {dT2}"))
                    conn.execute(text(f"SELECT TOP 0 * INTO {newT3} FROM {dT3}"))
                print(f"[SQL] Created new tables: {newT1}, {newT2}, {newT3}")
            except Exception as e:
                print('[SQL] Error creating new tables:', e)
        else:
            print('[SQL] Tables already exist.')

    # ======================================================================
    # UI & Visualization
    # ======================================================================
    def createEoPViz(self):
        # Split frames
        self.sim_frame = tk.Frame(self, bg="black", width=845, height=450)
        self.sim_frame.pack(side="left", fill="both", expand=True)
        self.sim_frame.update_idletasks()

        self.plot_container = tk.Frame(self, bg="#222", width=1250, height=450)
        self.plot_container.pack(side="right", fill="both", expand=True)

        # Toggle frame
        toggle_frame = tk.Frame(self.plot_container, bg="#111")
        toggle_frame.pack(side="top", fill="x", pady=4)

        self.show_pressure = tk.BooleanVar(value=True)
        self.show_temp = tk.BooleanVar(value=True)
        self.show_substrate = tk.BooleanVar(value=True)

        ttk.Checkbutton(toggle_frame, text="Consolidated Pressure", variable=self.show_pressure).pack(side="left", padx=10)
        ttk.Checkbutton(toggle_frame, text="Tape Temperature", variable=self.show_temp).pack(side="left", padx=10)
        ttk.Checkbutton(toggle_frame, text="Substrate Temperature", variable=self.show_substrate).pack(side="left", padx=10)

        self.sql_status_var = tk.StringVar(value="SQL: Idle")
        self.sql_label = tk.Label(toggle_frame, textvariable=self.sql_status_var, fg="#ccc", bg="#111", font=("Consolas", 11))
        self.sql_label.pack(side="right", padx=15)

        # Pygame embedding
        os.environ['SDL_WINDOWID'] = str(self.sim_frame.winfo_id())
        os.environ['SDL_VIDEODRIVER'] = 'windib'
        pygame.display.init()
        pygame.font.init()
        pygame.display.set_mode((850, 450))
        self.surface = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.start_time = time.time()

        # Matplotlib setup
        self.fig = Figure(figsize=(17, 8), dpi=100)
        self.ax_ts = self.fig.add_subplot(2, 3, (1, 3))
        self.ax_hist_p = self.fig.add_subplot(2, 3, 4)
        self.ax_hist_t = self.fig.add_subplot(2, 3, 5)
        self.ax_hist_sub = self.fig.add_subplot(2, 3, 6)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_container)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Initialize data lists
        self.pressures, self.temps, self.substrate_temps = [], [], []
        self.positions = []
        self.rolling_means_p, self.rolling_stds_p = [], []
        self.rolling_means_t, self.rolling_stds_t = [], []
        self.rolling_means_sub, self.rolling_stds_sub = [], []

    # ======================================================================
    # Data Worker (Simulated PLC reader)
    # ======================================================================
    def data_worker(self):
        while self.running:
            start_time = time.time()
            # Placeholder for real PLC read
            pressure = random.uniform(80, 120)
            tape_temp = random.uniform(20, 60)
            substrate_temp = random.uniform(40, 65)

            with self.data_lock:
                self.pressures.append(pressure)
                self.temps.append(tape_temp)
                self.substrate_temps.append(substrate_temp)
                self.positions.append(self.pipe_position)

                window = 30
                self.rolling_means_p.append(np.mean(self.pressures[-window:]))
                self.rolling_stds_p.append(np.std(self.pressures[-window:]))
                self.rolling_means_t.append(np.mean(self.temps[-window:]))
                self.rolling_stds_t.append(np.std(self.temps[-window:]))
                self.rolling_means_sub.append(np.mean(self.substrate_temps[-window:]))
                self.rolling_stds_sub.append(np.std(self.substrate_temps[-window:]))

            elapsed = time.time() - start_time
            time.sleep(max(0, 0.1 - elapsed))  # 10 Hz

    # ======================================================================
    # Visualization update loop
    # ======================================================================
    def update_loop(self):
        if not self.running:
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.on_close()

        # Update pipe position
        if self.pipe_position >= 100:
            self.direction = -1
        elif self.pipe_position <= 0:
            self.direction = 1
        self.pipe_position += self.direction * 0.25

        # Draw visuals
        self.surface.fill((0, 0, 0))
        self.draw_helical_pipe(self.surface)
        pygame.display.flip()

        # Update matplotlib plots
        self.update_plots()

        self.clock.tick(30)
        self.after(200, self.update_loop)


    def draw_helical_pipe(self, surface):
        y_center = self.HEIGHT // 2
        diameter = self.BASE_DIAMETER_PX + (self.wrap_count * self.TAPE_THICKNESS_PX)
        radius = diameter / 2
        pygame.draw.rect(surface, self.PIPE_COLOR, (0, y_center - radius, self.WIDTH, diameter),
                         border_radius=int(radius))

        stripe_count = 10
        base_color = self.TAPE_COLORS[int(self.wrap_count) % len(self.TAPE_COLORS)]
        for i in range(stripe_count):
            phase_shift = self.flow_phase + (i * (math.pi * 2 / stripe_count))
            points = [(x, y_center + radius * math.sin(0.02 * x + phase_shift * self.direction)) for x in range(0, self.WIDTH, 8)]
            pygame.draw.lines(surface, base_color, False, points, 3)

        self.flow_phase += 0.1 * self.direction
        self.wrap_count += abs(self.direction) * 0.01

    # ======================================================================
    # Plot updates
    # ======================================================================
    def update_plots(self):
        self.ax_ts.clear(); self.ax_hist_p.clear(); self.ax_hist_t.clear(); self.ax_hist_sub.clear()
        if not self.positions:
            return

        def plot_line(ax, pos, data, mean, std, color, label, show):
            if not show: return
            ax.plot(pos, data, color=color, alpha=0.3)
            ax.plot(pos, mean, color=color, lw=2, label=label)
            ax.fill_between(pos, mean - std, mean + std, color=color, alpha=0.2)

        with self.data_lock:
            p_mean, p_std = np.array(self.rolling_means_p), np.array(self.rolling_stds_p)
            t_mean, t_std = np.array(self.rolling_means_t), np.array(self.rolling_stds_t)
            s_mean, s_std = np.array(self.rolling_means_sub), np.array(self.rolling_stds_sub)

            plot_line(self.ax_ts, self.positions, self.pressures, p_mean, p_std, "purple", "Pressure ±σ", self.show_pressure.get())
            plot_line(self.ax_ts, self.positions, self.temps, t_mean, t_std, "red", "Tape Temp ±σ", self.show_temp.get())
            plot_line(self.ax_ts, self.positions, self.substrate_temps, s_mean, s_std, "lime", "Substrate ±σ", self.show_substrate.get())

        self.ax_ts.set_title("Live Time-Series")
        self.ax_ts.legend(loc="upper left")
        self.ax_ts.grid(True)

        for ax, data, color, label, show in [
            (self.ax_hist_p, self.pressures, "purple", "Roller Pressure", self.show_pressure.get()),
            (self.ax_hist_t, self.temps, "red", "Tape Temp", self.show_temp.get()),
            (self.ax_hist_sub, self.substrate_temps, "green", "Substrate Temp", self.show_substrate.get())
        ]:
            if show and len(data) > 2:
                ax.hist(data, bins=20, density=True, alpha=0.4, color=color)
                mu, std = np.mean(data), np.std(data)
                x = np.linspace(min(data), max(data), 100)
                ax.plot(x, norm.pdf(x, mu, std), color=color, lw=2)
                ax.set_title(f"{label} (μ={mu:.2f}, σ={std:.2f})")
                ax.grid(True)

        self.canvas.draw()

    # ======================================================================
    # SQL Export worker
    # ======================================================================
    def export_worker(self):
        while self.running:
            time.sleep(5)
            with self.data_lock:
                if len(self.positions) < 40:
                    continue
                df = pd.DataFrame({
                    "pipe_pos": self.positions[-40:],
                    "rollerpressure": self.pressures[-40:],
                    "tapetemperature": self.temps[-40:],
                    "substtemprature": self.substrate_temps[-40:],
                })
            try:
                df.to_sql(self.clone_rp, self.engine, if_exists='append', index=False)
                df.to_sql(self.clone_tt, self.engine, if_exists='append', index=False)
                df.to_sql(self.clone_st, self.engine, if_exists='append', index=False)
                self.sql_status_var.set("SQL: Idle")
            except Exception as e:
                print("[SQL ERROR]", e)
                self.sql_status_var.set("SQL: ERROR")

    # ======================================================================
    # Cleanup
    # ======================================================================
    def on_close(self):
        self.running = False
        self.engine.dispose()
        pygame.quit()
        self.destroy()
