# # ================================WITH PRESSURE DATA ===========================================================[]

# --------------------------------------------FINAL SAMPLE --------------------------------------[FAVOURITE 2]

# """
# Helical Tape Wrapping Machine Simulation with Pressure & Temperature
# - Sampling every 0.25 m
# - Rolling mean & std over last 1 m
# - Color-coded histograms
# Controls:
#   → / ← : start wrapping right / left (when stopped)
#   SPACE : pause
#   R     : clear samples
#   ESC   : quit (auto-save CSV)
# """
# import pygame, sys, math, random, statistics, time
# import pandas as pd
# import numpy as np
#
# # ---------------- CONFIG ----------------
# WIDTH, HEIGHT = 1500, 750
# FPS = 60
#
# PIPE_LENGTH_METERS = 100
# PIXELS_PER_METER = 8
#
# BASE_DIAMETER_PX = 80
# TAPE_THICKNESS_MM = 0.5
# TAPE_THICKNESS_PX = (TAPE_THICKNESS_MM / 1000) * PIXELS_PER_METER * 80
#
# ACCEL = 1.8
# DECEL = 2.8
# MAX_SPEED = 1.4
#
# SAMPLE_INTERVAL_M = 0.25
# ROLL_WINDOW_M = 1.0
#
# PRESSURE_STD_THRESHOLD = 0.05
# PRESSURE_STD_MAX = 0.25
# TEMP_STD_THRESHOLD = 0.2
# TEMP_STD_MAX = 2.0
# STEMP_STD_THRESHOLD = 0.2
# STEMP_STD_MAX = 2.0
#
#
# BG = (22,24,28)
# PIPE_COLOR = (70,130,220)
# TAPE_COLORS = [(255,255,180),(200,255,255),(255,200,255),(200,255,200)]
# PRESSURE_COLOR = (255,180,80)
# TEMP_COLOR = (80,200,255)
# STEMP_COLOR = (135,211, 0)
# STATS_BG = (40,45,55)
#
# # ---------------- INIT ----------------
# pygame.init()
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("Magma Tape Laying Simulation")
# clock = pygame.time.Clock()
# font = pygame.font.SysFont("Consolas", 18)
# bigfont = pygame.font.SysFont("Consolas", 22)
#
# # ---------------- STATE ----------------
# direction = 1
# position_m = 0.0
# x_offset = 0.0
# is_running = True
# wrap_count = 0
# speed = 0.0
# flow_phase = 0.0
# sensor_data = []
# last_sample_position = 0.0
#
# # ---------------- HELPERS ----------------
# def simulate_pressure_temp():
#     base_p = 2.0 + random.uniform(-0.12,0.12)
#     p = round(base_p + random.uniform(-0.03,0.03),3)
#     t = round(25.0 + (p-2.0)*8 + random.uniform(-0.3,0.3),2)
#     s = round(23.0 + (p - 2.0) * 8 + random.uniform(-0.3, 0.3), 2)
#     return p, t, s
#
# def color_from_std(std_val, threshold, max_std):
#     if std_val <= threshold: return (60,200,80)
#     ratio = min(1.0, max(0.0, (std_val - threshold)/(max_std-threshold)))
#     if ratio < 0.5:
#         t = ratio/0.5
#         r = int(60 + (255-60)*t)
#         g = int(200 + (255-200)*t)
#         return (r,g,60)
#     else:
#         t = (ratio-0.5)/0.5
#         r = 255
#         g = int(255-(255-80)*t)
#         return (r,g,60)
#
# # -------------------------------------------------------------------- DRAWING ----------------
#
# def draw_interwoven_lattice(surface, x_offset, wraps, phase, direction):
#     """
#     Draw a lattice-style interwoven helical tape.
#     Two sets of diagonal stripes cross each other.
#     Pipe grows in diameter with wraps.
#     """
#     y_center = HEIGHT // 2
#     current_diameter = int(BASE_DIAMETER_PX + wraps * TAPE_THICKNESS_PX)
#     radius = current_diameter / 2
#     # Draw background pipe body
#     pygame.draw.rect(surface, PIPE_COLOR, (0, y_center - radius, WIDTH, current_diameter), border_radius=int(radius))
#
#     # lattice parameters
#     stripe_spacing = max(30, radius * 0.6)
#     stripe_width = max(3, radius * 0.08)
#     amp = radius * 0.5
#
#     # two crossing directions
#     for direction_sign, phase_offset in [(1, 0), (-1, math.pi)]:
#         color = TAPE_COLORS[wraps % len(TAPE_COLORS)]
#         points = []
#         step = 6
#         for x in range(0, WIDTH + step, step):
#             y = y_center + amp * math.sin((x / stripe_spacing) * 2 * math.pi * direction_sign + phase + phase_offset)
#             points.append((x, y))
#         pygame.draw.lines(surface, color, False, points, int(stripe_width))
#
#     # ticks every 10 m
#     for meter in range(0, PIPE_LENGTH_METERS + 1, 10):
#         tick_x = int((meter * PIXELS_PER_METER - x_offset) % (PIPE_LENGTH_METERS * PIXELS_PER_METER))
#         if 0 <= tick_x <= WIDTH:
#             pygame.draw.line(surface, (230, 230, 230), (tick_x, y_center + radius), (tick_x, y_center + radius + 12), 2)
#             lbl = font.render(f"{meter}m", True, (230, 230, 230))
#             surface.blit(lbl, (tick_x - lbl.get_width() // 2, y_center + radius + 14))
#
#     return y_center, current_diameter
#
# def draw_helical_pipe(surface, x_offset, wrap_count, flow_phase, direction, speed):
#     y_center = HEIGHT // 2
#     diameter = BASE_DIAMETER_PX + wrap_count * tape_thickness_px
#     radius = diameter / 2
#     color = TAPE_COLORS[wrap_count % len(TAPE_COLORS)]
#     # Draw background pipe body
#     pygame.draw.rect(surface, PIPE_COLOR, (0, y_center - radius, WIDTH, diameter), border_radius=int(radius))
#
#     # Simulate helical stripes using sine waves
#     stripe_count = 10
#     for i in range(stripe_count):
#         phase_shift = flow_phase + (i * (math.pi * 2 / stripe_count))
#         points = []
#         for x in range(0, WIDTH, 10):
#             y = y_center + radius * math.sin(0.02 * (x * direction) + phase_shift)
#             points.append((x, y))
#         pygame.draw.lines(surface, color, False, points, 3)
#
#     # Meter ticks every 10m
#     for meter in range(0, PIPE_LENGTH_METERS + 1, 10):
#         tick_x = int((meter * PIXELS_PER_METER - x_offset) % PIPE_LENGTH)
#         if 0 <= tick_x <= WIDTH:
#             pygame.draw.line(surface, (220, 220, 220),
#                              (tick_x, y_center + radius),
#                              (tick_x, y_center + radius + 10), 1)
#             label = font.render(f"{meter}m", True, (220, 220, 220))
#             surface.blit(label, (tick_x - 10, y_center + radius + 12))
#
#     return y_center, diameter
#
#
# def draw_time_series(surface, data):
#     chart_w, chart_h = WIDTH-800, 150
#     chart_x, chart_y = 1020, HEIGHT-chart_h - 490
#     pygame.draw.rect(surface, STATS_BG, (chart_x - 230, chart_y, chart_w, chart_h), border_radius=8)
#     pygame.draw.rect(surface, (100,100,100), (chart_x- 230, chart_y, chart_w, chart_h),2)
#
#     if not data: return
#     pres_vals = [p for _, p, _, _ in data]
#     temp_vals = [t for _, _, t, _ in data]
#     stemp_vals = [s for _, _, _, s in data]
#
#     max_p, min_p = max(pres_vals), min(pres_vals)
#     max_t, min_t = max(temp_vals), min(temp_vals)
#     max_s, min_s = max(stemp_vals), min(stemp_vals)
#
#     pts_pres = []
#     pts_temp = []
#     pts_stemp = []
#     visible = data[-chart_w:]
#
#     # Compute for Min/Max ----------------------------------------------------------[]
#     for i,(m, p, t, s) in enumerate(visible):
#         x = chart_x - 230 +i
#         y_p = chart_y + chart_h - int((p - min_p) / (max_p - min_p + 1e-6) * chart_h)
#         y_t = chart_y + chart_h - int((t - min_t) / (max_t - min_t + 1e-6) * chart_h)
#         y_s = chart_y + chart_h - int((s - min_s) / (max_s - min_s + 1e-6) * chart_h)
#
#         pts_pres.append((x,y_p))
#         pts_temp.append((x,y_t))
#         pts_stemp.append((x, y_s))
#
#     if len(pts_pres) > 1: pygame.draw.lines(surface,PRESSURE_COLOR,False,pts_pres,2)
#     if len(pts_temp) > 1: pygame.draw.lines(surface,TEMP_COLOR,False,pts_temp,2)
#     if len(pts_stemp) > 1: pygame.draw.lines(surface, STEMP_COLOR, False, pts_stemp, 2)
#     surface.blit(font.render("Statistical Distribution of DNV Parameters [RP (bar) | TT (°C) | ST (°C)]", True, (220,220,220)),(chart_x - 290, chart_y-55)) #20
#
#
# def draw_histogram(surface, values, pos_x, title, color):
#     if not values: return
#     box_w, box_h = 320, 150  # position of Critical params []
#     box_x, box_y = pos_x+85, HEIGHT-box_h - 30
#
#     pygame.draw.rect(surface, STATS_BG, (box_x, box_y, box_w, box_h), border_radius=8)
#     pygame.draw.rect(surface, (90,90,90), (box_x, box_y, box_w, box_h), 2)
#
#     bins = np.linspace(min(values), max(values), 32)
#     hist, edges = np.histogram(values, bins=bins)
#
#     max_h = max(hist) if hist.size>0 and max(hist)>0 else 1
#     bw = (box_w-28)/len(hist)
#
#     for i,h in enumerate(hist):
#         x = box_x+14+i*bw
#         bh = (h/max_h)*(box_h-40)
#         y = box_y+box_h-bh-14
#         pygame.draw.rect(surface,color,(x,y,bw*0.9,bh))
#     surface.blit(font.render(title, True, (220,220,220)), (box_x+10, box_y-20))
#
#
# def draw_stats_panel(surface, data, pos_m):
#     recent_pres = [p for (m, p, t, s) in data if 0<=abs(pos_m)-m<=ROLL_WINDOW_M]
#     recent_temp = [t for (m, p, t, s) in data if 0<=abs(pos_m)-m<=ROLL_WINDOW_M]
#     # -- Add -----
#     recent_stemp = [s for (m, p, t, s) in data if 0 <= abs(pos_m) - m <= ROLL_WINDOW_M]
#
#     cur_p, cur_t, cur_s = (data[-1][1], data[-1][2], data[-1][3]) if data else (None,None, None)
#     # print('TP02', cur_p, cur_t, cur_s)
#
#     mean_p = statistics.mean(recent_pres) if recent_pres else None
#     std_p = statistics.pstdev(recent_pres) if recent_pres and len(recent_pres)>1 else 0.0
#     mean_t = statistics.mean(recent_temp) if recent_temp else None
#     std_t = statistics.pstdev(recent_temp) if recent_temp and len(recent_temp)>1 else 0.0
#     # ---- Add ------
#     mean_s = statistics.mean(recent_stemp) if recent_stemp else None
#     std_s = statistics.pstdev(recent_stemp) if recent_stemp and len(recent_stemp) > 1 else 0.0
#
#
#     box_w, box_h = 320, 150
#     box_x, box_y = 10, HEIGHT - box_h - 30
#     pygame.draw.rect(surface, STATS_BG, (box_x, box_y, box_w, box_h), border_radius=8) # fill box
#     pygame.draw.rect(surface, (100,100,100), (box_x, box_y, box_w, box_h),2) # boarder colour
#     lines = [
#         f"Position: {pos_m:.2f}m",
#
#         f"Current RP: {cur_p:.3f} bar" if cur_p else "Current RP: -",
#         f"Mean RP(1m): {mean_p:.3f} Std: {std_p:.4f}" if mean_p else "Mean RP(1m): -",
#         "",
#         f"Current TT: {cur_t:.2f} °C" if cur_t else "Current TT: -",
#         f"Mean TT(1m): {mean_t:.2f} Std: {std_t:.3f}" if mean_t else "Mean TT(1m): -",
#         "",
#         f"Current ST: {cur_t:.2f} °C" if cur_s else "Current ST: -",
#         f"Mean ST(1m): {mean_s:.2f} Std: {std_s:.3f}" if mean_s else "Mean ST(1m): -",]
#
#     for i,txt in enumerate(lines):
#         surface.blit(font.render(txt, True, (230,230,230)), (box_x+10, box_y + 5 + i * 15)) # text
#     return recent_pres, recent_temp, recent_stemp
#
#
# def draw_grand_mean_panel(surface, data, pos_m):
#     recent_pres = [p for (m, p, t, s) in data if 0<=abs(pos_m)-m<=ROLL_WINDOW_M]
#     recent_temp = [t for (m, p, t, s) in data if 0<=abs(pos_m)-m<=ROLL_WINDOW_M]
#     # -- Add -----
#     recent_stemp = [s for (m, p, t, s) in data if 0 <= abs(pos_m) - m <= ROLL_WINDOW_M]
#
#     cur_p, cur_t, cur_s = (data[-1][1], data[-1][2], data[-1][3]) if data else (None,None, None)
#     # print('TP02', cur_p, cur_t, cur_s)
#
#     gmean_p = statistics.mean(recent_pres) if recent_pres else None
#     gstd_p = statistics.pstdev(recent_pres) if recent_pres and len(recent_pres)>1 else 0.0
#     gmean_t = statistics.mean(recent_temp) if recent_temp else None
#     gstd_t = statistics.pstdev(recent_temp) if recent_temp and len(recent_temp)>1 else 0.0
#     # ---- Add ------
#     gmean_s = statistics.mean(recent_stemp) if recent_stemp else None
#     gstd_s = statistics.pstdev(recent_stemp) if recent_stemp and len(recent_stemp) > 1 else 0.0
#
#
#     box_w, box_h = 350, 150
#     box_x, box_y = 1060, HEIGHT - box_h - 30
#     pygame.draw.rect(surface, STATS_BG, (box_x, box_y, box_w, box_h), border_radius=8) # fill box
#     pygame.draw.rect(surface, (100,100,100), (box_x, box_y, box_w, box_h),2) # boarder colour
#     lines = [
#         f"Position: {pos_m:.2f}m",
#
#         f"Current [RP]: {cur_p:.3f} bar" if cur_p else "x̄ of Mean / 1m: -",
#         f"x̄ of Mean: {gmean_p:.3f} x̄ of Std: {gstd_p:.4f}" if gmean_p else "x̄ RP(1m): -",
#         "",
#         f"Current [TT]: {cur_t:.2f} °C" if cur_t else "x̄ of Mean / 1m: -",
#         f"x̄ of Mean: {gmean_t:.2f} x̄ of Std: {gstd_t:.3f}" if gmean_t else "x̄ TT(1m): -",
#         "",
#         f"Current [ST]: {cur_t:.2f} °C" if cur_s else "x̄ of Mean / 1m: -",
#         f"x̄ of Mean: {gmean_s:.2f} x̄ of Std: {gstd_s:.3f}" if gmean_s else "x̄ ST(1m): -",]
#
#     for i,txt in enumerate(lines):
#         surface.blit(font.render(txt, True, (230,230,230)), (box_x+10, box_y + 5 + i * 15)) # text
#     return recent_pres, recent_temp, recent_stemp
#
#
# # ---------------- MAIN LOOP ----------------
# while True:
#     dt = clock.tick(FPS)/1000.0
#
#     # events
#     for ev in pygame.event.get():
#         if ev.type==pygame.QUIT:
#             pd.DataFrame(sensor_data, columns=["position_m","pressure_bar","temp_C", "stemp_C"]).to_csv("wrap_data.csv",index=False)
#             pygame.quit(); sys.exit()
#
#         if ev.type==pygame.KEYDOWN:
#             if ev.key==pygame.K_ESCAPE:
#                 pd.DataFrame(sensor_data, columns=["position_m","pressure_bar","temp_C", "stemp_C"]).to_csv("wrap_data.csv",index=False)
#                 pygame.quit(); sys.exit()
#
#             elif ev.key==pygame.K_SPACE: is_running=False
#
#             elif ev.key==pygame.K_r: sensor_data=[]
#
#             elif not is_running:
#                 if ev.key==pygame.K_RIGHT: direction=1; is_running=True
#                 elif ev.key==pygame.K_LEFT: direction=-1; is_running=True
#
#     # motion
#     if is_running and speed<MAX_SPEED: speed=min(MAX_SPEED, speed+ACCEL*dt)
#     elif not is_running and speed>0: speed=max(0.0, speed-DECEL*dt)
#     if speed>0:
#         delta_m = speed *dt * direction
#         position_m += delta_m
#         x_offset += delta_m*PIXELS_PER_METER
#         flow_phase += speed * dt * 2.5 * direction
#
#         if abs(position_m - last_sample_position) >= SAMPLE_INTERVAL_M:
#             p, t, s = simulate_pressure_temp()
#             # print('TP03', p, t, s)
#             sensor_data.append((position_m, p, t, s))
#             last_sample_position = position_m
#
#         if position_m>=PIPE_LENGTH_METERS:
#             position_m = PIPE_LENGTH_METERS; is_running=False; wrap_count+=1; speed=0.0
#         elif position_m<=0:
#             position_m=0.0; is_running=False; wrap_count+=1; speed=0.0
#
#     # draw ----------------------------------------------------------------------[]
#     screen.fill(BG)
#     draw_helical_pipe(screen, x_offset, wrap_count, flow_phase, direction, speed)
#
#     draw_time_series(screen, sensor_data)
#     recent_pres, recent_temp , recent_stemp = draw_stats_panel(screen, sensor_data, abs(position_m))
#     recent_Rpres, recent_Rtemp, recent_Rstemp = draw_grand_mean_panel(screen, sensor_data, abs(position_m))
#
#     # Left side Statistic Panel, boarder & Fill
#     # if recent_pres: draw_histogram(screen, recent_pres, pos_x=250, title="[Roller Pressure]", color=color_from_std(statistics.pstdev(recent_pres) if len(recent_pres)>1 else 0.0, PRESSURE_STD_THRESHOLD, PRESSURE_STD_MAX))
#     # if recent_temp: draw_histogram(screen, recent_temp, pos_x=440, title="[Tape Temperature]", color=color_from_std(statistics.pstdev(recent_temp) if len(recent_temp)>1 else 0.0, TEMP_STD_THRESHOLD, TEMP_STD_MAX))
#     # if recent_stemp: draw_histogram(screen, recent_stemp, pos_x=650, title="[Substrate Temperature]", color=color_from_std(statistics.pstdev(recent_stemp) if len(recent_stemp) > 1 else 0.0, STEMP_STD_THRESHOLD, STEMP_STD_MAX))
#     # ----------------------------------------------------------
#     if recent_Rpres: draw_histogram(screen, recent_Rpres, pos_x=250, title="", color=color_from_std(statistics.pstdev(recent_pres) if len(recent_pres)>1 else 0.0, PRESSURE_STD_THRESHOLD, PRESSURE_STD_MAX))
#     if recent_Rtemp: draw_histogram(screen, recent_Rtemp, pos_x=440, title="", color=color_from_std(statistics.pstdev(recent_temp) if len(recent_temp)>1 else 0.0, TEMP_STD_THRESHOLD, TEMP_STD_MAX))
#     if recent_Rstemp: draw_histogram(screen, recent_Rstemp, pos_x=650, title="", color=color_from_std(statistics.pstdev(recent_stemp) if len(recent_stemp) > 1 else 0.0, STEMP_STD_THRESHOLD, STEMP_STD_MAX))
#
#     dir_txt = "→ RIGHT" if direction==1 else "← LEFT"
#     status = "RUNNING" if is_running or speed>0 else "STOPPED"
#     header = bigfont.render(f"Dir:{dir_txt} Speed:{speed:.2f} m/s Layer:{wrap_count} Pos:{position_m:.2f}m Status:{status}", True, (230,230,230))
#     screen.blit(header, (20,16))
#     inst = font.render("SPACE: Pause | ←/→: Start | R: Clear samples | ESC: Quit(save CSV)", True, (200,200,200))
#     screen.blit(inst,(20,56))
#     pygame.display.flip()


