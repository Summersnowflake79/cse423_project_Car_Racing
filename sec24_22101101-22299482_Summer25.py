
import sys
import random
import math
from time import time

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

window_width = 800
window_height = 800

ground_color = (0.2, 0.6, 0.2)
track_color = (0.5, 0.5, 0.5)

cones = []
trees = []
flowers = []

camera_view = 0


car_x = 15.0
car_z = -5.0
car_angle = 0.0
car_speed = 0.0


checkpoints = [
    {'x': 15, 'z': 26, 'width': 20, 'depth': 2},
    {'x': -15, 'z': 0, 'width': 2, 'depth': 44},
    {'x': 15, 'z': -26, 'width': 20, 'depth': 2},
    {'x': 15.0, 'z': -5.0, 'width': 20, 'depth': 2}
]
current_checkpoint = 0
lap_count = 0

health = 100
max_health = 100
score = 0
level = 1
max_level = 3
laps_required_per_level = {1: 1, 2: 2, 3: 3}
level_lap_target = 1

boost_pads = [
    {'x': 15, 'z': 10, 'width': 10, 'depth': 4, 'active': True},
    {'x': -15, 'z': 10, 'width': 10, 'depth': 4, 'active': True}
]
health_packs = [
    {'x': 0, 'z': -26, 'width': 2, 'depth': 2, 'active': True, 'rotation': 0}
]
treasures = [
    {'x': -5, 'z': 20, 'radius': 1.0, 'active': True},
    {'x': 8, 'z': -10, 'radius': 1.0, 'active': True}
]
nitro_count = 0
nitro_active = False
nitro_end_time = 0.0
nitro_duration = 2.0
nitro_multiplier = 3.0

game_over = False
victory = False
race_started = False

countdown_state = 0
countdown_start_time = 0

checkpoint_last_trigger = []
checkpoint_cooldown_time = 500
level_missions = {
    1: "Mission: Complete 1 lap within the time limit!",
    2: "Mission: Avoid cones and finish 2 laps!",
    3: "Mission: Collect all treasures and finish 3 laps!"
}
level_time_limits = {1: 60, 2: None, 3: None}
time_limit = None
time_remaining = None
level_start_time = 0
level_complete = False
level_complete_time = 0
level_complete_delay = 3000

def ensure_checkpoint_arrays():
    global checkpoint_last_trigger
    n = len(checkpoints)
    if len(checkpoint_last_trigger) != n:
        checkpoint_last_trigger = [0] * n

