from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import pygame
import time
import random
import getMotion as m

window_w = 1000
window_h = 800
half_w = 2.5
half_h = 2.0
half_d = 2.0
coords = m.numpy.zeros((5, m.num_of_frames, 2))
pygame.mixer.init()
pygame.init()

class Hero:

    def get_motion(self):
        """extracts motion data from saved text files"""
        file_buff = open("body.txt", "r")
        cnt = 0
        for line in file_buff:
            x_and_y = line.split()
            coords[0][cnt][0], coords[0][cnt][1] = convert_coords(x_and_y)
            cnt += 1
        file_buff.close()
        file_buff = open("left_arm.txt", "r")
        cnt = 0
        for line in file_buff:
            x_and_y = line.split()
            coords[1][cnt][0], coords[1][cnt][1] = convert_coords(x_and_y)
            cnt += 1
        file_buff.close()
        file_buff = open("right_arm.txt", "r")
        cnt = 0
        for line in file_buff:
            x_and_y = line.split()
            coords[2][cnt][0], coords[2][cnt][1] = convert_coords(x_and_y)
            cnt += 1
        file_buff.close()
        file_buff = open("left_leg.txt", "r")
        cnt = 0
        for line in file_buff:
            x_and_y = line.split()
            coords[3][cnt][0], coords[3][cnt][1] = convert_coords(x_and_y)
            cnt += 1
        file_buff.close()
        file_buff = open("right_leg.txt", "r")
        cnt = 0
        for line in file_buff:
            x_and_y = line.split()
            coords[4][cnt][0], coords[4][cnt][1] = convert_coords(x_and_y)
            cnt += 1
        file_buff.close()

    global half_w, half_h, half_d
    x_body = 0.0
    y_body = 0.0
    run_reaction = False
    call_cnt = 0
    # constant dimensions
    body_top_r = 0.27
    body_bottom_r = 0.15
    body_length = 0.4
    arm_r = 0.082
    leg_r = 0.045
    arm_length = 0.42
    leg_length = 0.65
    head_r = 0.52
    neck_length = 0.1

    def __init__(self):
        Hero.get_motion(self)

    def draw_hero(self):
        if Hero.call_cnt == m.num_of_frames:
            return "finished"

        def draw_body():
            glPushMatrix()
            # along z-axis to start (base z = 0)
            glRotatef(270.0, 1.0, 0.0, 0.0)
            glTranslatef(Hero.x_body, 0.0, Hero.y_body - 0.5*Hero.body_length)
            glColor3f(0.35, 0.8, 0.65)
            gluCylinder(gluNewQuadric(), Hero.body_bottom_r, Hero.body_top_r, Hero.body_length, 25, 25)
            glPopMatrix()

        def draw_head():
            neck_length = 0.1
            neck_r = 0.05
            head_r = 0.52
            glPushMatrix()
            glRotatef(270.0, 1.0, 0.0, 0.0)
            glTranslate(Hero.x_body, 0.0, Hero.y_body + 0.5*Hero.body_length)
            glColor3f(0.55, 0.47, 0.14)
            gluCylinder(gluNewQuadric(), neck_r, neck_r, neck_length, 25, 25)
            glPopMatrix()
            glPushMatrix()
            glTranslatef(Hero.x_body, Hero.y_body + neck_length + 0.5*Hero.body_length + neck_length, 0.0)
            glColor3f(head_r, 0.47, 0.14)
            glutSolidSphere(0.175, 25, 25)
            glPopMatrix()

        def draw_limb(limb_type, left_or_right):
            hand_r = 0.1
            end_x, end_y, limb_r, body_r = set_variables(limb_type, left_or_right)
            origin_x, origin_y = locate_limb_origin(Hero.x_body, Hero.y_body, Hero.body_length, body_r, limb_type, left_or_right)

            if limb_type == "leg":
                Hero.leg_length = pythagoras(origin_x, origin_y, end_x, end_y)
            elif limb_type == "arm":
                Hero.arm_length = pythagoras(origin_x, origin_y, end_x, end_y)

            glPushMatrix()
            glBegin(GL_QUADS)

            # top
            glColor3f(0.35, 0.8, 0.65)
            glVertex3f(origin_x + limb_r, origin_y, limb_r)
            glVertex3f(origin_x + limb_r, origin_y, -limb_r)
            glVertex3f(origin_x - limb_r, origin_y, limb_r)
            glVertex3f(origin_x - limb_r, origin_y, -limb_r)
            # bottom
            glColor3f(0.35, 0.8, 0.65)
            glVertex3f(end_x + limb_r, end_y, limb_r)
            glVertex3f(end_x + limb_r, end_y, -limb_r)
            glVertex3f(end_x - limb_r, end_y, limb_r)
            glVertex3f(end_x - limb_r, end_y, -limb_r)
            # front
            glColor3f(0.35, 0.8, 0.65)
            glVertex3f(end_x + limb_r, end_y, limb_r)
            glVertex3f(end_x - limb_r, end_y, limb_r)
            glVertex3f(origin_x + limb_r, origin_y, limb_r)
            glVertex3f(origin_x - limb_r, origin_y, limb_r)
            # back
            glColor3f(0.35, 0.8, 0.65)
            glVertex3f(end_x + limb_r, end_y, -limb_r)
            glVertex3f(end_x - limb_r, end_y, -limb_r)
            glVertex3f(origin_x + limb_r, origin_y, -limb_r)
            glVertex3f(origin_x - limb_r, origin_y, -limb_r)
            # LHS
            glColor3f(0.35, 0.8, 0.65)
            glVertex3f(end_x - limb_r, end_y, -limb_r)
            glVertex3f(end_x - limb_r, end_y, limb_r)
            glVertex3f(end_x - limb_r, origin_y, -limb_r)
            glVertex3f(end_x - limb_r, origin_y, limb_r)
            # RHS
            glColor3f(0.35, 0.8, 0.65)
            glVertex3f(end_x + limb_r, end_y, -limb_r)
            glVertex3f(end_x + limb_r, end_y, limb_r)
            glVertex3f(end_x + limb_r, origin_y, -limb_r)
            glVertex3f(end_x + limb_r, origin_y, limb_r)

            glEnd()
            glPopMatrix()
            # draw hand or foot
            glPushMatrix()
            glTranslatef(end_x, end_y, 0.0)
            glColor3f(0.55, 0.47, 0.14)
            glutSolidSphere(hand_r, 25, 25)
            glPopMatrix()

        def set_variables(limb_type, left_or_right):
            """sets variables to automate limb drawing
            :param leg or arm
            :param left or right"""
            if limb_type == "arm":
                limb_r = Hero.arm_r
                body_r = Hero.body_top_r
                if left_or_right == "left":
                    end_x = x_L_hand
                    end_y = y_L_hand
                elif left_or_right == "right":
                    end_x = x_R_hand
                    end_y = y_R_hand
                else:
                    print("invalid limb position")
            elif limb_type == "leg":
                limb_r = Hero.leg_r
                body_r = Hero.body_bottom_r
                if left_or_right == "left":
                    end_x = x_L_leg
                    end_y = y_L_leg
                elif left_or_right == "right":
                    end_x = x_R_leg
                    end_y = y_R_leg
                else:
                    print("invalid limb position")
            else:
                print("invalid body type")
            return end_x, end_y, limb_r, body_r

        Hero.x_body, Hero.y_body = coords[0][Hero.call_cnt][:]
        x_L_hand, y_L_hand = coords[1][Hero.call_cnt][:]
        x_R_hand, y_R_hand = coords[2][Hero.call_cnt][:]
        x_L_leg, y_L_leg = coords[3][Hero.call_cnt][:]
        x_R_leg, y_R_leg = coords[4][Hero.call_cnt][:]

        glPushMatrix()
        glTranslatef(-half_w, 0.0, 0.0)
        draw_body()
        draw_head()
        draw_limb("arm", "left")
        draw_limb("arm", "right")
        draw_limb("leg", "left")
        draw_limb("leg", "right")
        glPopMatrix()

        Hero.call_cnt += 1