# -----------------------------------------FINAL EDITION ---------------------------------------------[3]

"""
Tkinter dashboard (Option B)
- Left: embedded Pygame animation (interwoven helical wrapping, diameter growth)
- Right: Matplotlib plots (top: time series last 5 m with shaded ±1σ; bottom: histograms with Gaussian overlay)
- Sampling every 0.25 m; rolling stats window = 1 m
- Realistic sensor ranges:
    Pressure ~ 100 kPa ± ~5 kPa
    Temperature ~ 40 °C ± ~3 °C
Controls:
  ← / →  : set direction and resume
  SPACE  : pause / resume
  R      : clear samples
  ESC    : save wrap_data.csv and quit
"""
import os
import sys
import math
import random
import time
import statistics
import tkinter as tk

from tkinter import messagebox, ttk

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import pygame

# ---------------- CONFIG ----------------
LEFT_WIDTH = 950    # Simulation now on the right
LEFT_HEIGHT = 720
# -------------Simulation sce
RIGHT_WIDTH = 1500           # time series window, now on the left
FPS = 20                     # frame rate
SAMPLE_STEP_M = 0.25         # sample every 0.25 m
ROLL_WINDOW_M = 1.0          # rolling stats window (1 m)
TS_WINDOW_M = 5.0            # time series window (5 m)

