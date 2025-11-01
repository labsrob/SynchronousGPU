import os, time, math, random, threading
import tkinter as tk
from tkinter import ttk
from queue import Queue
from datetime import datetime
import numpy as np
import pandas as pd
import pygame
from sqlalchemy import create_engine, text
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.stats import norm

# --------------------------------------------------------------------------
# 1️ SQL CONFIG
# --------------------------------------------------------------------------
SERVER = '127.0.0.1'
DATABASE = "DAQ_sSPC"
USERNAME = "TCP01"
PASSWORD = "Testing27!"
TEMPLATE_TABLE = "pipe_data_template"

conn_str = (f"mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}"
            "?driver=ODBC+Driver+17+for+SQL+Server")
engine = create_engine(conn_str)

# --- Table Check Function ---
def table_exists(engine, schema_name, table_name):
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
        print(f"Error checking table: {e}")
        return None

# --- Run Check ---
pWON = '20250923'
xRP = f"XRP_{pWON}"
xTT = f"XTT_{pWON}"
xST = f"XST_{pWON}"
newSqlTables1, newSqlTables2, newSqlTables3 = xRP, xTT, xST
dataTemplate1, dataTemplate2, dataTemplate3 = '[dbo].[18_EoPRP]', '[dbo].[19_EoPTT]', '[dbo].[20_EoPST]'

def create_table_from_template(engine, newSqlTables1, newSqlTables2, newSqlTables3, dataTemplate1, dataTemplate2, dataTemplate3):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_table = f"pipe_data_run_{timestamp}"
    try:
        existsA = table_exists(engine, "dbo", newSqlTables1)
        existsB = table_exists(engine, "dbo", newSqlTables2)
        existsC = table_exists(engine, "dbo", newSqlTables3)
        print('TP01', existsA, existsB, existsC)
    except Exception:
        print('TP02 Tables not exists, creating new Tables...')

    if existsA == 'No' or existsB == 'No' or existsC == 'No':
        try:
            with engine.begin() as conn:
                conn.execute(text(f"SELECT TOP 0 * INTO {newSqlTables1} FROM {dataTemplate1}"))
                conn.execute(text(f"SELECT TOP 0 * INTO {newSqlTables2} FROM {dataTemplate2}"))
                conn.execute(text(f"SELECT TOP 0 * INTO {newSqlTables3} FROM {dataTemplate3}"))

            print(f"[SQL] Created new table: {newSqlTables1, newSqlTables2, newSqlTables3}")
        except Exception:
            print('TP03 Error creating new Tables..')
    else:
        print('Tables already exists...')

    return newSqlTables1, newSqlTables2, newSqlTables3


table_name = create_table_from_template(engine, newSqlTables1, newSqlTables2, newSqlTables3, dataTemplate1, dataTemplate2, dataTemplate3)
print('TO001', table_name)
export_queue = Queue()

# --------------------------------------------------------------------------
# 2️ TKINTER MAIN WINDOW
# --------------------------------------------------------------------------
root = tk.Tk()
root.title("Bidirectional Tape Laying Process - SPC")
root.geometry("2400x820")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

tab_dashboard = ttk.Frame(notebook)
notebook.add(tab_dashboard, text="Simulation + Plots")

# Layout split
sim_frame = tk.Frame(tab_dashboard, bg="black", width=850, height=250)
sim_frame.pack(side="left", fill="both", expand=True)
sim_frame.update()

plot_container = tk.Frame(tab_dashboard, bg="#222", width=1250, height=250)
plot_container.pack(side="right", fill="both", expand=True)

# Toggle checkboxes frame
toggle_frame = tk.Frame(plot_container, bg="#111")
toggle_frame.pack(side="top", fill="x", pady=4)

show_pressure = tk.BooleanVar(value=True)
show_temp = tk.BooleanVar(value=True)
show_substrate = tk.BooleanVar(value=True)

ttk.Checkbutton(toggle_frame, text="Consolidated Pressure", variable=show_pressure).pack(side="left", padx=10)
ttk.Checkbutton(toggle_frame, text="Tape Temperature", variable=show_temp).pack(side="left", padx=10)
ttk.Checkbutton(toggle_frame, text="Substrate Temperature", variable=show_substrate).pack(side="left", padx=10)

