# coding = utf-8
import pygame
import sys
import random

# mon import /mon ajout
from client import Client
import threading
import socket
import time
import re
import json

from enums.power_up_type import PowerUpType
from player import Player
from player2 import Player2
from explosion import Explosion
from enemy import Enemy
from enums.algorithm import Algorithm
from power_up import PowerUp

BACKGROUND_COLOR = (107, 142, 35)

font = None

player = None
enemy_list = []
ene_blocks = []
bombs = []
explosions = []
power_ups = []

GRID_BASE = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
             [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
             [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
             [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
             [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
             [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
             [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
             [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
             [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
             [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
             [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
             [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
             [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

#grid = [row[:] for row in GRID_BASE]

grid = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 2, 2, 2, 2, 2, 2, 3, 0, 1], [1, 0, 1, 2, 1, 
2, 1, 2, 1, 2, 1, 0, 1], [1, 0, 2, 2, 2, 0, 2, 2, 2, 0, 0, 0, 1], [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 0, 1], [1, 0, 2, 2, 2, 0, 2, 2, 2, 2, 2, 0, 1], [1, 2, 1, 2, 1, 0, 1, 0, 1, 0, 1, 2, 1], [1, 2, 2, 2, 2, 2, 
2, 2, 0, 2, 2, 2, 1], [1, 2, 1, 2, 1, 0, 1, 2, 1, 0, 1, 0, 1], [1, 0, 2, 2, 2, 2, 2, 0, 2, 2, 2, 0, 1], 
[1, 0, 1, 0, 1, 0, 1, 2, 1, 0, 1, 0, 1], [1, 0, 3, 2, 2, 2, 2, 0, 2, 2, 0, 0, 1], [1, 1, 1, 1, 1, 1, 1, 
1, 1, 1, 1, 1, 1]] #doit être mis en dure pour éviter d'avoir une map vide (elle doit correspondre à la genération mise en dure aussi)


def affect(my_id):  #Affectation de l'id du joueur
    if not 'player_id' in globals():
        global player_id
        player_id = json.loads(my_id)
        print("Vous êtes le joueur ",my_id)

def callback(data): #Fonction d'écoute du retour du serveur (étape X (final) du cheminement))
    print("data",data,len(data))
    if data[0] == "{":  #Vérifi si le text reçu est un objet stringifié
        try:
            test = json.loads(data)
            # print("callback 0", test)
            # print("callback 1", test["x"])
            if test['player'] == 1:
                try:
                    temp = test["y"]
                    player.move(test["x"], test["y"], grid, ene_blocks, power_ups)
                    movement = True

                    if temp != player.direction:    
                        player.frame = 0
                        player.direction = temp
                    if movement:
                        if player.frame == 2:
                            player.frame = 0
                        else:
                            player.frame += 1
                except:
                       
                    temp_bomb = player.plant_bomb(grid)
                    bombs.append(temp_bomb)
                    grid[temp_bomb.pos_x][temp_bomb.pos_y] = 3
                    player.bomb_limit -= 1

            if test['player'] == 2:
                try:
                    temp = test["y"]
                    player2.move(test["x"], test["y"], grid, ene_blocks, power_ups)
                    movement = True

                    if temp != player.direction:    
                        player2.frame = 0
                        player2.direction = temp
                    if movement:
                        if player2.frame == 2:
                            player2.frame = 0
                        else:
                            player2.frame += 1
                except:
                    temp_bomb = player2.plant_bomb(grid)
                    bombs.append(temp_bomb)
                    grid[temp_bomb.pos_x][temp_bomb.pos_y] = 3
                    player2.bomb_limit -= 1

        except Exception as error:
            print("error",error)

    else:
        affect(data[0])


# création d'une instance de classe Client en utilisant les informations (username,server,port)
client = Client("player", "192.168.1.100", 59001, callback)
# démarrage du thread d'écoute pour que le client puisse recevoir les messages du serveur
client.listen()


def send(message):
    if client:
        # envoie le message récupérer auparavant grâce à la méthode "send"
        client.send(message)


def game_init(surface, path, player_alg, player2_alg, en2_alg, en3_alg, scale):

    global font
    font = pygame.font.SysFont('Bebas', scale)
    global enemy_list
    global ene_blocks
    global player
    global player2  # Ajout de la variable player2

    enemy_list = []
    ene_blocks = []
    global explosions
    global bombs
    global power_ups
    bombs.clear()
    explosions.clear()
    power_ups.clear()

    player = Player()

    # Ajout d'un deuxième joueur
    player2 = Player2()
    player2.load_animations(scale)
    ene_blocks.append(player2)

    # if en2_alg is not Algorithm.NONE:     Partie gestio des apparitions des bots
    #     en2 = Enemy(1, 11, en2_alg)
    #     en2.load_animations('2', scale)
    #     enemy_list.append(en2)
    #     ene_blocks.append(en2)

    # if en3_alg is not Algorithm.NONE:
    #     en3 = Enemy(11, 1, en3_alg)
    #     en3.load_animations('3', scale)
    #     enemy_list.append(en3)
    #     ene_blocks.append(en3)

    if player_alg is Algorithm.PLAYER:
        player.load_animations(scale)
        ene_blocks.append(player)
    elif player_alg is not Algorithm.NONE:
        en0 = Enemy(1, 1, player_alg)
        en0.load_animations('', scale)
        enemy_list.append(en0)
        ene_blocks.append(en0)
        player.life = False
    else:
        player.life = False

    grass_img = pygame.image.load('images/terrain/grass.png')
    grass_img = pygame.transform.scale(grass_img, (scale, scale))

    block_img = pygame.image.load('images/terrain/block.png')
    block_img = pygame.transform.scale(block_img, (scale, scale))

    box_img = pygame.image.load('images/terrain/box.png')
    box_img = pygame.transform.scale(box_img, (scale, scale))

    bomb1_img = pygame.image.load('images/bomb/1.png')
    bomb1_img = pygame.transform.scale(bomb1_img, (scale, scale))

    bomb2_img = pygame.image.load('images/bomb/2.png')
    bomb2_img = pygame.transform.scale(bomb2_img, (scale, scale))

    bomb3_img = pygame.image.load('images/bomb/3.png')
    bomb3_img = pygame.transform.scale(bomb3_img, (scale, scale))

    explosion1_img = pygame.image.load('images/explosion/1.png')
    explosion1_img = pygame.transform.scale(explosion1_img, (scale, scale))

    explosion2_img = pygame.image.load('images/explosion/2.png')
    explosion2_img = pygame.transform.scale(explosion2_img, (scale, scale))

    explosion3_img = pygame.image.load('images/explosion/3.png')
    explosion3_img = pygame.transform.scale(explosion3_img, (scale, scale))

    terrain_images = [grass_img, block_img, box_img, grass_img]
    bomb_images = [bomb1_img, bomb2_img, bomb3_img]
    explosion_images = [explosion1_img, explosion2_img, explosion3_img]

    power_up_bomb_img = pygame.image.load('images/power_up/bomb.png')
    power_up_bomb_img = pygame.transform.scale(
        power_up_bomb_img, (scale, scale))

    power_up_fire_img = pygame.image.load('images/power_up/fire.png')
    power_up_fire_img = pygame.transform.scale(
        power_up_fire_img, (scale, scale))

    power_ups_images = [power_up_bomb_img, power_up_fire_img]

    main(surface, scale, path, terrain_images,
         bomb_images, explosion_images, power_ups_images)


def draw(s, grid, tile_size, show_path, game_ended, terrain_images, bomb_images, explosion_images, power_ups_images):
    s.fill(BACKGROUND_COLOR)
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            s.blit(terrain_images[grid[i][j]], (i * tile_size,
                   j * tile_size, tile_size, tile_size))

    for pu in power_ups:
        s.blit(power_ups_images[pu.type.value], (pu.pos_x *
               tile_size, pu.pos_y * tile_size, tile_size, tile_size))

    for x in bombs:
        s.blit(bomb_images[x.frame], (x.pos_x * tile_size,
               x.pos_y * tile_size, tile_size, tile_size))

    for y in explosions:
        for x in y.sectors:
            s.blit(explosion_images[y.frame], (x[0] * tile_size,
                   x[1] * tile_size, tile_size, tile_size))
    if player.life:
        s.blit(player.animation[player.direction][player.frame],
               (player.pos_x * (tile_size / 4), player.pos_y * (tile_size / 4), tile_size, tile_size))

    if player2.life:
        s.blit(player2.animation[player2.direction][player2.frame],
               (player2.pos_x * (tile_size / 4), player2.pos_y * (tile_size / 4), tile_size, tile_size))

    for en in enemy_list:
        if en.life:
            s.blit(en.animation[en.direction][en.frame],
                   (en.pos_x * (tile_size / 4), en.pos_y * (tile_size / 4), tile_size, tile_size))
            if show_path:
                if en.algorithm == Algorithm.DFS:
                    for sek in en.path:
                        pygame.draw.rect(s, (255, 0, 0, 240),
                                         [sek[0] * tile_size, sek[1] * tile_size, tile_size, tile_size], 1)
                else:
                    for sek in en.path:
                        pygame.draw.rect(s, (255, 0, 255, 240),
                                         [sek[0] * tile_size, sek[1] * tile_size, tile_size, tile_size], 1)

    if game_ended:
        tf = font.render("Press ESC to go back to menu",
                         False, (153, 153, 255))
        s.blit(tf, (10, 10))

    pygame.display.update()


def generate_map(grid):
    # for i in range(1, len(grid) - 1):
    #     for j in range(1, len(grid[i]) - 1):
    #         if grid[i][j] != 0:
    #             continue
    #         elif (i < 3 or i > len(grid) - 4) and (j < 3 or j > len(grid[i]) - 4):
    #             continue
    #         if random.randint(0, 9) < 7:
    #             grid[i][j] = 2
    grid = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],    #Map prédéfini (copie à la sortie d'un generated_map basique)
    [1, 0, 0, 2, 2, 2, 2, 2, 2, 2, 3, 0, 1],
    [1, 0, 1, 2, 1, 2, 1, 2, 1, 2, 1, 0, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1],
    [1, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 1],
    [1, 2, 1, 2, 1, 2, 1, 0, 1, 2, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 0, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 0, 1, 0, 1, 2, 1, 2, 1, 2, 1, 0, 1],
    [1, 0, 3, 2, 2, 2, 2, 2, 2, 2, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

    return


def main(s, tile_size, show_path, terrain_images, bomb_images, explosion_images, power_ups_images):
    generate_map(grid)

    clock = pygame.time.Clock()

    running = True
    game_ended = False
    while running:
        players_mouves = client.listen()

        dt = clock.tick(15)
        for en in enemy_list:
            en.make_move(grid, bombs, explosions, ene_blocks)

        if player.life:
            keys = pygame.key.get_pressed()
            global temp
            global movement
            temp = player.direction
            movement = False
            if keys[pygame.K_DOWN]:
                send(json.dumps(
                    {"player": player_id, "x": 0, "y": 1, "temp": 0 }))
                # player.move(0, 1, grid, ene_blocks, power_ups)
                movement = True
            elif keys[pygame.K_RIGHT]:
                send(json.dumps(
                    {"player": player_id, "x": 1, "y": 0, "temp": 1 }))

                movement = True
            elif keys[pygame.K_UP]:
                send(json.dumps(
                    {"player": player_id, "x": 0, "y": -1, "temp": 2 }))

                movement = True
            elif keys[pygame.K_LEFT]:
                send(json.dumps(
                    {"player": player_id, "x": -1, "y": 0, "temp": 3 }))
                movement = True
            # if temp != player.direction:
            #     player.frame = 0
            #     player.direction = temp
            # if movement:
            #     if player.frame == 2:
            #         player.frame = 0
            #     else:
            #         player.frame += 1
        if player2.life:
            keys_player2 = pygame.key.get_pressed()
            temp_player2 = player2.direction
            movement_player2 = False
            if keys_player2[pygame.K_s]:
                temp_player2 = 0
                player2.move(0, 1, grid, ene_blocks, power_ups)
                movement_player2 = True
            elif keys_player2[pygame.K_d]:
                temp_player2 = 1
                player2.move(1, 0, grid, ene_blocks, power_ups)
                movement_player2 = True
            elif keys_player2[pygame.K_z]:
                temp_player2 = 2
                player2.move(0, -1, grid, ene_blocks, power_ups)
                movement_player2 = True
            elif keys_player2[pygame.K_q]:
                temp_player2 = 3
                player2.move(-1, 0, grid, ene_blocks, power_ups)
                movement_player2 = True
            if temp_player2 != player2.direction:
                player2.frame = 0
                player2.direction = temp_player2
            if movement_player2:
                if player2.frame == 2:
                    player2.frame = 0
                else:
                    player2.frame += 1
        draw(s, grid, tile_size, show_path, game_ended, terrain_images,
             bomb_images, explosion_images, power_ups_images)
        if not game_ended:
            game_ended = check_end_game()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit(0)
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE: #Envoi des bombs
                    send(json.dumps({"player": player_id, "bomb": True }))
                    # if player.bomb_limit == 0 or not player.life:
                    #     continue
                    # temp_bomb = player.plant_bomb(grid)
                    # bombs.append(temp_bomb)
                    # grid[temp_bomb.pos_x][temp_bomb.pos_y] = 3
                    # player.bomb_limit -= 1
                elif e.key == pygame.K_ESCAPE:
                    running = False
                if e.key == pygame.K_r:
                    send(json.dumps({"player": player_id, "bomb": True }))
                    # if player2.bomb_limit == 0 or not player2.life:
                    #     continue
                    # temp_bomb = player2.plant_bomb(grid)
                    # bombs.append(temp_bomb)
                    # grid[temp_bomb.pos_x][temp_bomb.pos_y] = 3
                    # player2.bomb_limit -= 1
                elif e.key == pygame.K_ESCAPE:
                    running = False
    
        update_bombs(grid, dt) #à ne surtout sortir du while sinon les bombes n'exposent pas

    explosions.clear()
    enemy_list.clear()
    ene_blocks.clear()
    power_ups.clear()

def update_bombs(grid, dt):
    for b in bombs:
        b.update(dt)
        if b.time < 1:
            b.bomber.bomb_limit += 1
            grid[b.pos_x][b.pos_y] = 0
            exp_temp = Explosion(b.pos_x, b.pos_y, b.range)
            exp_temp.explode(grid, bombs, b, power_ups)
            exp_temp.clear_sectors(grid, random, power_ups)
            explosions.append(exp_temp)
    if player not in enemy_list:
        player.check_death(explosions)
    if player2 not in enemy_list:
        player2.check_death(explosions)
    for en in enemy_list:
        en.check_death(explosions)
    for e in explosions:
        e.update(dt)
        if e.time < 1:
            explosions.remove(e)


def check_end_game():
    if not player.life:
        return True

    for en in enemy_list:
        if en.life:
            return False

    return True
