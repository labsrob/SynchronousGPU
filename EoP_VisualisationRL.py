# --------------------------------------------FINAL SAMPLE --------------------------------------[FAVOURITE 2]

"""
Helical Tape Wrapping Machine Simulation with Pressure & Temperature
- Sampling every 0.25 m
- Rolling mean & std over last 1 m
- Color-coded histograms
Controls:
  → / ← : start wrapping right / left (when stopped)
  SPACE : pause
  R     : clear samples
  ESC   : quit (auto-save CSV)
"""
import pygame, sys, math, random, statistics, time
import pandas as pd
import numpy as np

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 1500, 750
FPS = 60

PIPE_LENGTH_METERS = 100
PIXELS_PER_METER = 8

BASE_DIAMETER_PX = 80
TAPE_THICKNESS_MM = 0.5
VISUAL_SCALE = 80            # exaggeration factor for visibility
TAPE_THICKNESS_PX = (TAPE_THICKNESS_MM / 1000) * PIXELS_PER_METER * 80
PIPE_LENGTH = PIPE_LENGTH_METERS * PIXELS_PER_METER

ACCEL = 1.8
DECEL = 2.8
MAX_SPEED = 1.2  # to use (100cm per sec @ 6m/min)

SAMPLE_INTERVAL_M = 0.25
ROLL_WINDOW_M = 1.0

PRESSURE_STD_THRESHOLD = 0.05
PRESSURE_STD_MAX = 0.25
TEMP_STD_THRESHOLD = 0.2
TEMP_STD_MAX = 2.0
STEMP_STD_THRESHOLD = 0.2
STEMP_STD_MAX = 2.0


BG = (22,24,28)
PIPE_COLOR = (70,130,220)
TAPE_COLORS = [(255,255,180),(200,255,255),(255,200,255),(200,255,200)]
PRESSURE_COLOR = (0,53,255) # Blue
TEMP_COLOR = (255,0,64)     # Red
STEMP_COLOR = (0,255,139)   # Green
STATS_BG = (40,45,55)

# ---------------- INIT ----------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Magma Tape Laying Simulation")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Consolas", 18)
bigfont = pygame.font.SysFont("Consolas", 22)

# ---------------- STATE ----------------
direction = 1
position_m = 0.0
x_offset = 0.0
is_running = True
wrap_count = 0
speed = 0.0
flow_phase = 0.0
sensor_data = []
last_sample_position = 0.0
tape_thickness_px = (TAPE_THICKNESS_MM / 1000) * PIXELS_PER_METER * VISUAL_SCALE  # scaled up visually

# ---------------- HELPERS ----------------
def simulate_pressure_temp():
    base_p = 2.0 + random.uniform(-0.12,0.12)
    p = round(base_p + random.uniform(-0.03,0.03),3)
    t = round(25.0 + (p-2.0)*8 + random.uniform(-0.3,0.3),2)
    s = round(23.0 + (p - 2.0) * 8 + random.uniform(-0.3, 0.3), 2)
    return p, t, s


def color_from_std(std_val, threshold, max_std):
    if std_val <= threshold: return (60,200,80)
    ratio = min(1.0, max(0.0, (std_val - threshold)/(max_std-threshold)))
    if ratio < 0.5:
        t = ratio/0.5
        r = int(60 + (255-60)*t)
        g = int(200 + (255-200)*t)
        return (r,g,60)
    else:
        t = (ratio-0.5)/0.5
        r = 255
        g = int(255-(255-80)*t)
        return (r,g,60)

# -------------------------------------------------------------------- DRAWING ----------------