plot_frame = tk.Frame(plot_container, bg="#222")
plot_frame.pack(fill="both", expand=True)

bottom_frame = tk.Frame(root, bg="#111", height=40)
bottom_frame.pack(fill="x")

sql_status_var = tk.StringVar(value="SQL: Idle")
sql_label = tk.Label(bottom_frame, textvariable=sql_status_var, fg="#ccc", bg="#111", font=("Consolas", 12))
sql_label.pack(side="left", padx=10)

sql_led = tk.Canvas(bottom_frame, width=20, height=20, bg="#111", highlightthickness=0)
sql_led.pack(side="left", padx=(0, 10))
led_circle = sql_led.create_oval(4, 4, 16, 16, fill="#555")
def set_led(color): sql_led.itemconfig(led_circle, fill=color)

# --------------------------------------------------------------------------
# 3️ PYGAME EMBED
# --------------------------------------------------------------------------
os.environ['SDL_WINDOWID'] = str(sim_frame.winfo_id())
os.environ['SDL_VIDEODRIVER'] = 'windib'
pygame.display.init()
pygame.font.init()
pygame.display.set_mode((850, 900))
surface = pygame.display.get_surface()
clock = pygame.time.Clock()

# --------------------------------------------------------------------------
# 4 SIMULATION PARAMETERS
# --------------------------------------------------------------------------
WIDTH, HEIGHT = 850, 450
BASE_DIAMETER_PX = 150      # 6" Base Diameter Pipe
TAPE_THICKNESS_PX = 0.2     # same for 22mm or 18 mm tape
PIXELS_PER_METER = 10
PIPE_COLOR = (40, 40, 40)
TAPE_COLORS = [(180, 180, 255), (120, 200, 255)]
PIPE_LENGTH_METERS = 100
WRAP_SPEED = 1.2            # TODO: plug in SCADA values
SAMPLING_RESOLUTION = 0.25

wrap_count, pipe_position, flow_phase, direction = 0, 0.0, 0.0, 1
start_time = time.time()

pressure_data, temp_data, substrate_data = [], [], []
rolling_means_p, rolling_stds_p = [], []
rolling_means_t, rolling_stds_t = [], []
rolling_means_sub, rolling_stds_sub = [], []
positions, pressures, temps, substrate_temps = [], [], [], []