def init_gl():
    glClearColor(0.8, 0.9, 1.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

def draw_ground():
    glColor3f(*ground_color)
    glBegin(GL_QUADS)
    glVertex3f(-50.0, 0.0, -50.0)
    glVertex3f(-50.0, 0.0, 50.0)
    glVertex3f(50.0, 0.0, 50.0)
    glVertex3f(50.0, 0.0, -50.0)
    glEnd()

def draw_racetrack():
    glColor3f(*track_color)
    outer_x_min, outer_x_max = -20.0, 20.0
    outer_z_min, outer_z_max = -30.0, 30.0
    inner_x_min, inner_x_max = -10.0, 10.0
    inner_z_min, inner_z_max = -22.0, 22.0
    
    glBegin(GL_QUADS)
    glVertex3f(inner_x_min, 0.01, inner_z_max); glVertex3f(inner_x_max, 0.01, inner_z_max)
    glVertex3f(inner_x_max, 0.01, outer_z_max); glVertex3f(inner_x_min, 0.01, outer_z_max)
    glEnd()
    
    glBegin(GL_QUADS)
    glVertex3f(inner_x_min, 0.01, outer_z_min); glVertex3f(inner_x_max, 0.01, outer_z_min)
    glVertex3f(inner_x_max, 0.01, inner_z_min); glVertex3f(inner_x_min, 0.01, inner_z_min)
    glEnd()
    
    glBegin(GL_QUADS)
    glVertex3f(outer_x_min, 0.01, inner_z_min); glVertex3f(inner_x_min, 0.01, inner_z_min)
    glVertex3f(inner_x_min, 0.01, inner_z_max); glVertex3f(outer_x_min, 0.01, inner_z_max)
    glEnd()
    
    glBegin(GL_QUADS)
    glVertex3f(inner_x_max, 0.01, inner_z_min); glVertex3f(outer_x_max, 0.01, inner_z_min)
    glVertex3f(outer_x_max, 0.01, inner_z_max); glVertex3f(inner_x_max, 0.01, inner_z_max)
    glEnd()
    
    glBegin(GL_QUADS)
    glVertex3f(inner_x_max, 0.01, inner_z_max); glVertex3f(outer_x_max, 0.01, inner_z_max)
    glVertex3f(outer_x_max, 0.01, outer_z_max); glVertex3f(inner_x_max, 0.01, outer_z_max)
    glEnd()
    glBegin(GL_QUADS)
    glVertex3f(outer_x_min, 0.01, inner_z_max); glVertex3f(inner_x_min, 0.01, inner_z_max)
    glVertex3f(inner_x_min, 0.01, outer_z_max); glVertex3f(outer_x_min, 0.01, outer_z_max)
    glEnd()
    glBegin(GL_QUADS)
    glVertex3f(outer_x_min, 0.01, outer_z_min); glVertex3f(inner_x_min, 0.01, outer_z_min)
    glVertex3f(inner_x_min, 0.01, inner_z_min); glVertex3f(outer_x_min, 0.01, inner_z_min)
    glEnd()
    glBegin(GL_QUADS)
    glVertex3f(inner_x_max, 0.01, outer_z_min); glVertex3f(outer_x_max, 0.01, outer_z_min)
    glVertex3f(outer_x_max, 0.01, inner_z_min); glVertex3f(inner_x_max, 0.01, inner_z_min)
    glEnd()
    
    start_line_z_pos = -5.0; line_width_z = 2.0; square_side = 1.0
    num_squares_x = int((outer_x_max - inner_x_max) / square_side)
    num_squares_z = int(line_width_z / square_side)
    for j in range(num_squares_z):
        for i in range(num_squares_x):
            if (i + j) % 2 == 0: glColor3f(1.0, 1.0, 1.0)
            else: glColor3f(0.0, 0.0, 0.0)
            x_pos = inner_x_max + (i * square_side)
            z_pos = start_line_z_pos - (line_width_z / 2.0) + (j * square_side)
            glBegin(GL_QUADS)
            glVertex3f(x_pos, 0.02, z_pos); glVertex3f(x_pos + square_side, 0.02, z_pos)
            glVertex3f(x_pos + square_side, 0.02, z_pos + square_side); glVertex3f(x_pos, 0.02, z_pos + square_side)
            glEnd()

def draw_car(x, z, r, g, b, rotation):
    glPushMatrix()
    glTranslatef(x, 0.3, z)
    glRotatef(rotation, 0.0, 1.0, 0.0)
    glColor3f(r, g, b)
    glPushMatrix(); glScalef(0.8, 0.4, 1.6); glutSolidCube(1.0); glPopMatrix()
    glColor3f(0.1, 0.1, 0.1)
    wheel_size = 0.15
    glPushMatrix(); glTranslatef(0.4, -0.2, 0.6); glutSolidCube(wheel_size); glPopMatrix()
    glPushMatrix(); glTranslatef(-0.4, -0.2, 0.6); glutSolidCube(wheel_size); glPopMatrix()
    glPushMatrix(); glTranslatef(0.4, -0.2, -0.6); glutSolidCube(wheel_size); glPopMatrix()
    glPushMatrix(); glTranslatef(-0.4, -0.2, -0.6); glutSolidCube(wheel_size); glPopMatrix()
    glPopMatrix()

def draw_cone(x, z):
    glPushMatrix(); glTranslatef(x, 0.25, z); glRotatef(-90, 1.0, 0.0, 0.0)
    glColor3f(1.0, 0.6, 0.0); glutSolidCone(0.5, 1.0, 10, 10); glPopMatrix()

def draw_tree(x, z):
    glPushMatrix(); glTranslatef(x, 0.0, z)
    glColor3f(0.5, 0.3, 0.1); glPushMatrix(); glRotatef(-90.0, 1.0, 0.0, 0.0)
    quadric = gluNewQuadric(); gluCylinder(quadric, 0.5, 0.5, 2.0, 32, 32); glPopMatrix()
    glColor3f(0.0, 0.5, 0.0); glPushMatrix(); glTranslatef(0.0, 2.0, 0.0)
    glutSolidSphere(1.5, 32, 32); glPopMatrix(); glPopMatrix()

def draw_lake():
    glPushMatrix(); glColor3f(0.6, 0.8, 1.0); glTranslatef(0.0, 0.01, 0.0)
    glRotatef(-90.0, 1.0, 0.0, 0.0); quadric = gluNewQuadric()
    gluDisk(quadric, 0.0, 8.0, 50, 1); gluDeleteQuadric(quadric); glPopMatrix()

def draw_flowers():
    for x, z, r, g, b in flowers:
        glPushMatrix(); glColor3f(r, g, b); glTranslatef(x, 0.05, z)
        glutSolidSphere(0.15, 10, 10); glPopMatrix()

def draw_text(x, y, text, font=GLUT_BITMAP_TIMES_ROMAN_24):
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glColor3f(1.0, 1.0, 1.0); glRasterPos2f(x, y)
    for ch in text: glutBitmapCharacter(font, ord(ch))
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)

