# Importing modules
import pygame
from pygame.locals import *
import math

# Initializing Pygame components
pygame.init()
pygame.font.init()
clock = pygame.time.Clock()
screenwidth, screenheight = 600,600
screen=pygame.display.set_mode((screenwidth,screenheight))
myfont = pygame.font.SysFont("monospace",16)

# Game FPS -- should work out to "real-time"
framerate = 60
dt = 1/framerate

# Input conditions
currtime = 0 # Current Time Elapsed, sec
dnrng0 = 0 # Initial Downrange, m
targ_dnrng = 1000e3 # Target Downrange, m
alt0 = 135e3 # Initial Altitude, m
altf = 0 # Target/Cutoff Altitude, m
velx0 = 6e3 # Horizontal Velocity, m/s
vely0 = -1e3 # Vertical Velocity, m/s (Postive Up)
torque_mag = 1 # Magnitude of banking torque applied
I = 1 # Moment of inertia around banking axis
CD = 1 # Drag coefficient
CL = 0.24 # Lift coefficient
Sref = 15.9 # Drag Reference Area,  m^2
vehmass = 3300 # Vehicle Mass, kg
angle0 = 90 # Initial Bank Angle, deg

angle_rad = angle0*3.1415/180.0
omega = 0
deadband = 0.05


keys = [False, False, False, False]

vehicle_pos = pygame.Vector2(dnrng0,alt0)
vehicle_vel = pygame.Vector2(velx0,vely0)

capsule_side = pygame.image.load("Capsule_side.png")
capsule_side = pygame.transform.scale(capsule_side,(50,50))
capsule_side_w, capsule_side_h = capsule_side.get_size()

capsule_back = pygame.image.load("Capsule_back.png")
capsule_back_pixel_size = 100
capsule_back = pygame.transform.scale(capsule_back,(capsule_back_pixel_size,capsule_back_pixel_size))
capsule_back_w, capsule_back_h = capsule_back.get_size()
capsule_back_pos = 500,50


# Functions
def blitRotate(surf,image,pos,originPos,angle):

    #offset from pivot to center
    image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center

    # rotated offset from pivot to center
    rotated_offset = offset_center_to_pivot.rotate(-angle)

    # rotated image center
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    # get a rotated image
    rotated_image = pygame.transform.rotate(image,angle)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)

    # rotated and blit the image
    surf.blit(rotated_image, rotated_image_rect)

    # draw rectangle around the image
    ## Omitted

def position_mapping(vehpos,screenwidth,screenheight):
    dnrng_max = targ_dnrng*1.1
    
    screen_y_min = screenheight*0.2
    screen_y_max = screenheight*0.9
    screen_x_min = screenwidth*0.1
    screen_x_max = screenwidth*0.8

    dnrng = vehpos[0]
    alt = vehpos[1]

    alt_screenpos = screen_y_min + (alt - alt0)*(screen_x_max-screen_y_min)/(0-alt0)

    dnrng_screenpos = screen_x_min + (dnrng - dnrng0)*(screen_x_max-screen_x_min)/(targ_dnrng*1.1-dnrng0)

    return dnrng_screenpos, alt_screenpos

def aero_accel(vehpos,vehvel,angle):
    rho = exponentialatmosphere(vehpos)

    try:
        drag_accel_unit = -1.0*pygame.math.Vector2.normalize(vehvel)
    except:
        drag_accel_unit = pygame.math.Vector2(0,0)

    lift_accel_temp = drag_accel_unit.rotate(-90)
    try:
        lift_accel_unit = pygame.math.Vector2.normalize(lift_accel_temp)
    except:
        lift_accel_unit = pygame.math.Vector2(0,0)

    dynpress = 0.5 * rho * pygame.math.Vector2.magnitude(vehvel)**2

    drag_force = dynpress * CD * Sref

    lift_force = dynpress * CL * Sref * math.cos(angle)

    drag_accel = drag_force/vehmass * drag_accel_unit
    lift_accel = lift_force/vehmass * lift_accel_unit

    aero_accel = drag_accel + lift_accel

    return aero_accel

def exponentialatmosphere(vehpos):
    rhoref = 1.2 # kg/m^3,  Earth
    H = 8.5e3 # m, Earth
    
    rho = rhoref * math.exp(-vehpos[1]/H)
    return rho

def gravity_accel(vehpos):

    gravity_accel = pygame.Vector2(0,-9.8)
    return gravity_accel