class Villain:

    class Shot:
        x = 0.0
        y = 0.0
        # constant shot velocities
        Vx = 0.033
        Vy = 0.022

        def __init__(self):
            self.x = Villain.x_L_hand
            # randomize y direction
            direction = random.uniform(-0.001, 0.001)
            self.y = Villain.y_L_hand + direction
            shot_sound = pygame.mixer.Sound("laser.ogg")
            shot_sound.play()

        def draw_shot(self):
            glPushMatrix()
            glBegin(GL_TRIANGLES)
            glColor3f(.9, 0.4, 0.0)
            glVertex3f(self.x - 0.25, self.y, 0.0)
            glVertex3f(self.x, self.y + 0.10, 0.0)
            glVertex3f(self.x, self.y - 0.10, 0.0)
            glEnd()
            glPopMatrix()

        def get_position(self):
            return self.x, self.y


    global half_w, half_h, half_d
    shots = []
    x_body = 2.0
    y_body = 0.0
    z_body = 0.0
    x_direction = "left"
    y_direction = "up"
    z_direction = "away"
    scene_position = "right"
    right_scene_pos = half_w - 2.0
    left_scene_pos = -half_w + 2.0
    x_L_hand = 0.0
    y_L_hand = 0.0
    time_start = 0.0
    time_shots = 0.0
    # unused for second feature
    run_reaction = False
    # constant dimensions
    body_top_r = 0.27
    body_bottom_r = 0.15
    body_length = 0.4
    arm_r = 0.082
    leg_r = 0.045
    arm_length = 0.42
    leg_length = 0.65
    head_r = 0.52
    neck_length = 0.1


    def __init__(self):
        Villain.time_start = time.time()

    def draw_villain(self):

        def shoot():
            for a_shot in Villain.shots:
                a_shot.x -= Villain.Shot.Vx
                a_shot.y += Villain.Shot.Vy
                if a_shot.x < -half_w:
                    Villain.shots.remove(a_shot)
                    del a_shot
                else:
                    a_shot.draw_shot()

            time_now = time.time()
            time_between_shots = time_now - Villain.time_shots
            # shoot every 2.5 seconds
            if time_between_shots > 2.5:
                Villain.shots.append(Villain.Shot())
                Villain.time_shots = time_now


        def draw_body():
            glPushMatrix()
            # along z-axis to start (base z = 0)
            glRotatef(270.0, 1.0, 0.0, 0.0)
            glTranslatef(Villain.x_body, Villain.z_body, Villain.y_body - Villain.body_length*0.5)
            glColor3f(0.35, 0.45, 0.65)
            gluCylinder(gluNewQuadric(), Villain.body_bottom_r, Villain.body_top_r, Villain.body_length, 25, 25)
            glPopMatrix()

        def draw_head():
            neck_length = 0.1
            neck_r = 0.05
            head_r = 0.52
            glPushMatrix()
            glRotatef(270.0, 1.0, 0.0, 0.0)
            glTranslate(Villain.x_body, Villain.z_body, Villain.y_body + 0.5*Villain.body_length)
            glColor3f(0.55, 0.47, 0.14)
            gluCylinder(gluNewQuadric(), neck_r, neck_r, neck_length, 25, 25)
            glPopMatrix()
            glPushMatrix()
            glTranslatef(Villain.x_body, Villain.y_body + neck_length + 0.5*Villain.body_length + neck_length, Villain.z_body)
            glColor3f(head_r, 0.47, 0.14)
            glutSolidSphere(0.175, 25, 25)
            glPopMatrix()

        def draw_limb(limb_type, left_or_right):
            hand_r = 0.1
            end_x, end_y, limb_r, body_r = set_variables(limb_type, left_or_right)
            origin_x, origin_y = locate_limb_origin(Villain.x_body, Villain.y_body, Villain.body_length, body_r, limb_type, left_or_right)
            # draw hand or foot
            glPushMatrix()
            glTranslatef(end_x, end_y - hand_r, Villain.z_body)
            glColor3f(0.55, 0.47, 0.14)
            glutSolidSphere(hand_r, 25, 25)
            glPopMatrix()

            # draw limb
            glPushMatrix()
            if limb_type == "arm":
                if left_or_right == "left":
                    glRotate(90, 0.0, 1.0, 0.0)
                    glTranslatef(Villain.z_body, origin_y - Villain.arm_r, origin_x - Villain.arm_length)
                elif left_or_right == "right":
                    glRotate(270, 1.0, 0.0, 0.0)
                    glTranslatef(origin_x, Villain.z_body, origin_y - Villain.arm_length)
                glColor3f(0.35, 0.45, 0.65)
                gluCylinder(gluNewQuadric(), limb_r, limb_r, Villain.arm_length, 25, 25)

            elif limb_type == "leg":
                glRotatef(270, 1.0, 0.0, 0.0)
                glTranslatef(origin_x, Villain.z_body, origin_y - Villain.leg_length)
                glColor3f(0.35, 0.45, 0.65)
                gluCylinder(gluNewQuadric(), limb_r, limb_r, Villain.leg_length, 25, 25)
            glPopMatrix()

        def set_variables(limb_type, left_or_right):
            """ sets variables for limb drawing automation
            :param leg or arm
            :param right or left"""
            if limb_type == "arm":
                limb_r = Villain.arm_r
                body_r = Villain.body_top_r
                if left_or_right == "left":
                    end_x = Villain.x_L_hand
                    end_y = Villain.y_L_hand
                elif left_or_right == "right":
                    end_x = x_R_hand
                    end_y = y_R_hand
                else:
                    print("invalid limb position")
            elif limb_type == "leg":
                limb_r = Villain.leg_r
                body_r = Villain.body_bottom_r
                if left_or_right == "left":
                    end_x = x_L_foot
                    end_y = y_L_foot
                elif left_or_right == "right":
                    end_x = x_R_foot
                    end_y = y_R_foot
                else:
                    print("invalid limb position")
            else:
                print("invalid body type")
            return end_x, end_y, limb_r, body_r

        Villain.x_L_hand = Villain.x_body - Villain.body_top_r - Villain.arm_length
        Villain.y_L_hand = Villain.y_body + Villain.body_length * 0.5
        x_R_hand = Villain.x_body + Villain.body_top_r + 0.5 * Villain.arm_r
        y_R_hand = Villain.y_body + Villain.body_length * 0.5 - Villain.arm_length
        x_L_foot = Villain.x_body - Villain.body_bottom_r
        y_L_foot = Villain.y_body - Villain.body_length * 0.5 - Villain.leg_length
        x_R_foot = Villain.x_body + Villain.body_bottom_r
        y_R_foot = Villain.y_body - Villain.body_length * 0.5 - Villain.leg_length

        draw_body()
        draw_head()
        draw_limb("arm", "left")
        draw_limb("arm", "right")
        draw_limb("leg", "left")
        draw_limb("leg", "right")
        shoot()

    def update_villain(self):
        """moves villain position"""
        time_curr = time.time()
        time_elapse = time_curr - Villain.time_start
        Villain.time_start = time_curr

        if Villain.y_direction == "up":
            if Villain.y_body + 0.5*Villain.body_length + Villain.neck_length + Villain.head_r <= half_h:
                Villain.y_body += 0.5*time_elapse
            else:
                Villain.y_direction = "down"

        elif Villain.y_direction == "down":
            if Villain.y_body + 0.5*Villain.body_length + Villain.leg_length >= -half_h:
                Villain.y_body -= 0.5*time_elapse
            else:
                Villain.y_direction = "up"

        # unused code for second intelligent feature
        if Villain.run_reaction:
            if Villain.scene_position == "right":
                Villain.x_body -= 1.0*time_elapse
                if Villain.x_body >= Villain.left_scene_pos:
                    Villain.scene_position = "left"
                    Villain.run_reaction = False
                    Villain.z_body = 0.0

            elif Villain.scene_position == "left":
                Villain.x_body += 1.0*time_elapse
                if Villain.x_body <= Villain.right_scene_pos:
                    Villain.scene_position = "right"
                    Villain.run_reaction = False
                    Villain.z_body = 0.0

    #### unused code for second intelligent feature
    def react_to_close_proximity(self):
        if Villain.scene_position == "right":
            Villain.z_body = -1.5
        elif Villain.scene_position == "left":
            Villain.z_body = 1.5
        Villain.run_reaction = True