PIPE_LENGTH_M = 100.0
PIXELS_PER_METER = 8
PIPE_LENGTH_PX = int(PIPE_LENGTH_M * PIXELS_PER_METER)

BASE_DIAM_PX = 100
TAPE_THICKNESS_MM = 0.5
VISUAL_SCALE = 80
TAPE_THICKNESS_PX = (TAPE_THICKNESS_MM / 1000) * PIXELS_PER_METER * VISUAL_SCALE

# realistic sensor ranges (for simulation)
PRESSURE_BASE_KPA = 100.0
PRESSURE_VAR_KPA = 5.0
TEMP_BASE_C = 40.0
TEMP_VAR_C = 3.0

BG = "#0f1113"
PIPE_COLOR = (75, 140, 220)
TAPE_COLORS = [(255, 244, 180), (200, 244, 255)]
P_COLOR = "#ff9933"
T_COLOR = "#66d1ff"
S_COLOR = "#F527EB"
STATS_BG = "#1b1d22"

# ---------------- GLOBAL STATE ----------------
direction = 1                # 1 = right, -1 = left
position_m = 0.0             # current linear position along pipe (meters)
x_offset_px = 0.0
is_running = True
wrap_count = 0
flow_phase = 0.0

# storage of samples (absolute position, pressure_kpa, temp_c)
samples = []   # list of (position_m, pressure_kpa, temp_c)

