import character as c

window = 0
half_w = 5.0
half_h = 3.0
half_d = 2.5

hero = c.Hero()
villain = c.Villain()
rain = []
c.pygame.mixer.init()
c.pygame.init()

def init_scene(width, height):
    # specify background colour of window after clearing of colour buffers RGBA
    c.glClearColor(0.0, 0.0, 0.0, 0.0)
    c.glClearDepth(1.0)
    # pixel drawn only if incoming depth value is less than stored depth value (for overlapping faces)
    c.glDepthFunc(c.GL_LESS)
    # enable depth test specified above
    c.glEnable(c.GL_DEPTH_TEST)
    c.glPolygonMode(c.GL_FRONT, c.GL_FILL)
    c.glPolygonMode(c.GL_BACK, c.GL_FILL)
    c.glShadeModel(c.GL_SMOOTH)
    # allows visualisation of variations in z coordinate with respect to viewing point
    c.glMatrixMode(c.GL_PROJECTION)
    c.glLoadIdentity()
    # 45 degree field view, aspect ratio, display range 0.1 to 100
    c.gluPerspective(45.0, float(width) / float(height), 0.1, 100.0)
    # define in terms of world coordinates view used also
    c.glMatrixMode(c.GL_MODELVIEW)


def resize_scene(width, height):
    """ Note this function was taken directly from lab wk 8 solution provided
        by Dr Tom Cai, The University of Sydney"""

    if height == 0:
        height = 1
    # change x-y coordinates to window x-y coordinates
    c.glViewport(0, 0, width, height)
    c.glMatrixMode(c.GL_PROJECTION)
    c.glLoadIdentity()
    c.gluPerspective(45.0, float(width) / float(height), 0.1, 100.0)
    c.glMatrixMode(c.GL_MODELVIEW)
    c.window_w = width
    c.window_h = height


def key_press(*args):
    """ provides escape sequence"""

    # if ANSI escape sequence ESC is pressed (b prefix for python3 conversion)
    if args[0] == b"\x1b":
        print("\nExiting.")
        exit()


def draw_background():
    """draws a 3D midnight blue space"""

    global half_w, half_d, half_h
    # multiply translation matrix by current matrix and store result as current matrix
    # i.e push whole coordinate system forward by 5
    c.glTranslatef(0.0, 0.0, -6.0)
    # begin defining shape (specified as quadrilateral. Defined by every 4 vertex points)
    c.glBegin(c.GL_QUADS)
    # midnight blue https://www.opengl.org/discussion_boards/showthread.php/132502-Color-tables
    c.glColor3f(0.184314, 0.184314, 0.309804)
    c.glVertex3f(half_w, half_h, -half_d)
    c.glVertex3f(-half_w, half_h, -half_d)
    c.glVertex3f(-half_w, half_h, half_d)
    c.glVertex3f(half_w, half_h, half_d)

    c.glColor3f(0.184314, 0.184314, 0.309804)
    c.glVertex3f(half_w, -half_h, half_d)
    c.glVertex3f(-half_w, -half_h, half_d)
    c.glVertex3f(-half_w, -half_h, -half_d)
    c.glVertex3f(half_w, -half_h, -half_d)
    # Back drop
    c.glColor3f(0.184314, 0.184314, 0.309804)
    c.glVertex3f(half_w, -half_h, -half_d)
    c.glVertex3f(-half_w, -half_h, -half_d)
    c.glVertex3f(-half_w, half_h, -half_d)
    c.glVertex3f(half_w, half_h, -half_d)

    c.glColor3f(0.184314, 0.184314, 0.309804)
    c.glVertex3f(-half_w, half_h, half_d)
    c.glVertex3f(-half_w, half_h, -half_d)
    c.glVertex3f(-half_w, -half_h, -half_d)
    c.glVertex3f(-half_w, -half_h, half_d)

    c.glColor3f(0.184314, 0.184314, 0.309804)
    c.glVertex3f(half_w, half_h, -half_d)
    c.glVertex3f(half_w, half_h, half_d)
    c.glVertex3f(half_w, -half_h, half_d)
    c.glVertex3f(half_w, -half_h, -half_d)

    c.glEnd()


