import tkinter as tk
from tkinter import ttk
import threading, time, random, os
import pygame
import numpy as np
import pandas as pd
from queue import Queue
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sqlalchemy import create_engine, text

class collectiveEoP(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.place(x=10, y=10)
        self.running = True

        # --------------------------
        # Pipe & visualization params
        # --------------------------
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

        # --------------------------
        # Data storage
        # --------------------------
        self.pressures, self.temps, self.substrate_temps = [], [], []
        self.positions = []
        self.rolling_means_p, self.rolling_stds_p = [], []
        self.rolling_means_t, self.rolling_stds_t = [], []
        self.rolling_means_sub, self.rolling_stds_sub = [], []

        # --------------------------
        # SQL & export queue
        # --------------------------
        self.SERVER = '10.0.3.172'
        self.DATABASE = "DAQ_sSPC"
        self.USERNAME = "TCP01"
        self.PASSWORD = "Testing27!"
        self.clone_rp, self.clone_tt, self.clone_st = '[dbo].[18_EoPRP]', '[dbo].[19_EoPTT]', '[dbo].[20_EoPST]'
        self.conn_str = f"mssql+pyodbc://{self.USERNAME}:{self.PASSWORD}@{self.SERVER}/{self.DATABASE}?driver=ODBC+Driver+17+for+SQL+Server"
        self.engine = create_engine(self.conn_str)
        self.export_queue = Queue()

        # --------------------------
        # Initialize tab5 container for visualization
        # --------------------------
        self.init_visualization(master)

        # --------------------------
        # Start threads
        # --------------------------
        threading.Thread(target=self.data_worker, daemon=True).start()
        threading.Thread(target=self.update_loop, daemon=True).start()
        threading.Thread(target=self.export_worker, daemon=True).start()

    # --------------------------
    # Visualization Setup
    # --------------------------
    def init_visualization(self, master):
        # Use master (tab5) as parent
        self.sim_frame = tk.Frame(master, bg="black", width=850, height=450)
        self.sim_frame.pack(side="left", fill="both", expand=True)
        self.sim_frame.update()

        self.plot_container = tk.Frame(master, bg="#222", width=1250, height=450)
        self.plot_container.pack(side="right", fill="both", expand=True)

        # Toggle checkboxes
        toggle_frame = tk.Frame(self.plot_container, bg="#111")
        toggle_frame.pack(side="top", fill="x", pady=4)
        self.show_pressure = tk.BooleanVar(value=True)
        self.show_temp = tk.BooleanVar(value=True)
        self.show_substrate = tk.BooleanVar(value=True)
        ttk.Checkbutton(toggle_frame, text="Consolidated Pressure", variable=self.show_pressure).pack(side="left", padx=10)
        ttk.Checkbutton(toggle_frame, text="Tape Temperature", variable=self.show_temp).pack(side="left", padx=10)
        ttk.Checkbutton(toggle_frame, text="Substrate Temperature", variable=self.show_substrate).pack(side="left", padx=10)

        # Matplotlib figure
        self.fig = Figure(figsize=(12, 7), dpi=100)
        self.fig.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, wspace=0.18, hspace=0.2)
        self.ax_ts = self.fig.add_subplot(2, 3, (1, 3))
        self.ax_hist_p = self.fig.add_subplot(2, 3, 4)
        self.ax_hist_t = self.fig.add_subplot(2, 3, 5)
        self.ax_hist_sub = self.fig.add_subplot(2, 3, 6)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_container)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Embed Pygame in sim_frame
        os.environ['SDL_WINDOWID'] = str(self.sim_frame.winfo_id())
        os.environ['SDL_VIDEODRIVER'] = 'windib'
        pygame.display.init()
        pygame.font.init()
        pygame.display.set_mode((850, 450))
        self.surface = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.start_time = time.time()

    # --------------------------
    # Data Worker (PLC/SQL Template)
    # --------------------------
    def data_worker(self):
        """
        Reads PLC data at 10 Hz and pushes to internal lists / queue
        """
        while self.running:
            start_time = time.time()
            # TODO: Replace below with actual PLC read
            pressure, tape_temp, substrate_temp = random.uniform(80, 120), random.uniform(20, 60), random.uniform(40, 65)

            # Append to lists
            self.positions.append(self.pipe_position)
            self.pressures.append(pressure)
            self.temps.append(tape_temp)
            self.substrate_temps.append(substrate_temp)

            # Calculate rolling stats
            window = 10
            self.rolling_means_p.append(np.mean(self.pressures[-window:]))
            self.rolling_stds_p.append(np.std(self.pressures[-window:]))
            self.rolling_means_t.append(np.mean(self.temps[-window:]))
            self.rolling_stds_t.append(np.std(self.temps[-window:]))
            self.rolling_means_sub.append(np.mean(self.substrate_temps[-window:]))
            self.rolling_stds_sub.append(np.std(self.substrate_temps[-window:]))

            # Maintain 10 Hz rate
            elapsed = time.time() - start_time
            time.sleep(max(0, 0.1 - elapsed))

    # --------------------------
    # Update Loop (Animation & Plots)
    # --------------------------
    def update_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.on_close()

            # Bidirectional motion
            if self.pipe_position >= 100: self.direction = -1
            elif self.pipe_position <= 0: self.direction = 1
            self.pipe_position += 0.25 * self.direction
            self.flow_phase += 0.1 * self.direction
            self.wrap_count += abs(self.direction) * 0.01

            # Draw pipe + HUD
            self.surface.fill((0, 0, 0))
            self.draw_helical_pipe()
            self.draw_hud_overlay()
            pygame.display.flip()
            self.clock.tick(30)

            # Update plots
            self.update_plots()
            time.sleep(0.03)  # ~30 FPS

    # --------------------------
    # Pipe drawing (simplified)
    # --------------------------
    def draw_helical_pipe(self):
        y_center = self.HEIGHT // 2
        diameter = self.BASE_DIAMETER_PX + (self.wrap_count * self.TAPE_THICKNESS_PX)
        radius = diameter / 2
        pygame.draw.rect(self.surface, self.PIPE_COLOR, (0, y_center - radius, self.WIDTH, diameter), border_radius=int(radius))
        base_r, base_g, base_b = self.TAPE_COLORS[int(self.wrap_count) % len(self.TAPE_COLORS)]
        pygame.draw.circle(self.surface, (base_r, base_g, base_b), (int(self.pipe_position * 8) % self.WIDTH, y_center), 5)

    def draw_hud_overlay(self):
        font = pygame.font.SysFont("Consolas", 16)
        label = font.render(f"Pos: {self.pipe_position:.2f}m  Layers: {self.wrap_count:.2f}", True, (200, 200, 200))
        self.surface.blit(label, (20, 20))

    # --------------------------
    # Update matplotlib plots
    # --------------------------
    def update_plots(self):
        self.ax_ts.clear()
        self.ax_hist_p.clear()
        self.ax_hist_t.clear()
        self.ax_hist_sub.clear()

        if self.positions:
            def plot_line(ax, data, mean, std, color, label, show):
                if not show: return
                ax.plot(self.positions, data, color=color, alpha=0.3)
                ax.plot(self.positions, mean, color=color, lw=2, label=label)
                ax.fill_between(self.positions, mean - std, mean + std, color=color, alpha=0.2)

            plot_line(self.ax_ts, self.pressures, self.rolling_means_p, self.rolling_stds_p, 'purple', 'Pressure ±σ', self.show_pressure.get())
            plot_line(self.ax_ts, self.temps, self.rolling_means_t, self.rolling_stds_t, 'red', 'Tape Temp ±σ', self.show_temp.get())
            plot_line(self.ax_ts, self.substrate_temps, self.rolling_means_sub, self.rolling_stds_sub, 'lime', 'Substrate ±σ', self.show_substrate.get())

            self.ax_ts.set_title("Live Time-Series")
            self.ax_ts.legend(loc="upper left")
            self.ax_ts.grid(True)

        self.fig.tight_layout()
        self.canvas.draw()

    # --------------------------
    # SQL Export Worker
    # --------------------------
    def export_worker(self):
        while self.running:
            if len(self.positions) >= 40:
                # TODO: Export last 40 samples to SQL
                df = pd.DataFrame({
                    "pipe_pos": self.positions[-40:],
                    "rollerpressure": self.pressures[-40:],
                    "tapetemperature": self.temps[-40:],
                    "substtemprature": self.substrate_temps[-40:],
                })
                # Example:
                # df.to_sql(self.clone_rp, self.engine, if_exists='append', index=False)
                # df.to_sql(self.clone_tt, self.engine, if_exists='append', index=False)
                # df.to_sql(self.clone_st, self.engine, if_exists='append', index=False)

            time.sleep(0.1)

    # --------------------------
    # Cleanup
    # --------------------------
    def on_close(self):
        self.running = False
        self.engine.dispose()
        pygame.quit()
        self.destroy()
