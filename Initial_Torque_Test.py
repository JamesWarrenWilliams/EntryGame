import pygame
from pygame.locals import *

pygame.init()
pygame.font.init()
clock = pygame.time.Clock()
screenwidth, screenheight = 600, 600
screen=pygame.display.set_mode((screenwidth,screenheight))
myfont = pygame.font.SysFont("monospace",16)

capsule_bank_pos_x = 150
capsule_bank_pos_y = 150
# angle_step = 5.
torque_mag = 1
I = 1

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




image = pygame.image.load("Capsule_back.png")
w,h = image.get_size()
keys = [False, False, False, False]

framerate = 60 # FPS
dt = 1.0/framerate

angle_rad = 0
omega = 0
deadband = 0.05
done = False
while not done:
    clock.tick(framerate)


    pos = (capsule_bank_pos_x,capsule_bank_pos_y)
    screen.fill((255,255,255))

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

    omega = omega + torque/I*dt
    angle_rad = angle_rad + omega*dt
    angle_rad = angle_rad % (2.0*3.1415)

    angle = angle_rad*57.2957795

    omega_deg = omega*57.2957795

    angletext = myfont.render(f"Angle: {angle:0.2f} deg",1,(0,0,0))
    screen.blit(angletext,(5,10))
    omegatext = myfont.render(f"Omega: {omega:0.2f} rad/s",1,(0,0,0))
    # omegatext = myfont.render(f"Omega: {omega:0.2f} rad/s ({omega_deg:0.2f} deg/s)",1,(0,0,0))
    screen.blit(omegatext,(5,26))

    blitRotate(screen,image,pos,(w/2,h/2),angle)
    pygame.draw.line(screen, 0, [screenwidth/2,0],[screenwidth/2,screenheight/2],3)


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

    # if keys[0]: # Down
    #     if capsule_bank_pos_y > 0:
    #         capsule_bank_pos_y -= 1
    # elif keys[2]: # Up
    #     if capsule_bank_pos_y < height-64:
    #         capsule_bank_pos_y += 1
    # elif keys[1]: # Left
    #     if capsule_bank_pos_x > 0:
    #         capsule_bank_pos_x -= 1

    # elif keys[3]: # Right
    #     if capsule_bank_pos_x <width-64:
    #         capsule_bank_pos_x += 1


 