#### utility functions #####

def pythagoras(x1, y1, x2, y2):
    return m.math.sqrt(((x2 - x1) ** 2 + (y2 - y1) ** 2))


def tan(x1, y1, x2, y2):
    angle = m.math.atan2(y2 - y1, x2 - x1)
    return m.math.degrees(angle)


def coords_at_angle_and_length(angle, hypotenuse):
    radians = m.math.radians(angle)
    x = hypotenuse * m.math.cos(radians)
    y = hypotenuse * m.math.sin(radians)
    return x, y


def convert_coords(x_and_y):
    """ converts coords from image processing to model view in pyopengl
    :param x and y coordinates
    """
    x_scale = 2*half_w / (m.frame_width + m.pad_width * 2)
    y_scale = 2*half_h / (m.frame_height + m.pad_height * 2)
    # scaled then moved to + - system
    x_converted = int(x_and_y[0]) * x_scale
    y_converted = half_h - int(x_and_y[1]) * y_scale
    return x_converted, y_converted


def locate_limb_origin(body_x, body_y, body_length, body_radius, limb_type, left_or_right):
    """ finds the origin location of a limb on body
    :param x location of body center
    :param y location of body center
    :param length of body
    :param radius of body ( will differ if limb type is leg or arm
    :param leg or arm
    :param left or right limb"""
    if limb_type == "arm":
        origin_y = body_y + body_length/2
    elif limb_type == "leg":
        origin_y = body_y - body_length/2
    else:
        print("not a valid body type")

    if left_or_right == "left":
        origin_x = body_x - body_radius
    elif left_or_right == "right":
        origin_x = body_x + body_radius
    else:
        print("not a valid limb position")
    return origin_x, origin_y


def locate_center_coords(x1, y1, x2, y2):
    center_x = (x1 + x2)/2
    center_y = (y1 + y2)/2
    return center_x, center_y