# --------------------------------------------------------------------------
# DRAWING SIMULATED PIPE - USING BEST REALISTIC IMAGE - RL
# --------------------------------------------------------------------------
def draw_helical_pipe(surface, pipe_position, wrap_count, flow_phase, direction=1):
    y_center = HEIGHT // 2
    diameter = BASE_DIAMETER_PX + (wrap_count * TAPE_THICKNESS_PX)
    radius = diameter / 2
    pygame.draw.rect(surface, PIPE_COLOR, (0, y_center - radius, WIDTH, diameter), border_radius=int(radius))

    base_r, base_g, base_b = TAPE_COLORS[int(wrap_count) % len(TAPE_COLORS)]
    color_shift = int((wrap_count * 4) % 60)
    color = (min(base_r + color_shift, 255), min(base_g + color_shift // 2, 255), min(base_b + color_shift // 3, 255))

    stripe_count = 10
    for i in range(stripe_count):
        phase_shift = flow_phase + (i * (math.pi * 2 / stripe_count))
        points = [(x, y_center + radius * math.sin(0.02 * x + phase_shift * direction)) for x in range(0, WIDTH, 8)]
        pygame.draw.lines(surface, color, False, points, 3)

    font = pygame.font.SysFont("Consolas", 16)
    tick_color_major = (230, 230, 230)
    offset_px = -(pipe_position * PIXELS_PER_METER) % (PIPE_LENGTH_METERS * PIXELS_PER_METER)
    for m in range(-1, int(WIDTH / PIXELS_PER_METER) + 2):
        tick_x = int((m * PIXELS_PER_METER) + offset_px)
        if 0 <= tick_x <= WIDTH and (int(pipe_position) + m) % 10 == 0:
            pygame.draw.line(surface, tick_color_major, (tick_x, y_center + radius + 5), (tick_x, y_center + radius + 15), 2)
            surface.blit(font.render(f"{int(pipe_position) + m} m", True, tick_color_major),
                         (tick_x - 12, y_center + radius + 18))

    label = font.render(f"Diameter: {diameter:.1f}px  Layers: {wrap_count}  Pos: {pipe_position:.2f} m", True, (200, 200, 200))
    surface.blit(label, (20, 20))
    return diameter


def draw_hud_overlay(surface, pipe_position, wrap_count, diameter, pressure_data, temp_data, substrate_data, start_time, direction):
    now = time.time()
    elapsed = now - start_time
    recent_p = pressure_data[-5:] if pressure_data else [0]
    recent_t = temp_data[-5:] if temp_data else [0]
    recent_s = substrate_data[-5:] if substrate_data else [0]
    mean_p, std_p = np.mean(recent_p), np.std(recent_p)
    mean_t, std_t = np.mean(recent_t), np.std(recent_t)
    mean_s, std_s = np.mean(recent_s), np.std(recent_s)
    overlay_rect = pygame.Surface((350, 190), pygame.SRCALPHA)
    overlay_rect.fill((0, 0, 0, 150))
    surface.blit(overlay_rect, (20, 60))
    font = pygame.font.SysFont("Consolas", 18)
    stats = [
        f"Pipe Pos: {pipe_position:6.2f} m",
        f"Diameter: {diameter:6.1f}px",
        f"Layer(s): {int(wrap_count):3d}",
        f"Pressure: {mean_p:6.2f} (σ={std_p:.2f})",
        f"TapeTemp: {mean_t:6.2f}°C (σ={std_t:.2f})",
        f"Substrate: {mean_s:6.2f}°C (σ={std_s:.2f})",
        f"Direction: {'-→' if direction == 1 else '←-'}",
        f"Elapsed: {elapsed:5.1f}s"
    ]
    for i, txt in enumerate(stats):
        surface.blit(font.render(txt, True, (200, 255, 200)), (30, 70 + i * 20))

# --------------------------------------------------------------------------
# MATPLOTLIB FIGURE
# --------------------------------------------------------------------------
fig = Figure(figsize=(25, 7), dpi=100)

ax_ts = fig.add_subplot(2, 3, (1,3))    # Combined time series (top quarter)
ax_hist_p = fig.add_subplot(2, 3, 4)    # Pressure histogram
ax_hist_t = fig.add_subplot(2, 3, 5)    # Pipe Temp histogram
ax_hist_sub = fig.add_subplot(2, 3, 6)  # Substrate Temp histogram

canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().pack(fill="both", expand=True)


# --- Batch SQL save every 600 samples, i.e. 1 mt pipe ---
if len(positions) % 40 == 0:
    df = pd.DataFrame({
        "timestamp": [datetime.now()] * len(positions[-40:]),
        "pipe_pos": positions[-40:],
        "rollerpressure": pressures[-40:],
        "tapetemperature": temps[-40:],
        "substtemprature": substrate_temps[-40:],
        "mean_pressure": rolling_means_p[-40:],
        "std_pressure": rolling_stds_p[-40:],
        "mean_temperature": rolling_means_t[-40:],
        "std_temperature": rolling_stds_t[-40:],
        "mean_substrateTemp": rolling_means_sub[-40:],
        "std_substrateTemp": rolling_stds_t[-40:],
    })
    export_queue.put(df)

def update_plots():
    ax_ts.clear(); ax_hist_p.clear(); ax_hist_t.clear(); ax_hist_sub.clear()
    if positions:
        def plot_line_with_shade(ax, pos, data, mean, std, color, label, show):
            if not show: return
            ax.plot(pos, data, color=color, alpha=0.3)
            ax.plot(pos, mean, color=color, lw=2, label=label)
            ax.fill_between(pos, mean - std, mean + std, color=color, alpha=0.2)

        # ±1σ regions with toggles
        p_mean, p_std = np.array(rolling_means_p), np.array(rolling_stds_p)
        t_mean, t_std = np.array(rolling_means_t), np.array(rolling_stds_t)
        s_mean, s_std = np.array(rolling_means_sub), np.array(rolling_stds_sub)

        plot_line_with_shade(ax_ts, positions, pressures, p_mean, p_std, "purple", "Pressure ±σ", show_pressure.get())
        plot_line_with_shade(ax_ts, positions, temps, t_mean, t_std, "red", "Tape Temp ±σ", show_temp.get())
        plot_line_with_shade(ax_ts, positions, substrate_temps, s_mean, s_std, "lime", "Substrate ±σ", show_substrate.get())

        ax_ts.set_title("Live Time-Series (toggle signals)")
        ax_ts.set_ylabel("Values")
        ax_ts.legend(loc="upper left")
        ax_ts.grid(True)

        def plot_hist(ax, data, color, label, show):
            if not show or len(data) < 2: return
            ax.hist(data, bins=20, density=True, alpha=0.4, color=color)
            mu, std = np.mean(data), np.std(data)
            x = np.linspace(min(data), max(data), 100)
            ax.plot(x, norm.pdf(x, mu, std), color=color, lw=2)
            ax.set_title(f"{label} (μ={mu:.2f}, σ={std:.2f})")
            ax.set_xlabel("Value"); ax.set_ylabel("Density"); ax.grid(True)

            # Add limit shift ------------------
        plot_hist(ax_hist_p, pressures, "purple", "Roller Pressure", show_pressure.get())
        plot_hist(ax_hist_t, temps, "red", "Tape Temp", show_temp.get())
        plot_hist(ax_hist_sub, substrate_temps, "green", "Substrate Temp", show_substrate.get())

    fig.tight_layout()
    canvas.draw()

# --------------------------------------------------------------------------[]
# SQL THREAD
# --------------------------------------------------------------------------[]
def export_worker():
    while True:
        batch = export_queue.get()
        if batch is None: break
        root.after(0, lambda: (sql_status_var.set("SQL: Saving..."), set_led("#00FF00")))
        try:
            batch.to_sql(table_name, con=engine, if_exists='append', index=False)
        except Exception as e:
            print("[SQL ERROR]", e)
            root.after(0, lambda: (sql_status_var.set("SQL: ERROR"), set_led("#FF0000")))
        else:
            root.after(1000, lambda: (sql_status_var.set("SQL: Idle"), set_led("#555")))
        export_queue.task_done()
        time.sleep(0.1)

threading.Thread(target=export_worker, daemon=True).start()

# --------------------------------------------------------------------------
# 8 MAIN LOOP (Bidirectional motion)
# --------------------------------------------------------------------------
def update_loop():
    global pipe_position, wrap_count, flow_phase, direction

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            on_close()

    # Bidirectional motion: reverse when reaching ends
    if pipe_position >= 100:
        direction = -1
    elif pipe_position <= 0:
        direction = 1
    # ROLLER PRESSURE ----------------[]
    pR1H1 = random.uniform(85, 125)
    pR1H2 = random.uniform(75, 105)
    pR1H3 = random.uniform(95, 125)
    pR1H4 = random.uniform(95, 115)
    pR1H5 = random.uniform(25, 95)
    pR1H6 = random.uniform(65, 135)
    pR1H7 = random.uniform(75, 125)
    pR1H8 = random.uniform(85, 125)
    pR1H9 = random.uniform(77, 105)
    pR1H10 = random.uniform(85, 125)
    pR1H11 = random.uniform(82, 105)
    pR1H12 = random.uniform(83, 101)
    pR1H13 = random.uniform(92, 103)
    pR1H14 = random.uniform(91, 125)
    pR1H15 = random.uniform(90, 135)
    pR1H16 = random.uniform(91, 145)
    pipe_position += direction * 0.25
    pDir = direction
    # current_pressure = random.uniform(95, 105)
    current_pressure = np.nanmean([pR1H1, pR1H2, pR1H3, pR1H4, pR1H5, pR1H6, pR1H7, pR1H8, pR1H9, pR1H10, pR1H11, pR1H12,
                                  pR1H13, pR1H14, pR1H15, pR1H16])

    # TAPE TEMPERATURE ----------------[]
    tR1H1 = random.uniform(20, 65)
    tR1H2 = random.uniform(25, 45)
    tR1H3 = random.uniform(15, 65)
    tR1H4 = random.uniform(25, 45)
    tR1H5 = random.uniform(25, 65)
    tR1H6 = random.uniform(35, 55)
    tR1H7 = random.uniform(15, 45)
    tR1H8 = random.uniform(15, 25)
    tR1H9 = random.uniform(17, 57)
    tR1H10 = random.uniform(15, 25)
    tR1H11 = random.uniform(12, 50)
    tR1H12 = random.uniform(13, 51)
    tR1H13 = random.uniform(22, 43)
    tR1H14 = random.uniform(21, 25)
    tR1H15 = random.uniform(20, 45)
    tR1H16 = random.uniform(31, 45)
    pipe_position += direction * 0.25
    pDir = direction
    # current_pressure = random.uniform(95, 105)
    current_temp = np.nanmean([tR1H1, tR1H2, tR1H3, tR1H4, tR1H5, tR1H6, tR1H7, tR1H8, tR1H9, tR1H10, tR1H11, tR1H12,
                                  tR1H13, tR1H14, tR1H15, tR1H16])

    # SUBSTRATE TEMPERATURE -------------[]
    sR1H1 = random.uniform(40, 62)
    sR1H2 = random.uniform(55, 55)
    sR1H3 = random.uniform(35, 69)
    sR1H4 = random.uniform(35, 55)
    sR1H5 = random.uniform(45, 62)
    sR1H6 = random.uniform(35, 51)
    sR1H7 = random.uniform(55, 47)
    sR1H8 = random.uniform(35, 35)
    sR1H9 = random.uniform(37, 52)
    sR1H10 = random.uniform(45, 45)
    sR1H11 = random.uniform(32, 52)
    sR1H12 = random.uniform(43, 53)
    sR1H13 = random.uniform(32, 47)
    sR1H14 = random.uniform(41, 45)
    sR1H15 = random.uniform(30, 48)
    sR1H16 = random.uniform(41, 65)
    pipe_position += direction * 0.25
    pDir = direction
    # current_sub = random.uniform(95, 105)
    current_sub = np.nanmean([sR1H1, sR1H2, sR1H3, sR1H4, sR1H5, sR1H6, sR1H7, sR1H8, sR1H9, sR1H10, sR1H11, sR1H12,
                                  sR1H13, sR1H14, sR1H15, sR1H16])
    # ------------------------------[]
    # Aggregated values for time series plot
    pressures.append(current_pressure)
    temps.append(current_temp)
    substrate_temps.append(current_sub)
    positions.append(pipe_position)

    window = 10
    rolling_means_p.append(np.mean(pressures[-window:]))
    rolling_stds_p.append(np.std(pressures[-window:]))
    rolling_means_t.append(np.mean(temps[-window:]))
    rolling_stds_t.append(np.std(temps[-window:]))
    rolling_means_sub.append(np.mean(substrate_temps[-window:]))
    rolling_stds_sub.append(np.std(substrate_temps[-window:]))

    surface.fill((0, 0, 0))
    diameter = draw_helical_pipe(surface, pipe_position, wrap_count, flow_phase, direction)
    draw_hud_overlay(surface, pipe_position, wrap_count, diameter, pressures, temps, substrate_temps, start_time, direction)

    flow_phase += 0.1 * direction
    wrap_count += abs(direction) * 0.01

    pygame.display.flip()
    clock.tick(30)
    update_plots()
    root.after(200, update_loop)

# --------------------------------------------------------------------------
# 9 CLEANUP
# --------------------------------------------------------------------------
def on_close():
    export_queue.put(None)
    if len(positions) > 0:
        df = pd.DataFrame({
            "timestamp": [datetime.now()] * len(positions),
            "pipe_pos": positions,

            "rollerpressure": pressures,
            "tapetemperature": temps,
            "substtemprature": substrate_temps,
            "mean_pressure": rolling_means_p,
            "std_pressure": rolling_stds_p,
            "mean_temperature": rolling_means_t,
            "std_temperature": rolling_stds_t,
            "mean_substrateTemp": rolling_means_sub,
            "std_substrateTemp": rolling_stds_t,
        })
        export_queue.put(df)
    export_queue.put(None)  # stop worker
    engine.dispose()
    root.destroy()
    pygame.quit()
    print("Exiting...")

root.protocol("WM_DELETE_WINDOW", on_close)
root.after(1000, update_loop)
root.mainloop()