last_sample_pos = -1e9

# ---

# ---------------- TK SETUP ----------------
root = tk.Tk()
root.title("Embedded Pygame + Tkinter Dashboard (Option B)")
root.configure(bg=BG)

label = ttk.Label(text='[ Mode]', font=12)
label.pack(padx=10, pady=5)

# Define Axes ---------------------#
# f = Figure(figsize=(25, 8), dpi=100)  # pMtX
# f.subplots_adjust(left=0.022, bottom=0.05, right=0.983, top=0.955, wspace=0.138, hspace=0.18)

f = Figure(figsize=(25.5, 8), dpi=100)
f.subplots_adjust(left=0.026, bottom=0.05, right=0.983, top=0.936, wspace=0.18, hspace=0.174)

main_frame = tk.Frame(root, bg=BG).pack(fill="both", expand=True)

left_frame = (tk.Frame(main_frame, width=LEFT_WIDTH, height=LEFT_HEIGHT, bg="black"))
left_frame.pack(side="right", padx=6, pady=6)
left_frame.pack_propagate(False)

right_frame = (tk.Frame(main_frame, width=RIGHT_WIDTH, bg=BG))
right_frame.pack(side="left", fill="y", padx=6, pady=6)
right_frame.pack_propagate(False)

# top-right stats labels
stats_frame = tk.Frame(left_frame, bg=BG)
stats_frame.pack(fill="x", padx=6, pady=6)
# ----------------------------------------
lbl_pressure = tk.Label(stats_frame, text="[RP]: - kPa", fg="white", bg=BG, font=("Consolas", 11))
lbl_pressure.pack(anchor="w")
lbl_temp = tk.Label(stats_frame, text="[TT]: - °C", fg="white", bg=BG, font=("Consolas", 11))
lbl_temp.pack(anchor="w")
lbl_stemp = tk.Label(stats_frame, text="[ST]: - °C", fg="white", bg=BG, font=("Consolas", 11))
lbl_stemp.pack(anchor="w")

# lbl_roll1 = tk.Label(stats_frame, text="Rolling (1 m): μ [RP]=- σ [RP]=-  |  μ [TT]=- σ [TT]=- |  μ [ST]=- σ [ST]=-", fg="white", bg=BG, font=("Consolas", 10))
lbl_roll1 = tk.Label(stats_frame, text="Rolling (1 m): μ [RP]=- σ [RP]=-  ", fg="white", bg=BG, font=("Consolas", 10))
lbl_roll1.pack(anchor="w", pady=(6,0))

lbl_roll2 = tk.Label(stats_frame, text="Rolling (1 m): μ [TT]=- σ [TT]=- ", fg="white", bg=BG, font=("Consolas", 10))
lbl_roll2.pack(anchor="w", pady=(7,0))

lbl_roll3 = tk.Label(stats_frame, text="Rolling (1 m): μ [ST]=- σ [ST]=-", fg="white", bg=BG, font=("Consolas", 10))
lbl_roll3.pack(anchor="w", pady=(8,0))
# Matplotlib figure on right
# fig = Figure(figsize=(7, 5), dpi=100)