done = False
while not done:
    clock.tick(framerate)
    currtime += dt
    screen.fill((255,255,255))

    # Input handling
    if   keys[1]:
        # Rotate left
        # blitRotate(screen, image, pos, (w/2,h/2), angle)
        # angle += angle_step
        torque = torque_mag
    elif keys[3]:
        # Rotate right
        torque = -torque_mag
    elif keys[2]:
        if omega > deadband:
            torque = -torque_mag
        elif omega < -deadband:
            torque = torque_mag
        else:
            torque = 0
    else:
        torque = 0.0


    ## BOUNDING BOXES
    pygame.draw.rect(screen,0,pygame.Rect(screenwidth*0.1,screenheight*0.2,screenwidth*0.8,screenheight*0.7),1)
    pygame.draw.rect(screen,(0,255,0),pygame.Rect(screenwidth*0.1,screenheight*0.8,screenwidth*0.8,screenheight*0.1))

    ## Target site
    pygame.draw.circle(screen,0,position_mapping((targ_dnrng,altf),screenwidth,screenheight),10)

    ## EOM UPDATES
    vehicle_vel = vehicle_vel + (aero_accel(vehicle_pos,vehicle_vel,angle_rad) + gravity_accel(vehicle_pos))*dt
    vehicle_pos = vehicle_pos + vehicle_vel*dt

    omega = omega + torque/I*dt
    angle_rad = angle_rad + omega*dt
    angle_rad = angle_rad % (2.0*3.1415)

    angle = angle_rad*57.2957795
    omega_deg = omega*57.2957795

    if vehicle_pos[1] <= altf:
        vehicle_pos[1] = altf
        vehicle_vel.xy = 0,0

    ## STATE Helper Variables
    try:
        gamma = math.copysign(57.29*math.acos(vehicle_vel[0]/pygame.math.Vector2.magnitude(vehicle_vel)),vehicle_vel[1])
    except:
        gamma = -90.0

    
    aoa = 0
    vehicle_angle = gamma + aoa

    ## IMAGE UPDATES

    vehicle_dnrng_screenpos, vehicle_alt_screenpos = position_mapping(vehicle_pos,screenwidth,screenheight)
    blitRotate(screen,capsule_side,(vehicle_dnrng_screenpos, vehicle_alt_screenpos),(capsule_side_w/2,capsule_side_h/2),vehicle_angle)

    blitRotate(screen,capsule_back,capsule_back_pos,(capsule_back_w/2,capsule_back_h/2),angle)

    ## TEXT UPDATES
    Downrangetext = myfont.render(f"Downrange: {1e-3*vehicle_pos[0]:0.2f}, km",1,(0,0,0))
    screen.blit(Downrangetext,(5,10))
    Altitudetext = myfont.render(f"Altitude: {1e-3*vehicle_pos[1]:0.2f}, km",1,(0,0,0))
    screen.blit(Altitudetext,(5,26))
    horveltext = myfont.render(f"Horiz. Velocity: {1e-3*vehicle_vel[0]:0.2f} km/s",1,(0,0,0))
    screen.blit(horveltext,(5,42))
    vertveltext = myfont.render(f"Vert. Velocity: {1e-3*vehicle_vel[1]:0.2f} km/s",1,(0,0,0))
    screen.blit(vertveltext,(5,58))
    gammatext = myfont.render(f"FPA : {gamma:0.2f} deg",1,(0,0,0))
    screen.blit(gammatext,(5,72))
    timetext = myfont.render(f"Time Elapsed : {currtime:0.0f} sec",1,(0,0,0))
    screen.blit(timetext,(5,88))
    angletext = myfont.render(f"Angle: {angle:0.2f} deg",1,(0,0,0))
    screen.blit(angletext,(300,10))
    omegatext = myfont.render(f"Omega: {omega:0.2f} rad/s",1,(0,0,0))
    # omegatext = myfont.render(f"Omega: {omega:0.2f} rad/s ({omega_deg:0.2f} deg/s)",1,(0,0,0))
    screen.blit(omegatext,(300,26))
    # Altitude and Downrange Units
    Downrange_Start_text = myfont.render(f"{1e-3*dnrng0:0.0f}",1,(0,0,0))
    screen.blit(Downrange_Start_text,(screenwidth*0.1,screenheight*0.9))
    Downrange_End_text = myfont.render(f"{1e-3*targ_dnrng*1.1:0.0f}",1,(0,0,0))
    screen.blit(Downrange_End_text,(screenwidth*0.9,screenheight*0.9))
    Downrange_Label_text = myfont.render("Downrange, km",1,(0,0,0))
    downrange_label_rect = Downrange_Label_text.get_rect(center=(screenwidth/2,screenheight*0.95))
    screen.blit(Downrange_Label_text,downrange_label_rect)

    Altitude_Start_text = myfont.render(f"{1e-3*alt0:0.0f}",1,(0,0,0))
    screen.blit(Altitude_Start_text,(screenwidth*0.05,screenheight*0.2))
    Altitude_End_text = myfont.render(f"{1e-3*altf:0.0f}",1,(0,0,0))
    screen.blit(Altitude_End_text,(screenwidth*0.05,screenheight*0.8))
    Altitude_Label_text = myfont.render("Altitude, km",1,(0,0,0))
    Altitude_label_rect = Altitude_Label_text.get_rect(center=(screenwidth*0.1,screenheight*0.5))
    altitude_label_wide,altitude_label_high = Altitude_Label_text.get_size()
    blitRotate(screen,Altitude_Label_text,(screenwidth*0.05,screenheight*0.5),(altitude_label_wide/2,altitude_label_high/2),90)

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key==K_UP:
                keys[0]=True
            elif event.key==K_LEFT:
                keys[1]=True
            elif event.key==K_DOWN:
                keys[2]=True
            elif event.key==K_RIGHT:
                keys[3]=True

        if event.type == pygame.KEYUP:
            if event.key==pygame.K_UP:
                keys[0]=False
            elif event.key==pygame.K_LEFT:
                keys[1]=False
            elif event.key==pygame.K_DOWN:
                keys[2]=False
            elif event.key==pygame.K_RIGHT:
                keys[3]=False