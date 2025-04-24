import random
import time
from random import randint
import pygame
import sys
from pygame.locals import *
from debug import debug
import math

pygame.init()
pygame.mixer.pre_init()
pygame.mixer.init()

# setup pygame/window #
mainClock = pygame.time.Clock()
prev_time = time.time()
dt = 0

pygame.display.set_caption('Some chest game idk')
screen = pygame.display.set_mode((1000, 800), 0, 32)
display = pygame.Surface((400, 400))

# font and text
font = pygame.font.Font("I-pixel-u.ttf", 8)
menu_font = pygame.font.Font("I-pixel-u.ttf", 25)
respawn_timer = 1.5
respawn_display = False
chest_timer = 1.5
finished_timer = 2

# menu
start_button_rect = pygame.Rect(80, 100, 90, 25)
game_loop = False
menu = True

# music and sound effect
menu_music = pygame.mixer.Sound("sounds/menu.mp3")
game_music = pygame.mixer.Sound("sounds/calmm.ogg")
chest_sound = pygame.mixer.Sound("sounds/chest.wav")
finished_sound = pygame.mixer.Sound("sounds/level-passed-143039.mp3")
sfx_channel = pygame.mixer.Channel(1)
finished_channel = pygame.mixer.Channel(2)

# player img and rect
right_frames = [pygame.image.load("graphics/player/player.png"), pygame.image.load("graphics/player/walk.png")]
left_frames = []
for frame in right_frames:
    left_frames.append(pygame.transform.flip(frame, True, False))

player_frames = right_frames
frame_index = 0
player_rect = player_frames[frame_index].get_rect()
animation_speed = 0.1
animation_counter = 0
moving = True

prev_y = 0
current_y = player_rect.y

# physics variables
jump_vel = 12
jump_height = 12
jump_counter = 0
grav_force = 0
player_speed = 100

right = False
left = False
gravity = True
jumping = False
falling = False
jump_allowed = False

true_scroll = [0, 0]

# chest counter
bar_rect = pygame.Rect(125 - 40, 5, 80, 10)
progress_rect = pygame.Rect(125 - 40 + 2, 5 + 2, 0, 6)


def load_map(filename):
    f = open(filename, "r")
    map_data = f.read()
    f.close()

    tiles = []
    map_data = map_data.split("\n")
    for row in map_data:
        tiles.append(list(row))

    return tiles


def collision_test(rect, tiles):
    collisions = []
    for tile in tiles:
        if rect.colliderect(tile):
            collisions.append(tile)
    return collisions


def move(rect, movement, tiles):  # movement = [5,2]
    global jump_counter
    global grav_force

    rect.x += movement[0]
    collisions = collision_test(rect, tiles)
    for tile in collisions:
        if movement[0] > 0:
            rect.right = tile.left
        if movement[0] < 0:
            rect.left = tile.right

    rect = gravity_jumping(rect)
    collisions = collision_test(rect, tiles)
    for tile in collisions:
        if movement[1] > 0:
            rect.bottom = tile.top
            jump_counter = 0
            grav_force = 0
        if movement[1] < 0:
            rect.top = tile.bottom
    return rect


def gravity_jumping(rect):
    global jump_vel
    global jump_height
    global jumping
    global gravity
    global grav_force
    global jump_counter

    if gravity:
        rect.y += grav_force
        grav_force += 0.5
    if jumping:
        jump_counter += 1
        rect.y -= jump_vel
        jump_vel -= 1
        grav_force = 0
        if jump_vel < 0:
            jumping = False
            gravity = True
            jump_vel = jump_height

    return rect


tiles = load_map("map")
tile_rects = []

# types of tiles
dirt_imgs = [pygame.image.load("graphics/terrain/dirt.png"), pygame.image.load("graphics/terrain/dirt2.png"), pygame.image.load("graphics/terrain/dirt_edge_left.png"),
             pygame.image.load("graphics/terrain/dirt_edge_right.png"), pygame.image.load("graphics/terrain/dirt_edges.png")]
dirt_randomiser = []
dirt_counter = 0

grass_imgs = [pygame.image.load("graphics/terrain/grass_corner_left.png"), pygame.image.load("graphics/terrain/grass.png"),
              pygame.image.load("graphics/terrain/grass_corner_right.png")]
grass_list = []
grass_counter = 0

flowers = []
for i in range(5):
    f = pygame.image.load(f"graphics/flowers/{i + 1}.png")
    flowers.append(f)
flower_randomiser = []
flower_counter = 0

chest = [pygame.image.load("graphics/chest/closed.png"), pygame.image.load("graphics/chest/open.png"),
         pygame.image.load("graphics/chest/shining.png")]
chest_randomiser = []
chest_status = []
chest_number = 0
chest_text = False
chest_counter = 0