# ---------------------------------[]
ax_ts = f.add_subplot(2, 3, (1, 3))     # Time Series plot of 3 parameters
ax_hist = f.add_subplot(2, 3, 4)        # void mapping profile
ax_hist2 = f.add_subplot(2, 3, 5)
ax_hist3 = f.add_subplot(2, 3, 6)
ax2 = ax_ts.twinx()

f.tight_layout(pad=3.0)
canvas_fig = FigureCanvasTkAgg(f, master=right_frame)   # self
canvas_widget = canvas_fig.get_tk_widget().pack(fill="both", expand=True, padx=6, pady=6)

# ---------------- PYGAME EMBED ----------------
# need to update the left_frame window id before setting SDL_WINDOW ID

left_frame.update_idletasks()
os.environ['SDL_WINDOWID'] = str(left_frame.winfo_id())

# select video driver for platform
if sys.platform.startswith("win"):
    os.environ['SDL_VIDEODRIVER'] = "windib"
else:
    # on Linux X11
    os.environ['SDL_VIDEODRIVER'] = "x11"

pygame.display.init()
pygame.font.init()   # << necessary to avoid "font not initialized" error

# create pygame surface bound to the Tk frame
screen = pygame.display.set_mode((LEFT_WIDTH, LEFT_HEIGHT))
pygame.display.update()

# prepare a pygame font
py_font = pygame.font.SysFont("consolas", 16)