def draw_interwoven_lattice(surface, x_offset, wraps, phase, direction):
    """
    Draw a lattice-style interwoven helical tape.
    Two sets of diagonal stripes cross each other.
    Pipe grows in diameter with wraps.
    """
    y_center = HEIGHT // 2
    current_diameter = int(BASE_DIAMETER_PX + wraps * TAPE_THICKNESS_PX)
    radius = current_diameter / 2
    # Draw background pipe body
    pygame.draw.rect(surface, PIPE_COLOR, (0, y_center - radius, WIDTH, current_diameter), border_radius=int(radius))

    # lattice parameters
    stripe_spacing = max(30, radius * 0.6)
    stripe_width = max(3, radius * 0.08)
    amp = radius * 0.5

    # two crossing directions
    for direction_sign, phase_offset in [(1, 0), (-1, math.pi)]:
        color = TAPE_COLORS[wraps % len(TAPE_COLORS)]
        points = []
        step = 6
        for x in range(0, WIDTH + step, step):
            y = y_center + amp * math.sin((x / stripe_spacing) * 2 * math.pi * direction_sign + phase + phase_offset)
            points.append((x, y))
        pygame.draw.lines(surface, color, False, points, int(stripe_width))

    # ticks every 10 m
    for meter in range(0, PIPE_LENGTH_METERS + 1, 10):
        tick_x = int((meter * PIXELS_PER_METER - x_offset) % (PIPE_LENGTH_METERS * PIXELS_PER_METER))
        if 0 <= tick_x <= WIDTH:
            pygame.draw.line(surface, (230, 230, 230), (tick_x, y_center + radius), (tick_x, y_center + radius + 12), 2)
            lbl = font.render(f"{meter}m", True, (230, 230, 230))
            surface.blit(lbl, (tick_x - lbl.get_width() // 2, y_center + radius + 14))

    return y_center, current_diameter

def draw_helical_pipe(surface, x_offset, wrap_count, flow_phase, direction, speed):
    y_center = HEIGHT // 2
    diameter = BASE_DIAMETER_PX + wrap_count * tape_thickness_px
    radius = diameter / 2
    color = TAPE_COLORS[wrap_count % len(TAPE_COLORS)]
    # Draw background pipe body
    pygame.draw.rect(surface, PIPE_COLOR, (0, y_center - radius, WIDTH, diameter), border_radius=int(radius))

    # Simulate helical stripes using sine waves
    stripe_count = 10
    for i in range(stripe_count):
        phase_shift = flow_phase + (i * (math.pi * 2 / stripe_count))
        points = []
        for x in range(0, WIDTH, 10):
            y = y_center + radius * math.sin(0.02 * (x * direction) + phase_shift)
            points.append((x, y))
        pygame.draw.lines(surface, color, False, points, 3)

    # Meter ticks every 10m
    for meter in range(0, PIPE_LENGTH_METERS + 1, 10):
        tick_x = int((meter * PIXELS_PER_METER - x_offset) % PIPE_LENGTH)
        if 0 <= tick_x <= WIDTH:
            pygame.draw.line(surface, (220, 220, 220),
                             (tick_x, y_center + radius),
                             (tick_x, y_center + radius + 10), 1)
            label = font.render(f"{meter}m", True, (220, 220, 220))
            surface.blit(label, (tick_x - 10, y_center + radius + 12))

    return y_center, diameter


def draw_time_series(surface, data):
    chart_w, chart_h = WIDTH-1060, 150  # Box width & height
    chart_x, chart_y = 1020, HEIGHT-chart_h - 30       # 490
    pygame.draw.rect(surface, STATS_BG, (chart_x + 30, chart_y, chart_w, chart_h), border_radius=8)
    pygame.draw.rect(surface, (100,100,100), (chart_x + 30, chart_y, chart_w, chart_h),2)

    if not data: return
    pres_vals = [p for _, p, _, _ in data]
    temp_vals = [t for _, _, t, _ in data]
    stemp_vals = [s for _, _, _, s in data]

    max_p, min_p = max(pres_vals), min(pres_vals)
    max_t, min_t = max(temp_vals), min(temp_vals)
    max_s, min_s = max(stemp_vals), min(stemp_vals)

    pts_pres = []
    pts_temp = []
    pts_stemp = []
    visible = data[-chart_w:]

    # Compute for Min/Max ----------------------------------------------------------[]
    for i,(m, p, t, s) in enumerate(visible):
        x = chart_x + 30 +i
        y_p = chart_y + chart_h - int((p - min_p) / (max_p - min_p + 1e-6) * chart_h)
        y_t = chart_y + chart_h - int((t - min_t) / (max_t - min_t + 1e-6) * chart_h)
        y_s = chart_y + chart_h - int((s - min_s) / (max_s - min_s + 1e-6) * chart_h)

        pts_pres.append((x,y_p))
        pts_temp.append((x,y_t))
        pts_stemp.append((x, y_s))

    if len(pts_pres) > 1: pygame.draw.lines(surface,PRESSURE_COLOR,False,pts_pres,2)
    if len(pts_temp) > 1: pygame.draw.lines(surface,TEMP_COLOR,False,pts_temp,2)
    if len(pts_stemp) > 1: pygame.draw.lines(surface, STEMP_COLOR, False, pts_stemp, 2)
    surface.blit(font.render("Dist - Blue [RP] | Red [TT] | Green [ST]", True, (220,220,220)),(chart_x+50, chart_y-20)) #20


def draw_histogram(surface, values, pos_x, title, color):
    if not values: return
    box_w, box_h = 320, 150  # position of Critical params []
    box_x, box_y = pos_x+85, HEIGHT-box_h - 30

    pygame.draw.rect(surface, STATS_BG, (box_x, box_y, box_w, box_h), border_radius=8)
    pygame.draw.rect(surface, (90,90,90), (box_x, box_y, box_w, box_h), 2)

    bins = np.linspace(min(values), max(values), 32)
    hist, edges = np.histogram(values, bins=bins)

    max_h = max(hist) if hist.size>0 and max(hist)>0 else 1
    bw = (box_w-28)/len(hist)

    for i,h in enumerate(hist):
        x = box_x+14+i*bw
        bh = (h/max_h)*(box_h-40)
        y = box_y+box_h-bh-14
        pygame.draw.rect(surface,color,(x,y,bw*0.9,bh))
    surface.blit(font.render(title, True, (220,220,220)), (box_x+10, box_y-20))


def draw_stats_panel(surface, data, pos_m):
    recent_pres = [p for (m, p, t, s) in data if 0<=abs(pos_m)-m<=ROLL_WINDOW_M]
    recent_temp = [t for (m, p, t, s) in data if 0<=abs(pos_m)-m<=ROLL_WINDOW_M]
    # -- Add -----
    recent_stemp = [s for (m, p, t, s) in data if 0 <= abs(pos_m) - m <= ROLL_WINDOW_M]

    cur_p, cur_t, cur_s = (data[-1][1], data[-1][2], data[-1][3]) if data else (None,None, None)
    # print('TP02', cur_p, cur_t, cur_s)

    mean_p = statistics.mean(recent_pres) if recent_pres else None
    std_p = statistics.pstdev(recent_pres) if recent_pres and len(recent_pres)>1 else 0.0
    mean_t = statistics.mean(recent_temp) if recent_temp else None
    std_t = statistics.pstdev(recent_temp) if recent_temp and len(recent_temp)>1 else 0.0
    # ---- Add ------
    mean_s = statistics.mean(recent_stemp) if recent_stemp else None
    std_s = statistics.pstdev(recent_stemp) if recent_stemp and len(recent_stemp) > 1 else 0.0


    box_w, box_h = 320, 150
    box_x, box_y = 10, HEIGHT - box_h - 30
    pygame.draw.rect(surface, STATS_BG, (box_x, box_y, box_w, box_h), border_radius=8) # fill box
    pygame.draw.rect(surface, (100,100,100), (box_x, box_y, box_w, box_h),2) # boarder colour
    lines = [
        f"Position: {pos_m:.2f}m",

        f"Current RP: {cur_p:.3f} bar" if cur_p else "Current RP: -",
        f"Mean RP(1m): {mean_p:.3f} Std: {std_p:.4f}" if mean_p else "Mean RP(1m): -",
        "",
        f"Current TT: {cur_t:.2f} °C" if cur_t else "Current TT: -",
        f"Mean TT(1m): {mean_t:.2f} Std: {std_t:.3f}" if mean_t else "Mean TT(1m): -",
        "",
        f"Current ST: {cur_t:.2f} °C" if cur_s else "Current ST: -",
        f"Mean ST(1m): {mean_s:.2f} Std: {std_s:.3f}" if mean_s else "Mean ST(1m): -",]

    for i,txt in enumerate(lines):
        surface.blit(font.render(txt, True, (230,230,230)), (box_x+10, box_y + 5 + i * 15)) # text
    return recent_pres, recent_temp, recent_stemp


def draw_grand_mean_panel(surface, data, pos_m):
    recent_pres = [p for (m, p, t, s) in data if 0<=abs(pos_m)-m<=ROLL_WINDOW_M]
    recent_temp = [t for (m, p, t, s) in data if 0<=abs(pos_m)-m<=ROLL_WINDOW_M]
    # -- Add -----
    recent_stemp = [s for (m, p, t, s) in data if 0 <= abs(pos_m) - m <= ROLL_WINDOW_M]

    cur_p, cur_t, cur_s = (data[-1][1], data[-1][2], data[-1][3]) if data else (None,None, None)
    # print('TP02', cur_p, cur_t, cur_s)

    gmean_p = statistics.mean(recent_pres) if recent_pres else None
    gstd_p = statistics.pstdev(recent_pres) if recent_pres and len(recent_pres)>1 else 0.0
    gmean_t = statistics.mean(recent_temp) if recent_temp else None
    gstd_t = statistics.pstdev(recent_temp) if recent_temp and len(recent_temp)>1 else 0.0
    # ---- Add ------
    gmean_s = statistics.mean(recent_stemp) if recent_stemp else None
    gstd_s = statistics.pstdev(recent_stemp) if recent_stemp and len(recent_stemp) > 1 else 0.0


    box_w, box_h = 350, 150
    box_x, box_y = 1060, HEIGHT - box_h - 30
    pygame.draw.rect(surface, STATS_BG, (box_x, box_y, box_w, box_h), border_radius=8) # fill box
    pygame.draw.rect(surface, (100,100,100), (box_x, box_y, box_w, box_h),2) # boarder colour
    lines = [
        f"Position: {pos_m:.2f}m",

        f"Current [RP]: {cur_p:.3f} bar" if cur_p else "x̄ of Mean / 1m: -",
        f"x̄ of Mean: {gmean_p:.3f} x̄ of Std: {gstd_p:.4f}" if gmean_p else "x̄ RP(1m): -",
        "",
        f"Current [TT]: {cur_t:.2f} °C" if cur_t else "x̄ of Mean / 1m: -",
        f"x̄ of Mean: {gmean_t:.2f} x̄ of Std: {gstd_t:.3f}" if gmean_t else "x̄ TT(1m): -",
        "",
        f"Current [ST]: {cur_t:.2f} °C" if cur_s else "x̄ of Mean / 1m: -",
        f"x̄ of Mean: {gmean_s:.2f} x̄ of Std: {gstd_s:.3f}" if gmean_s else "x̄ ST(1m): -",]

    for i,txt in enumerate(lines):
        surface.blit(font.render(txt, True, (230,230,230)), (box_x+10, box_y + 5 + i * 15)) # text
    return recent_pres, recent_temp, recent_stemp


# ---------------- MAIN LOOP ----------------
while True:
    dt = clock.tick(FPS)/1000.0

    # events
    for ev in pygame.event.get():
        if ev.type==pygame.QUIT:
            pd.DataFrame(sensor_data, columns=["position_m","pressure_bar","temp_C", "stemp_C"]).to_csv("wrap_data.csv",index=False)
            pygame.quit(); sys.exit()

        if ev.type==pygame.KEYDOWN:
            if ev.key==pygame.K_ESCAPE:
                pd.DataFrame(sensor_data, columns=["position_m","pressure_bar","temp_C", "stemp_C"]).to_csv("wrap_data.csv",index=False)
                pygame.quit(); sys.exit()

            elif ev.key==pygame.K_SPACE: is_running=False

            elif ev.key==pygame.K_r: sensor_data=[]

            elif not is_running:
                if ev.key==pygame.K_RIGHT: direction=1; is_running=True
                elif ev.key==pygame.K_LEFT: direction=-1; is_running=True

    # motion --------
    if is_running and speed<MAX_SPEED: speed=min(MAX_SPEED, speed+ACCEL*dt)
    elif not is_running and speed>0: speed=max(0.0, speed-DECEL*dt)
    if speed>0:
        delta_m = speed *dt * direction
        position_m += delta_m
        x_offset += delta_m*PIXELS_PER_METER
        flow_phase += speed * dt * 2.5 * direction

        if abs(position_m - last_sample_position) >= SAMPLE_INTERVAL_M:
            p, t, s = simulate_pressure_temp()
            # print('TP03', p, t, s)
            sensor_data.append((position_m, p, t, s))
            last_sample_position = position_m

        if position_m>=PIPE_LENGTH_METERS:
            position_m = PIPE_LENGTH_METERS; is_running=False; wrap_count+=1; speed=0.0
        elif position_m<=0:
            position_m=0.0; is_running=False; wrap_count+=1; speed=0.0

    # draw ----------------------------------------------------------------------[]
    screen.fill(BG)
    draw_helical_pipe(screen, x_offset, wrap_count, flow_phase, direction, speed)

    draw_time_series(screen, sensor_data)
    recent_pres, recent_temp , recent_stemp = draw_stats_panel(screen, sensor_data, abs(position_m))

    # Left side Statistic Panel, boarder & Fill
    if recent_pres: draw_histogram(screen, recent_pres, pos_x=250, title="[Roller Pressure]", color=color_from_std(statistics.pstdev(recent_pres) if len(recent_pres)>1 else 0.0, PRESSURE_STD_THRESHOLD, PRESSURE_STD_MAX))
    if recent_temp: draw_histogram(screen, recent_temp, pos_x=440, title="[Tape Temperature]", color=color_from_std(statistics.pstdev(recent_temp) if len(recent_temp)>1 else 0.0, TEMP_STD_THRESHOLD, TEMP_STD_MAX))
    if recent_stemp: draw_histogram(screen, recent_stemp, pos_x=650, title="[Substrate Temperature]", color=color_from_std(statistics.pstdev(recent_stemp) if len(recent_stemp) > 1 else 0.0, STEMP_STD_THRESHOLD, STEMP_STD_MAX))
    # ----------------------------------------------------------

    dir_txt = "→ RIGHT" if direction==1 else "← LEFT"
    status = "RUNNING" if is_running or speed>0 else "STOPPED"
    if wrap_count == 0:
        wrap_count = 1
    header = bigfont.render(f"Dir:{dir_txt} Speed:{speed:.2f} m/s Layer:{wrap_count} Pos:{position_m:.2f}m Status:{status}", True, (230,230,230))
    screen.blit(header, (20,16))
    inst = font.render("SPACE: Pause | ←/→: Start | R: Clear samples | ESC: Quit(save CSV)", True, (200,200,200))
    screen.blit(inst,(20,56))
    pygame.display.flip()