class RainDrops:
    rain_row = []

    def __init__(self, row):
        self.rain_row = row

    class Drop:

        def __init__(self, x, y):
            # randomize z position of rain drop
            self.z = c.random.uniform(-2.5, 2.5)
            self.x = x
            self.y = y

    def draw_drops(self):
        for droplet in self.rain_row:
            c.glBegin(c.GL_QUADS)
            c.glColor3f(0.658824, 0.658824, 0.658824)
            c.glVertex3f(droplet.x, droplet.y, droplet.z)
            c.glVertex3f(droplet.x, droplet.y-0.05, droplet.z)
            c.glVertex3f(droplet.x-0.005, droplet.y, droplet.z)
            c.glVertex3f(droplet.x-0.005, droplet.y-0.05, droplet.z)
            c.glEnd()

    def update_positions(self):
        """moves the rain drop's position
        :returns false if row needs to be removed (out of viewing range)"""
        y = 0
        for droplet in self.rain_row:
            droplet.x = droplet.x - 0.16
            droplet.y = droplet.y - 0.14
            y = droplet.y
        self.rain_row.append(RainDrops.Drop(half_w, y))
        if y < -half_h:
            return False


def draw_rain():
    """draws a row of rain drops along y, x and random initiated z"""
    global half_w, half_d, half_h, rain

    for row in rain:
        c.glPushMatrix()
        c.glTranslate(0.16, 0.14, 0)
        row.draw_drops()
        c.glPopMatrix()
        if row.update_positions() is False:
            rain.remove(row)
            del row

    x1 = half_w
    new_row = []
    while x1 > -half_w:
        new_row.append(RainDrops.Drop(x1, half_h))
        x1 -= 0.05
    new_rain_row = RainDrops(new_row)
    rain.append(new_rain_row)


def play_effect(effect):
    """plays sound effect
    :param type of effect to play"""

    if effect == "shot collision":
        ow_sound = c.pygame.mixer.Sound("Ow.ogg")
        ow_sound.play()


def check_for_colission():
    """compares current object (shots) position to that of hero character"""

    for shot in villain.shots:
        pos_x, pos_y = shot.get_position()
        y_upper_bound = c.Hero.y_body + 0.5*c.Hero.body_length + c.Hero.neck_length + 2*c.Hero.head_r
        y_lower_bound = c.Hero.y_body - 0.5*c.Hero.body_length - c.Hero.leg_length
        x_bound = c.Hero.x_body + c.Hero.body_bottom_r - half_w*0.5
        if pos_x < x_bound and pos_y < y_upper_bound and pos_y > y_lower_bound:
            villain.shots.remove(shot)
            del shot
            play_effect("shot collision")



def action():
    """glut function to loop through"""
    c.glClear(c.GL_COLOR_BUFFER_BIT | c.GL_DEPTH_BUFFER_BIT)
    c.glLoadIdentity()

    draw_background()
    draw_rain()
    if hero.draw_hero() == "finished":
        exit()
    # unused code for second intelligent design feature
    #if abs(hero.x_body - villain.x_body) < 2*hero.body_top_r + villain.arm_length:
    #    villain.react_to_close_proximity()
    villain.draw_villain()
    villain.update_villain()
    check_for_colission()

    c.glutSwapBuffers()
    c.glutPostRedisplay()


def draw_scene():
    global window
    c.glutInit()
    # RGBA mode, double buffered, window with depth buffer
    c.glutInitDisplayMode(c.GLUT_RGBA | c.GLUT_DOUBLE | c.GLUT_DEPTH)
    c.glutInitWindowSize(c.window_w, c.window_h)
    # set window position (where it opens)
    c.glutInitWindowPosition(0, 0)
    window = c.glutCreateWindow(b"Battle")
    c.glutDisplayFunc(action)
    c.glutIdleFunc(action)
    c.glutReshapeFunc(resize_scene)
    c.glutKeyboardFunc(key_press)
    init_scene(c.window_w, c.window_h)
    # play persistent rain sound effect and enter main processing
    c.pygame.mixer.Sound("rain.ogg").play(0)
    c.glutMainLoop()


def main():
    print()
    answer = raw_input("Do you require new motion data? y for YES")
    if answer is not None and answer == "y":
        c.m.run()
    else:
        draw_scene()


main()