initialisation_counter = 0

# loop #
while True:
    # change in time (dt)
    dt = time.time() - prev_time
    prev_time = time.time()

    # event handling #
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # clear display #
    display.fill((135, 206, 235))

    if game_loop:
        menu_music.fadeout(100)
        menu_music.stop()
        game_music.play(-1)
        game_music.set_volume(0.1)

        if initialisation_counter == 0:
            a = 0
            for i in tiles:
                b = 0
                for j in i:
                    if j == "1":
                        if tiles[a][b - 1] == "0":
                            dirt_randomiser.append(2)
                        elif tiles[a][b + 1] == "0":
                            dirt_randomiser.append(3)
                        elif tiles[a][b - 1] == "0" and tiles[a][b + 1] == "0":
                            dirt_randomiser.append(4)
                        else:
                            if randint(0, 15) == 7:
                                dirt_randomiser.append(1)
                            else:
                                dirt_randomiser.append(0)
                    if j == "2":
                        if randint(0, 3) == 2:
                            flower_randomiser.append(randint(0, 4))
                        else:
                            flower_randomiser.append(5)

                        if randint(0, 50) == 7:
                            chest_randomiser.append(1)
                            chest_number += 1
                        else:
                            chest_randomiser.append(0)

                        if tiles[a][b - 1] == "0":
                            grass_list.append(0)
                        elif tiles[a][b + 1] == "0":
                            grass_list.append(2)
                        else:
                            grass_list.append(1)

                    b += 1
                a += 1

            if chest_number == 0:
                chest_randomiser[randint(0, len(chest_randomiser) - 1)] = 1
                chest_number += 1

            chest_status = ["closed" for i in range(chest_number)]
            progress_increment = round(76 / chest_number) + 1
            initialisation_counter += 1

        prev_y = current_y
        current_y = player_rect.y

        if (current_y - prev_y) > 0:
            falling = True
        else:
            falling = False

        # jumping determination
        if falling:
            jump_allowed = False
        elif jump_counter > 0:
            jump_allowed = False
        else:
            jump_allowed = True

        keys = pygame.key.get_pressed()
        if keys[K_SPACE] and jump_allowed:
            gravity = False
            jumping = True
        # else:
        #     gravity = True
        #     jumping = False

        if keys[K_d]:
            right = True
        else:
            right = False
        if keys[K_a]:
            left = True
        else:
            left = False
        if keys[K_LSHIFT]:
            sprinting = True
            player_speed = 200
        else:
            sprinting = False
            player_speed = 100

        movement = [0, 0]
        if right:
            movement[0] += round(player_speed * dt)
            # player_speed += 1
            player_frames = right_frames
        if left:
            movement[0] -= round(player_speed * dt)
            # player_speed += 1
            player_frames = left_frames
        if jumping:
            movement[1] -= round(player_speed * dt)
        if gravity:
            movement[1] += round(player_speed * dt)
        # if not right and not left:
        #     player_speed = 75

        if (not right and left) or (right and not left):
            if not jumping:
                moving = True
            else:
                moving = False
        else:
            moving = False

        player_rect = move(player_rect, movement, tile_rects)

        offset_x = 100 - player_frames[frame_index].get_width() / 2
        offset_y = 100 - player_frames[frame_index].get_height() / 2

        # camera
        true_scroll[0] += (player_rect.x - true_scroll[0] - offset_x) / 10
        true_scroll[1] += (player_rect.y - true_scroll[1] - offset_y) / 10
        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        # drawing
        # animation
        if moving:
            animation_counter = animation_counter + animation_speed
            if animation_counter > 1:
                frame_index += 1
                if frame_index == len(player_frames):
                    frame_index = 0
                animation_counter = 0
        else:
            animation_counter = 0
            frame_index = 0

        player_rect.width = player_frames[frame_index].get_width()
        display.blit(player_frames[frame_index], (player_rect.x - scroll[0], player_rect.y - scroll[1]))

        # if player falls of the map
        if player_rect.y > 500:
            player_rect.x, player_rect.y = 0, 0
            respawn_display = True

        respawn_surf = font.render(str("Respawned!"), True, "white")
        respawn_rect = respawn_surf.get_rect(topleft=(player_rect.x - scroll[0] - 10, player_rect.y - 12 - scroll[1]))

        if respawn_display:
            respawn_timer -= dt
            display.blit(respawn_surf, respawn_rect)
            if respawn_timer < 0:
                respawn_display = False
                respawn_timer = 1.5

        # blitting map
        tile_rects = []
        chest_rects = []
        y = 0
        for row in tiles:
            x = 0
            for column in row:
                if column == "1":
                    display.blit(dirt_imgs[dirt_randomiser[dirt_counter]], (x * 16 - scroll[0], y * 16 - scroll[1]))
                    dirt_counter += 1
                if column == "2":
                    display.blit(grass_imgs[grass_list[grass_counter]], (x * 16 - scroll[0], y * 16 - scroll[1]))
                    if flower_randomiser[grass_counter] <= 4:
                        display.blit(flowers[flower_randomiser[grass_counter]],
                                     (x * 16 - scroll[0],
                                      y * 16 - (flowers[flower_randomiser[grass_counter]].get_height()) - scroll[1]))
                    else:
                        pass
                    if chest_randomiser[grass_counter] == 1:
                        if chest_status[chest_counter] == "closed":
                            display.blit(chest[0], (x * 16 - scroll[0], y * 16 - 16 - scroll[1]))
                        if chest_status[chest_counter] == "open":
                            display.blit(chest[1], (x * 16 - scroll[0], y * 16 - 16 - scroll[1]))
                        if chest_status[chest_counter] == "shining":
                            display.blit(chest[2], (x * 16 - scroll[0], y * 16 - 16 - scroll[1]))
                        chest_rects.append(pygame.Rect(x * 16 - 17, y * 16 - 5, 34, 21))
                        chest_counter += 1
                    else:
                        pass
                    grass_counter += 1
                if column != "0":
                    tile_rects.append(pygame.Rect(x * 16, y * 16, 16, 16))
                x += 1
            y += 1

        dirt_counter = 0
        grass_counter = 0
        chest_counter = 0

        for c in chest_rects:
            if player_rect.colliderect(c):
                if chest_status[chest_rects.index(c)] == "closed":
                    chest_text = True
                    chest_surf = font.render(str("Press E to open"), True, "white")
                    chest_text_rect = chest_surf.get_rect(
                        topleft=(player_rect.x - scroll[0] - 20, player_rect.y - 12 - scroll[1]))
                    if keys[K_e]:
                        chest_status[chest_rects.index(c)] = "open"
                        sfx_channel.play(chest_sound)
                        if progress_rect.width >= (76 / chest_number) * (chest_number - 1):
                            progress_rect.width += 76 - progress_rect.width
                        else:
                            progress_rect.width += progress_increment

        if chest_text:
            chest_timer -= dt
            display.blit(chest_surf, chest_text_rect)
            if chest_timer < 0:
                chest_text = False
                chest_timer = 1.5

        pygame.draw.rect(display, "#1d1727", bar_rect)
        pygame.draw.rect(display, "#ee8a45", progress_rect)

        # ending game
        if progress_rect.width == 76:
            progress_surf = menu_font.render(str("Finished!"), True, "white")
            progress_text_rect = progress_surf.get_rect(center=(125, 30))
            display.blit(progress_surf, progress_text_rect)
            finished_channel.set_volume(0.1)
            finished_channel.play(finished_sound)
            finished_timer -= dt
            if finished_timer < 0:
                game_loop = False
                menu = True
                sfx_channel.stop()
                game_music.stop()

    if menu and not game_loop:
        game_music.fadeout(100)
        game_music.stop()
        menu_music.play(-1)
        menu_music.set_volume(0.1)

        y = int(math.sin(prev_time * 8) * 8 + 70)
        menu_surf = menu_font.render(str("CHEST SEARCH"), True, "white")
        menu_rect = menu_surf.get_rect(center=(125, y))
        display.blit(menu_surf, menu_rect)

        if 680 > pygame.mouse.get_pos()[0] > 320 and 400 < pygame.mouse.get_pos()[1] < 500:
            pygame.draw.rect(display, "#447286", start_button_rect)
            if pygame.mouse.get_pressed()[0]:
                game_loop = True
                menu = False
                dirt_randomiser = []
                dirt_counter = 0
                grass_imgs = [pygame.image.load("graphics/terrain/grass_corner_left.png"), pygame.image.load("graphics/terrain/grass.png"),
                              pygame.image.load("graphics/terrain/grass_corner_right.png")]
                grass_list = []
                grass_counter = 0
                flower_randomiser = []
                flower_counter = 0
                chest_randomiser = []
                chest_status = []
                chest_number = 0
                chest_text = False
                chest_counter = 0
                initialisation_counter = 0

                player_rect.x, player_rect.y = 0, 0
                progress_rect.width = 0
                finished_timer = 2
        else:
            pygame.draw.rect(display, "#70ADC7", start_button_rect)

        button_surf = font.render(str("START"), True, "white")
        button_rect = button_surf.get_rect(center=(125, 112))
        display.blit(button_surf, button_rect)

    screen.blit(pygame.transform.scale_by(display, 4), (0, 0))

    # print(chest_rects[t])
    # update display #
    pygame.display.update()
    mainClock.tick(60)