# ---------------- Drawing functions (pygame) ----------------
def draw_interwoven(surface, x_off_px, wraps, phase):
    """Draw interwoven lattice moving according to x_off_px and phase, and return current diameter"""
    surface.fill((12, 14, 18))
    y_center = LEFT_HEIGHT // 2
    current_diam = int(BASE_DIAM_PX + wraps * TAPE_THICKNESS_PX)
    radius = current_diam / 2

    # base pipe band
    rect = pygame.Rect(0, int(y_center - radius), LEFT_WIDTH, int(2*radius))
    pygame.draw.rect(surface, PIPE_COLOR, rect)

    # interwoven helical: two opposite sine sets
    stripe_spacing = max(32, radius * 0.5)
    stripe_width = max(2, int(radius * 0.06))
    amp = radius * 0.45

    for set_idx, (dir_sign, ph_off) in enumerate(((1, 0.0), (-1, math.pi))):
        color = (255, 245, 180) if set_idx == 0 else (200, 245, 255)
        step = 6
        last = None
        for x in range(0, LEFT_WIDTH + step, step):
            # incorporate x_off_px into phase for movement
            y = int(y_center + amp * math.sin(((x + x_off_px*0.6) / stripe_spacing) * 2 * math.pi * dir_sign + phase + ph_off))
            if last:
                pygame.draw.line(surface, color, last, (x, y), stripe_width)
            last = (x, y)

    # ticks: every 10 m
    visible_w = LEFT_WIDTH
    scale = visible_w / PIPE_LENGTH_PX
    for meter in range(0, int(PIPE_LENGTH_M) + 1, 10):
        tick_x = int(meter * PIXELS_PER_METER * scale)
        # adjust by x_off_px
        px = int((tick_x - x_off_px*scale) % visible_w)
        if 0 <= px <= visible_w:
            pygame.draw.line(surface, (230,230,230), (px, int(y_center + radius)), (px, int(y_center + radius + 10)), 2)
            text_surf = py_font.render(f"{meter}m", True, (230,230,230))
            surface.blit(text_surf, (px - text_surf.get_width()//2, int(y_center + radius + 12)))

    # top-left status
    status_surf = py_font.render(f"Diam: {current_diam}px  Wraps: {wraps}", True, (240,240,240))
    surface.blit(status_surf, (8,8))

    pygame.display.update()
    return current_diam


def draw_helical_pipe(surface, x_offset, wrap_count, flow_phase, direction, speed):
    """Draw a helical tape-wrapped pipe with moving stripes and meter ticks."""
    surface.fill((12, 14, 18))
    y_center = LEFT_HEIGHT // 2
    diameter = BASE_DIAM_PX + wrap_count * TAPE_THICKNESS_PX
    radius = diameter / 2

    # Draw background pipe body
    pygame.draw.rect(surface, PIPE_COLOR, (0, y_center - radius, LEFT_WIDTH, diameter), border_radius=int(radius))

    # Simulate helical tape using sine waves
    stripe_count = 10
    for i in range(stripe_count):
        phase_shift = flow_phase + (i * (math.pi * 2 / stripe_count))
        color = TAPE_COLORS[i % len(TAPE_COLORS)]
        points = []
        for x in range(0, LEFT_WIDTH, 8):
            y = y_center + radius * math.sin(0.02 * (x * direction) + phase_shift + x_offset * 0.002)
            points.append((x, y))
        pygame.draw.lines(surface, color, False, points, 3)

    # Draw meter ticks every 10 m
    visible_w = LEFT_WIDTH
    scale = visible_w / PIPE_LENGTH_PX
    for meter in range(0, int(PIPE_LENGTH_M) + 1, 10):
        tick_x = int(meter * PIXELS_PER_METER * scale)
        if 0 <= tick_x <= LEFT_WIDTH:
            pygame.draw.line(surface, (220, 220, 220),
                             (tick_x, y_center + radius),
                             (tick_x, y_center + radius + 10), 2)
            label = py_font.render(f"{meter}m", True, (220, 220, 220))
            surface.blit(label, (tick_x - label.get_width() // 2, y_center + radius + 12))

    # Display wrap stats
    text = py_font.render(f"Diameter: {diameter:.1f}px | Wraps: {wrap_count}", True, (255, 255, 255))
    surface.blit(text, (8, 8))

    pygame.display.update()
    return diameter


# ---------------- Sensor simulation + helpers ----------------
def simulate_realistic_pressure_temp(phase_val):
    # pressure in kPa centered at 100
    p = PRESSURE_BASE_KPA + PRESSURE_VAR_KPA * math.sin(phase_val / 3.0) + random.uniform(-1.0, 1.0)
    # temperature in C centered at 40
    t = TEMP_BASE_C + TEMP_VAR_C * math.sin(phase_val / 5.0) + random.uniform(-0.4, 0.4)
    # Substrate Temperature
    s = TEMP_BASE_C + TEMP_VAR_C * math.sin(phase_val / 4.0) + random.uniform(-0.4, 0.4)

    return round(p, 3), round(t, 2), round(s, 2)


def append_sample(pos_m, p_kpa, t_c, s_c):
    global samples
    samples.append((pos_m, p_kpa, t_c, s_c))


def get_recent_window(pos_now, window_m=ROLL_WINDOW_M):
    """Return arrays of pressure/temp for samples with pos in (pos_now - window_m, pos_now]"""
    if not samples:
        return np.array([]), np.array([]), np.array([])
    arr = np.array(samples)
    xs = arr[:, 0].astype(float)
    ps = arr[:, 1].astype(float)
    ts = arr[:, 2].astype(float)
    ss = arr[:, 3].astype(float)
    mask = (xs <= pos_now) & (xs >= pos_now - window_m)

    return xs[mask], ps[mask], ts[mask], ss[mask]

# ------------------------------------- Plot update --------------------------------[]
def update_plots():
    global samples, position_m
    ax_ts.clear()
    ax2.clear()
    ax_hist.clear()
    ax_hist2.clear()
    ax_hist3.clear()

    if len(samples) == 0:
        canvas_fig.draw()
        return

    arr = np.array(samples)
    xs = arr[:, 0].astype(float)
    ps = arr[:, 1].astype(float)
    ts = arr[:, 2].astype(float)
    ss = arr[:, 3].astype(float)

    # time series last TS_WINDOW_M meters
    pos_now = position_m
    mask_ts = (xs >= max(0, pos_now - TS_WINDOW_M)) & (xs <= pos_now)
    xs_ts = xs[mask_ts]
    ps_ts = ps[mask_ts]
    ts_ts = ts[mask_ts]
    ss_ss = ss[mask_ts]

    if xs_ts.size > 0:
        ax_ts.plot(xs_ts, ps_ts, color=P_COLOR, label="[RP] (kPa)")
        ax_ts.set_ylabel("Pressure (kPa)", color=P_COLOR)
        ax2.plot(xs_ts, ts_ts, color=T_COLOR, label="[TT] (°C)")
        ax2.plot(xs_ts, ss_ss, color=S_COLOR, label="[ST] (°C)")
        ax2.set_ylabel("Temperature (°C)", color=T_COLOR)
        # plt.rcParams.update({'font.size': 7})
        ax_ts.legend(loc='upper right')
        ax2.legend(loc='lower right')

        ax_ts.set_xlim(max(0, pos_now - TS_WINDOW_M), pos_now + 0.01)

        # rolling mean/std over the recent 1m window (for display and shading)
        xr, pr, tr, sr = get_recent_window(pos_now, ROLL_WINDOW_M)
        if pr.size > 0:
            mean_p = float(np.mean(pr))
            std_p = float(np.std(pr))
            # show shaded band ±1σ using the full xs_ts domain
            if xs_ts.size > 0:
                ax_ts.fill_between(xs_ts, mean_p - std_p, mean_p + std_p, color=P_COLOR, alpha=0.12)
        if tr.size > 0:
            mean_t = float(np.mean(tr))
            std_t = float(np.std(tr))
            if xs_ts.size > 0:
                ax2.fill_between(xs_ts, mean_t - std_t, mean_t + std_t, color=T_COLOR, alpha=0.12)
    ax_ts.set_title("Last 5 m: [RP] | [TT] | [ST] (shaded ±1σ over last 1 m)")

    # ------------------------------------------[Roller Pressure]
    # Histograms (last 1 m)
    xr, pr, tr, sr = get_recent_window(pos_now, ROLL_WINDOW_M)
    if pr.size > 0:
        mean_p = float(np.mean(pr)); std_p = float(np.std(pr))
        color_p = (0.25, 0.6, 0.0) if std_p <= 1.0 else (0.8, 0.3, 0.0)
        ax_hist.hist(pr, bins=8, density=True, color=color_p, alpha=0.8, edgecolor='k')
        # gaussian overlay
        try:
            xs_line = np.linspace(pr.min(), pr.max(), 200)
            pdf = (1.0/(std_p * np.sqrt(2*np.pi))) * np.exp(-0.5 * ((xs_line - mean_p)/std_p)**2) if std_p>0 else np.zeros_like(xs_line)
            # scale pdf to density (already pdf)
            ax_hist.plot(xs_line, pdf, color='k', lw=1)
        except Exception:
            pass
        ax_hist.set_title(f"[RP] (1m) μ={mean_p:.2f} σ={std_p:.3f}")
    else:
        ax_hist.set_title("[RP] (1m) — no data")
    # ------------------------------------------[Tape Temperature]
    if tr.size > 0:
        mean_t = float(np.mean(tr))
        std_t = float(np.std(tr))
        color_t = (0.25, 0.6, 0.0) if std_t <= 0.8 else (0.8, 0.3, 0.0)
        ax_hist2.hist(tr, bins=8, density=True, color=color_t, alpha=0.8, edgecolor='k')
        try:
            xs_line = np.linspace(tr.min(), tr.max(), 200)
            pdf = (1.0/(std_t * np.sqrt(2*np.pi))) * np.exp(-0.5*((xs_line - mean_t)/std_t)**2) if std_t > 0 else np.zeros_like(xs_line)
            ax_hist2.plot(xs_line, pdf, color='k', lw=1)
        except Exception:
            pass
        ax_hist2.set_title(f"[ST] (1m) μ={mean_t:.2f} σ={std_t:.3f}")
    else:
        ax_hist2.set_title("[ST] (1m) — no data")
    # ------------------------------------------[Substrate Temp]
    if sr.size > 0:
        mean_s = float(np.mean(sr))
        std_s = float(np.std(sr))
        color_t = (0.25, 0.6, 0.0) if std_s <= 0.8 else (0.8, 0.3, 0.0)
        ax_hist3.hist(sr, bins=8, density=True, color=color_t, alpha=0.8, edgecolor='k')
        try:
            xs_line = np.linspace(sr.min(), sr.max(), 200)
            pdf = (1.0/(std_t * np.sqrt(2*np.pi))) * np.exp(-0.5 * ((xs_line - mean_s)/std_s)**2) if std_s > 0 else np.zeros_like(xs_line)
            ax_hist3.plot(xs_line, pdf, color='k', lw=1)
        except Exception:
            pass
        ax_hist3.set_title(f"[ST] (1m) μ={mean_s:.2f} σ={std_s:.3f}")
    else:
        ax_hist3.set_title("[ST] (1m) — no data")

    f.tight_layout()
    canvas_fig.draw()


def step():
    global flow_phase, x_offset_px, position_m, last_sample_pos, wrap_count, is_running, buffer_df

    # advance visuals / sampling
    if is_running:
        # move by SAMPLE_STEP_M each sample tick (user wanted every 0.25 m)
        # This moves the simulation by 0.25 m per step; if you prefer slower, reduce sample rate or add internal frames.
        delta_m = SAMPLE_STEP_M * direction
        position_m += delta_m
        x_offset_px += delta_m * PIXELS_PER_METER
        flow_phase += 0.6 * direction

        # clamp and stop at ends, increment wraps
        if position_m >= PIPE_LENGTH_M:
            position_m = PIPE_LENGTH_M
            is_running = False
            wrap_count += 1
        elif position_m <= 0:
            position_m = 0.0
            is_running = False
            wrap_count += 1

        # sample sensors at each step
        if position_m - last_sample_pos >= SAMPLE_STEP_M - 1e-9 or last_sample_pos - position_m >= SAMPLE_STEP_M - 1e-9:
            p_kpa, t_c, s_c = simulate_realistic_pressure_temp(flow_phase)
            append_sample(position_m, p_kpa, t_c, s_c)
            last_sample_pos = position_m

    # draw Pygame into left frame
    try:
        # current_diam = draw_interwoven(screen, x_offset_px, wrap_count, flow_phase)
        current_diam = draw_helical_pipe(screen, x_offset_px, wrap_count, flow_phase, direction, SAMPLE_STEP_M)

    except Exception as e:
        print("Pygame draw error:", e)

    # update labels: current and rolling stats
    xr, pr, tr, sr = get_recent_window(position_m, ROLL_WINDOW_M)
    cur_p = samples[-1][1] if samples else None
    cur_t = samples[-1][2] if samples else None
    cur_s = samples[-1][3] if samples else None

    if cur_p is None:
        lbl_pressure.config(text="Roller Pressure: - kPa")
        lbl_temp.config(text="Tape Temperature: - °C")
        lbl_stemp.config(text="Subst Temperature: - °C")
        lbl_roll1.config(text="Rolling (1 m): μ [RP]=- σ [RP]=-")
        lbl_roll2.config(text="Rolling (1 m): μ [TT]=- σ [TT]=-")
        lbl_roll3.config(text="Rolling (1 m): μ [ST]=- σ [ST]=-")
    else:
        p_mean = float(np.mean(pr)) if pr.size>0 else float('nan')
        p_std = float(np.std(pr)) if pr.size>0 else float('nan')
        t_mean = float(np.mean(tr)) if tr.size>0 else float('nan')
        t_std = float(np.std(tr)) if tr.size>0 else float('nan')
        # ------------------
        st_mean = float(np.mean(sr)) if sr.size > 0 else float('nan')
        st_std = float(np.std(sr)) if sr.size > 0 else float('nan')

        lbl_pressure.config(text=f"Roller Pressure: {cur_p:.2f} kPa")
        lbl_temp.config(text=f"Tape Temperature: {cur_t:.2f} °C")
        lbl_stemp.config(text=f"Subst Temperature: {cur_s:.2f} °C")

        lbl_roll1.config(text=f"Rolling (1 m): μ [RP]={p_mean:.2f} σ [RP]={p_std:.3f}")
        lbl_roll2.config(text=f"Rolling (1 m): μ [TT]={t_mean:.2f} σ [TT]={t_std:.3f}")
        lbl_roll3.config(text=f"Rolling (1 m): μ [ST]={st_mean:.2f} σ [ST]={st_std:.3f}")

    # update plots occasionally (not necessarily every step to save CPU)
    update_plots()
    root.after(int(1000 / FPS), step)

#---------------- Key handlers ----------------
def on_key(event):
    global is_running, direction, samples
    k = event.keysym
    if k == "space":
        is_running = not is_running
    elif k == "Left":
        direction = -1
        is_running = True
    elif k == "Right":
        direction = 1
        is_running = True
    elif k in ("r", "R"):
        samples.clear()
    elif k == "Escape":
        # save and quit
        if samples:
            df = pd.DataFrame(samples, columns=["position_m","pressure_kpa","temp_c"])
            df.to_csv("wrap_data.csv", index=False)
            print("Saved wrap_data.csv")
        pygame.quit()
        root.quit()
        root.destroy()
        sys.exit(0)

root.bind_all("<Key>", on_key)

# ---------------- Start ----------------
step()
root.mainloop()

# -------------------------------------- FINAL EDITION ------------------------------------------------[4]

# import tkinter as tk
# from tkinter import ttk
# from threading import Thread
# from queue import Queue
# # from sqlalchemy import create_engine, text
# import pandas as pd
# import numpy as np
# import pygame
# import random, time, math
# from datetime import datetime
#
# # --------------------------------------------------------------------------
# # 1️ SQL SERVER CONFIGURATION
# # --------------------------------------------------------------------------
# # SERVER = "127.0.0.1"
# # DATABASE = "DAQ_sSPC"
# # USERNAME = "TCP01"
# # PASSWORD = "Testing27!"
# # TEMPLATE_TABLE = "pipe_data_template"
# #
# # conn_str = (
# #     f"mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}"
# #     "?driver=ODBC+Driver+17+for+SQL+Server"
# # )
# # engine = create_engine(conn_str)
#
#
# # --------------------------------------------------------------------------
# # 2️ CREATE TABLE FROM TEMPLATE
# # --------------------------------------------------------------------------
# # def create_table_from_template(engine, template_table):
# #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# #     new_table = f"pipe_data_run_{timestamp}"
# #     with engine.begin() as conn:
# #         conn.execute(text(f"SELECT TOP 0 * INTO {new_table} FROM {template_table};"))
# #     print(f"[SQL] Created new table: {new_table}")
# #     return new_table
# #
# #
# # table_name = create_table_from_template(engine, TEMPLATE_TABLE)
# # buffer_df = pd.DataFrame()
# # export_queue = Queue()
#
#
# # --------------------------------------------------------------------------
# # 3️ TKINTER MAIN WINDOW
# # --------------------------------------------------------------------------
# root = tk.Tk()
# root.title("Helical Tape Wrapping Simulation Dashboard")
#
# # Layout frames
# main_frame = tk.Frame(root, bg="#111")
# main_frame.pack(fill="both", expand=True)
#
# # Left view port
# left_frame = tk.Frame(main_frame, bg="black", width=700, height=500)
# left_frame.pack(side="left", fill="both", expand=True)
#
# # right view port
# right_frame = tk.Frame(main_frame, bg="#222", width=400)
# right_frame.pack(side="right", fill="y")
#
# # bottom view port
# bottom_frame = tk.Frame(root, bg="#111", height=40)
# bottom_frame.pack(fill="x")
#
# # SQL LED
# sql_status_var = tk.StringVar(value="SQL: Idle")
# sql_label = tk.Label(bottom_frame, textvariable=sql_status_var, fg="#ccc", bg="#111", font=("Consolas", 12))
# sql_label.pack(side="left", padx=10)
#
# sql_led = tk.Canvas(bottom_frame, width=20, height=20, bg="#111", highlightthickness=0)
# sql_led.pack(side="left", padx=(0, 10))
# led_circle = sql_led.create_oval(4, 4, 16, 16, fill="#555")
#
# def set_led(color):
#     sql_led.itemconfig(led_circle, fill=color)
#
#
# # --------------------------------------------------------------------------
# # 4️ BACKGROUND SQL EXPORT THREAD
# # --------------------------------------------------------------------------
# # def export_worker():
# #     while True:
# #         batch = export_queue.get()
# #         if batch is None:
# #             break
# #
# #         root.after(0, lambda: sql_status_var.set("SQL: Saving..."))
# #         root.after(0, lambda: set_led("#00FF00"))
# #
# #         try:
# #             batch.to_sql(table_name, con=engine, if_exists='append', index=False)
# #         except Exception as e:
# #             print("[SQL ERROR]", e)
# #             root.after(0, lambda: set_led("#FF0000"))
# #             root.after(0, lambda: sql_status_var.set("SQL: ERROR"))
# #             time.sleep(1)
# #         else:
# #             root.after(1000, lambda: set_led("#555"))
# #             root.after(1000, lambda: sql_status_var.set("SQL: Idle"))
# #
# #         export_queue.task_done()
# #         time.sleep(0.1)
# #
# # export_thread = Thread(target=export_worker, daemon=True)
# # export_thread.start()
#
#
# # --------------------------------------------------------------------------
# # 5️ PYGAME EMBEDDED INTO TKINTER
# # --------------------------------------------------------------------------
# embed = tk.Frame(left_frame, width=700, height=500)
# embed.pack(fill="both", expand=True)
# embed.update()
#
# os_env = pygame.display.set_mode
# os_env = pygame.display.set_mode
# os_env = pygame.display.set_mode
# os_env = pygame.display.set_mode
#
# os_env = pygame.display.set_mode
# os_env = pygame.display.set_mode
# os_env = pygame.display.set_mode
# os_env = pygame.display.set_mode
#
# os_env = pygame.display.set_mode
# os_env = pygame.display.set_mode
# os_env = pygame.display.set_mode
# os_env = pygame.display.set_mode
#
# # Tkinter embedding trick
# os_env = pygame.display.set_mode
# embed_id = embed.winfo_id()
# pygame.display.init()
# pygame.display.set_mode((700, 500), 0, 32)
# pygame.display.set_caption("Helical Tape Wrapping Simulation")
#
# surface = pygame.display.get_surface()
# clock = pygame.time.Clock()
#
# # --------------------------------------------------------------------------
# # 6️ SIMULATION PARAMETERS
# # --------------------------------------------------------------------------
# WIDTH, HEIGHT = 700, 500
# BASE_DIAMETER_PX = 80
# TAPE_THICKNESS_PX = 1
# PIPE_LENGTH_METERS = 100
# PIXELS_PER_METER = 10
# TAPE_COLORS = [(180, 180, 255), (120, 200, 255)]
# PIPE_COLOR = (40, 40, 40)
# direction = 1
# wrap_count = 0
# flow_phase = 0
# speed = 2
#
# pressure_window, temp_window = [], []
# buffer_df = pd.DataFrame()
# pipe_position = 0.0
#
#
# # --------------------------------------------------------------------------
# # 7️ DRAW FUNCTION (Helical + diameter growth)
# # --------------------------------------------------------------------------
# def draw_helical_pipe(surface, wrap_count, flow_phase):
#     y_center = HEIGHT // 2
#     diameter = BASE_DIAMETER_PX + wrap_count * TAPE_THICKNESS_PX
#     radius = diameter / 2
#
#     # Background pipe
#     pygame.draw.rect(surface, PIPE_COLOR, (0, y_center - radius, WIDTH, diameter), border_radius=int(radius))
#
#     # Helical stripes
#     stripe_count = 8
#     for i in range(stripe_count):
#         color = TAPE_COLORS[i % len(TAPE_COLORS)]
#         phase_shift = flow_phase + (i * (math.pi * 2 / stripe_count))
#         points = []
#         for x in range(0, WIDTH, 8):
#             y = y_center + radius * math.sin(0.02 * x + phase_shift)
#             points.append((x, y))
#         pygame.draw.lines(surface, color, False, points, 3)
#
#     # Meter ticks
#     for meter in range(0, PIPE_LENGTH_METERS + 1, 10):
#         tick_x = int(meter * PIXELS_PER_METER)
#         if 0 <= tick_x <= WIDTH:
#             pygame.draw.line(surface, (220, 220, 220),
#                              (tick_x, y_center + radius),
#                              (tick_x, y_center + radius + 10), 1)
#
#     return diameter
#
#
# # --------------------------------------------------------------------------
# # 8️ MAIN LOOP UPDATER
# # --------------------------------------------------------------------------
# def update_loop():
#     global wrap_count, flow_phase, pipe_position, buffer_df
#
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             on_close()
#
#     # Simulate readings
#     pipe_position += 0.25
#     current_pressure = random.uniform(95, 105)
#     current_temp = random.uniform(20, 60)
#     pressure_window.append(current_pressure)
#     temp_window.append(current_temp)
#
#     if len(pressure_window) > 4:
#         pressure_window.pop(0)
#         temp_window.pop(0)
#
#     mean_p, std_p = np.mean(pressure_window), np.std(pressure_window)
#     mean_t, std_t = np.mean(temp_window), np.std(temp_window)
#
#     # Update buffer
#     new_row = {
#         "timestamp": datetime.now(),
#         "meter_position": pipe_position,
#         "pressure": current_pressure,
#         "temperature": current_temp,
#         "mean_pressure": mean_p,
#         "std_pressure": std_p,
#         "mean_temp": mean_t,
#         "std_temp": std_t,
#     }
#     buffer_df = pd.concat([buffer_df, pd.DataFrame([new_row])], ignore_index=True)
#
#     if len(buffer_df) >= 10000:
#         batch = buffer_df.copy()
#         buffer_df = pd.DataFrame()
#         # export_queue.put(batch)
#         root.after(0, lambda: set_led("#FFFF00"))
#
#     # Update animation
#     surface.fill((0, 0, 0))
#     diameter = draw_helical_pipe(surface, wrap_count, flow_phase)
#     wrap_count += 1 if pipe_position % 1 == 0 else 0
#     flow_phase += 0.1
#     pygame.display.flip()
#     clock.tick(30)
#
#     # Schedule next update
#     root.after(33, update_loop)
#
#
# # --------------------------------------------------------------------------
# # 9️ CLEANUP HANDLER
# # --------------------------------------------------------------------------
# def on_close():
#     # export_queue.put(None)
#     root.destroy()
#     pygame.quit()
#     print("Exiting...")
#
# root.protocol("WM_DELETE_WINDOW", on_close)
#
# # --------------------------------------------------------------------------
# # 10 START
# # --------------------------------------------------------------------------
# root.after(500, update_loop)
# root.mainloop()