def draw_boost_pads():
    for pad in boost_pads:
        glPushMatrix(); glTranslatef(pad['x'], 0.015, pad['z']); glBegin(GL_QUADS)
        glColor3f(0.8, 0.4, 0.1); half_w = pad['width']/2.0; half_d = pad['depth']/2.0
        glVertex3f(-half_w, 0.0, -half_d); glVertex3f(half_w, 0.0, -half_d)
        glVertex3f(half_w, 0.0, half_d); glVertex3f(-half_w, 0.0, half_d)
        glEnd(); glPopMatrix()

def draw_health_packs():
    for hp in health_packs:
        if hp.get('active', True):
            glPushMatrix(); glTranslatef(hp['x'], 0.25, hp['z'])
            glRotatef(hp.get('rotation', 0), 0, 1, 0); glColor3f(1.0, 0.0, 0.0)
            glutSolidCube(0.8); glPopMatrix()

def draw_treasures():
    for t in treasures:
        if t.get('active', True):
            glPushMatrix(); glTranslatef(t['x'], 0.25, t['z'])
            glColor3f(1.0, 0.9, 0.0); glutSolidSphere(0.6, 12, 12); glPopMatrix()

def draw_ui():
    margin = 10
    draw_text(margin, window_height - 30, f"Health: {health}/{max_health}")
    draw_text(margin, window_height - 60, f"Score: {score}")
    draw_text(margin, window_height - 90, f"Level: {level}")
    draw_text(margin, window_height - 120, f"Laps: {lap_count}/{level_lap_target}")
    draw_text(margin, window_height - 150, f"Nitro: {nitro_count}")
    draw_text(window_width - 260, window_height - 30, f"Next Checkpoint: {current_checkpoint + 1}/{len(checkpoints)}")
    if level == 1 and time_limit is not None and time_remaining is not None:
        draw_text(margin, window_height - 180, f"Time: {int(time_remaining)}s")

    if countdown_state > 0 and not level_complete:
        if level in level_missions:
            draw_text(window_width/2 - 250, window_height/2 + 40, level_missions[level])
        draw_text(window_width / 2 - 10, window_height / 2, str(countdown_state), GLUT_BITMAP_TIMES_ROMAN_24)

    if game_over:
        draw_text(window_width / 2 - 80, window_height / 2, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(window_width / 2 - 200, window_height / 2 - 40, "Press 'R' to Restart Level or 'Q' to Quit")
    if victory:
        draw_text(window_width / 2 - 100, window_height / 2, "VICTORY!", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(window_width / 2 - 200, window_height / 2 - 40, "Press 'R' to Play Again or 'Q' to Quit")
    if level_complete:
        draw_text(window_width/2 - 120, window_height/2, "LEVEL COMPLETE!")

def is_on_racetrack(x, z):
    outer_x_min, outer_x_max = -20.0, 20.0; outer_z_min, outer_z_max = -30.0, 30.0
    inner_x_min, inner_x_max = -10.0, 10.0; inner_z_min, inner_z_max = -22.0, 22.0
    is_on_outer = (outer_x_min <= x <= outer_x_max) and (outer_z_min <= z <= outer_z_max)
    is_in_inner_hole = (inner_x_min <= x <= inner_x_max) and (inner_z_min <= z <= inner_z_max)
    return is_on_outer and not is_in_inner_hole

def check_cone_collision(car_x_loc, car_z_loc):
    global health, car_speed
    for cone_x, cone_z in cones:
        if math.sqrt((car_x_loc - cone_x)**2 + (car_z_loc - cone_z)**2) < 1.0:
            health -= 10
            car_speed *= -0.3
            if health < 0: health = 0
            return True
    return False

def rect_contains(obj_x, obj_z, rect):
    half_w = rect.get('width', 0) / 2.0; half_d = rect.get('depth', 0) / 2.0
    return (rect['x']-half_w <= obj_x <= rect['x']+half_w) and \
           (rect['z']-half_d <= obj_z <= rect['z']+half_d)

def circle_contains(obj_x, obj_z, cx, cz, radius):
    return (obj_x - cx)**2 + (obj_z - cz)**2 <= radius**2

def check_checkpoints_and_lap():
    global current_checkpoint, lap_count, checkpoint_last_trigger
    now_ms = glutGet(GLUT_ELAPSED_TIME)
    if not (0 <= current_checkpoint < len(checkpoints)): current_checkpoint = 0
    cp = checkpoints[current_checkpoint]
    if rect_contains(car_x, car_z, cp):
        if (now_ms - checkpoint_last_trigger[current_checkpoint]) > checkpoint_cooldown_time:
            checkpoint_last_trigger[current_checkpoint] = now_ms
            current_checkpoint += 1
            if current_checkpoint >= len(checkpoints):
                lap_complete()
                current_checkpoint = 0
                if checkpoint_last_trigger: checkpoint_last_trigger[0] = now_ms

def lap_complete():
    global lap_count, score, level_complete, level_complete_time, race_started
    lap_count += 1
    score += 50
    if lap_count >= level_lap_target:
        if level >= max_level:
            victory_screen()
        else:
            level_complete = True
            race_started = False
            level_complete_time = glutGet(GLUT_ELAPSED_TIME)

def check_pickups():
    global health, score
    for hp in health_packs:
        if hp.get('active', False) and rect_contains(car_x, car_z, hp):
            hp['active'] = False; health = min(max_health, health + 30); score += 10
    for t in treasures:
        if t.get('active', False) and circle_contains(car_x, car_z, t['x'], t['z'], t['radius']):
            t['active'] = False; score += 25
    for pad in boost_pads:
        if pad.get('active', True) and rect_contains(car_x, car_z, pad):
            apply_boost(pad)

def apply_boost(pad):
    global car_speed, score
    car_speed += 0.8
    car_speed = min(8.0, car_speed)
    score += 5

def use_nitro():
    global nitro_count, nitro_active, nitro_end_time
    if nitro_count > 0 and not nitro_active:
        nitro_count -= 1
        nitro_active = True
        nitro_end_time = glutGet(GLUT_ELAPSED_TIME) + int(1000 * nitro_duration)


def start_race_countdown():
    """Resets the car to the start line and begins the 3-second countdown."""
    global countdown_state, countdown_start_time, race_started
    reset_car_position()
    race_started = False
    if camera_view in [1, 2]:
        countdown_state = 3
        countdown_start_time = glutGet(GLUT_ELAPSED_TIME)
    else:
        countdown_state = 0

def setup_level(level_num):
    global level, lap_count, level_lap_target, time_limit, time_remaining, level_start_time, health
    level = level_num
    lap_count = 0
    level_lap_target = laps_required_per_level.get(level, 1)
    health = max_health
    
    for hp in health_packs: hp['active'] = True
    for t in treasures: t['active'] = False
    
    cones.clear()
    if level == 1:
        time_limit = level_time_limits[1]
        time_remaining = time_limit
    elif level == 2:
        add_more_cones(5); time_limit = None
    elif level == 3:
        add_more_cones(10)
        for t in treasures: t['active'] = True
        time_limit = None

def advance_level():
    global level, nitro_count
    if level < max_level:
        level += 1
        nitro_count += 1
        setup_level(level)
        start_race_countdown()

def restart_level():
    global game_over, current_checkpoint
    game_over = False
    current_checkpoint = 0
    setup_level(level)
    start_race_countdown()

def restart_game():
    global score, nitro_count, game_over, victory, current_checkpoint
    score = 0; nitro_count = 0
    game_over = False; victory = False
    current_checkpoint = 0
    setup_level(1)
    start_race_countdown()

def trigger_game_over():
    global game_over, race_started
    game_over = True; race_started = False

def victory_screen():
    global victory, race_started
    victory = True; race_started = False

def add_more_cones(n):
    for _ in range(n):
        x = random.choice([-17.0, -13.0, 13.0, 17.0])
        z = random.uniform(-20.0, 20.0)
        cones.append((x, z))

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    if camera_view == 0:
        gluLookAt(0.0, 40.0, 60.0,  0.0, 0.0, 0.0,  0.0, 1.0, 0.0)
    elif camera_view == 1:
        cam_x = car_x - 5.0 * math.sin(math.radians(car_angle))
        cam_z = car_z - 5.0 * math.cos(math.radians(car_angle))
        gluLookAt(cam_x, 3.0, cam_z, car_x, 0.0, car_z, 0.0, 1.0, 0.0)
    elif camera_view == 2:
        cam_x = car_x + 1.5 * math.sin(math.radians(car_angle))
        cam_z = car_z + 1.5 * math.cos(math.radians(car_angle))
        look_at_x = cam_x + 5.0 * math.sin(math.radians(car_angle))
        look_at_z = cam_z + 5.0 * math.cos(math.radians(car_angle))
        gluLookAt(cam_x, 0.5, cam_z, look_at_x, 0.5, look_at_z, 0.0, 1.0, 0.0)

    draw_ground(); draw_racetrack(); draw_lake(); draw_flowers()
    draw_boost_pads(); draw_health_packs(); draw_treasures()
    for x, z in cones: draw_cone(x, z)
    for x, z in trees: draw_tree(x, z)
    draw_car(car_x, car_z, 1.0, 0.0, 0.0, car_angle)
    draw_ui()
    glutSwapBuffers()

def reshape(width, height):
    global window_width, window_height
    window_width, window_height = width, height
    glViewport(0, 0, width, height if height > 0 else 1)
    glMatrixMode(GL_PROJECTION); glLoadIdentity()
    gluPerspective(45.0, float(width) / float(height if height > 0 else 1), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def keyboard(key, x, y):
    global camera_view, car_speed, car_angle
    
    if key == b'q' or key == b'\x1b': sys.exit()
    if game_over and key == b'r': restart_level(); return
    if victory and key == b'r': restart_game(); return

    if key == b'c':
        camera_view = (camera_view + 1) % 3
        if not race_started and not game_over and not victory and camera_view in [1, 2]:
            start_race_countdown()
        glutPostRedisplay()
        return

    if key == b'n': use_nitro()
    
    if race_started and not game_over and not victory and not level_complete:
        if key == b'w': car_speed += 0.1
        elif key == b's': car_speed -= 0.1
        elif key == b'a': car_angle += 5.0
        elif key == b'd': car_angle -= 5.0

def reset_car_position():
    global car_x, car_z, car_angle, car_speed
    car_x = 15.0; car_z = -5.0; car_angle = 0.0; car_speed = 0.0

def update(value):
    global car_x, car_z, car_speed, car_angle, countdown_state, race_started, nitro_active
    global level_start_time, time_remaining, health, level_complete, level_complete_time

    if level_complete:
        if glutGet(GLUT_ELAPSED_TIME) - level_complete_time > level_complete_delay:
            level_complete = False; advance_level()
        glutPostRedisplay(); glutTimerFunc(10, update, 0); return
    
    if game_over or victory:
        glutPostRedisplay(); glutTimerFunc(10, update, 0); return

    if level == 1 and time_limit is not None and race_started:
        elapsed = (glutGet(GLUT_ELAPSED_TIME) - level_start_time) / 1000.0
        time_remaining = max(0, time_limit - elapsed)
        if time_remaining <= 0: trigger_game_over()
    if level == 3 and all(not t['active'] for t in treasures) and lap_count >= level_lap_target:
        victory_screen()

    if countdown_state > 0:
        elapsed = glutGet(GLUT_ELAPSED_TIME) - countdown_start_time
        if elapsed > 3000:
            countdown_state = 0; race_started = True
            if level == 1: level_start_time = glutGet(GLUT_ELAPSED_TIME)
        elif elapsed > 2000: countdown_state = 1
        elif elapsed > 1000: countdown_state = 2

    if nitro_active and glutGet(GLUT_ELAPSED_TIME) >= nitro_end_time:
        nitro_active = False

    if race_started:
        cur_speed = car_speed * (nitro_multiplier if nitro_active else 1.0)
        potential_x = car_x + cur_speed * math.sin(math.radians(car_angle))
        potential_z = car_z + cur_speed * math.cos(math.radians(car_angle))
        
        if is_on_racetrack(potential_x, potential_z):
            if not check_cone_collision(potential_x, potential_z):
                car_x, car_z = potential_x, potential_z
        else:
            car_speed *= -0.2; health -= 2
            if health < 0: health = 0
        
        car_speed *= 0.98
        check_pickups()
        check_checkpoints_and_lap()

    if health <= 0 and not game_over: trigger_game_over()
    glutPostRedisplay(); glutTimerFunc(10, update, 0)

def generate_static_scenery():
    ground_bounds = (-50.0, 50.0); lake_center = (0.0, 0.0); lake_radius = 8.0
    outer_x_min, outer_x_max = -20.0, 20.0; outer_z_min, outer_z_max = -30.0, 30.0
    inner_x_min, inner_x_max = -10.0, 10.0; inner_z_min, inner_z_max = -22.0, 22.0
    
    tree_count = 0
    while tree_count < 200:
        x, z = random.uniform(*ground_bounds), random.uniform(*ground_bounds)
        dist_from_lake = math.sqrt((x - lake_center[0])**2 + (z - lake_center[1])**2)
        if not ((outer_x_min <= x <= outer_x_max and outer_z_min <= z <= outer_z_max) or dist_from_lake < lake_radius):
            trees.append((x,z)); tree_count += 1
            
    flower_count = 0
    while flower_count < 200:
        x, z = random.uniform(inner_x_min, inner_x_max), random.uniform(inner_z_min, inner_z_max)
        dist_from_lake = math.sqrt((x - lake_center[0])**2 + (z - lake_center[1])**2)
        if dist_from_lake >= lake_radius + 0.5:
            flowers.append((x, z, random.random(), random.random(), random.random())); flower_count += 1

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutCreateWindow(b"Racing Game")
    init_gl()
    
    generate_static_scenery()
    ensure_checkpoint_arrays()
    restart_game()

    glutTimerFunc(10, update, 0)
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutMainLoop()

if __name__ == "__main__":
    main()