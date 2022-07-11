import pygame
from enemy import Enemy
from particles import AnimationPlayer
from settings import *
from tile import Tile
from player import Player
from debug import debug
from support import *
from random import choice, randint
from weapon import Weapon
from ui import UI
from enemy import Enemy
from particles import AnimationPlayer
from magic import MagicPlayer
from upgrade import Upgrade

class Level:
    def __init__(self):

        #get the display surface
        self.display_surface = pygame.display.get_surface()
        self.game_paused = False
        
        #sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.attackable_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()

        #sprite setup
        self.create_map()

        #attack sprites
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        

        #user interface
        self.ui = UI()
        self.upgrade = Upgrade(self.player)
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        #particles
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)

    def create_map(self):                                                                               # метод инициализации карты
        layouts = {
            'boundary': import_csv_layout('../map/map_FloorBlocks.csv'),
            'grass': import_csv_layout('../map/map_Grass.csv'),
            'object': import_csv_layout('../map/map_Objects.csv'),
            'entities': import_csv_layout('../map/map_Entities.csv')
        }
        graphics = {
            'grass': import_folder('../graphics/Grass'),
            'objects': import_folder('../graphics/objects')
        }
        
        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index*TILESIZE                                                                  # для колонки
                        y = row_index*TILESIZE                                                                  # для строки
                        #create a boundary tile
                        if style == 'boundary':
                            Tile((x,y), [self.obstacle_sprites], 'invisible')
                        #create a grass tile
                        if style == 'grass':
                            random_grass_image = choice(graphics['grass'])
                            Tile((x,y), [self.visible_sprites, self.obstacle_sprites, self.attackable_sprites], 'grass', random_grass_image)
                            
                        #create an objects tile
                        if style == 'object':
                            surf = graphics['objects'][int(col)]
                            Tile((x,y), [self.visible_sprites, self.obstacle_sprites], 'object', surf)

                        #create entities
                        if style == 'entities':
                            if col == '394':
                                self.player = Player(
                                    (x,y), 
                                    [self.visible_sprites], 
                                    self.obstacle_sprites, 
                                    self.create_attack, 
                                    self.destroy_attack,
                                    self.create_magic)
                            else:
                                if col == '390': monster_name = 'bamboo'
                                elif col == '391': monster_name = 'spirit'
                                elif col == '392': monster_name = 'raccoon'
                                elif col == '393': monster_name = 'squid'
                                Enemy(
                                    monster_name, 
                                    (x,y), 
                                    [self.visible_sprites, self.attackable_sprites], 
                                    self.obstacle_sprites,
                                    self.damage_player,
                                    self.trigger_death_particles,
                                    self.add_exp)
                    
    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visible_sprites, self.attack_sprites])

    def destroy_attack(self):                                                                           # уничтожение спрайта от атаки
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def create_magic(self, style, strength, cost):
        if style == 'heal':
            self.magic_player.heal(self.player, strength, cost, [self.visible_sprites])

        if style == 'flame':
            self.magic_player.flame(self.player, cost, [self.visible_sprites, self.attack_sprites])

    def player_attack_logic(self):
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack_sprite,self.attackable_sprites, False)
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if target_sprite.sprite_type == 'grass':
                            pos = target_sprite.rect.center
                            offset = pygame.math.Vector2(0,75)
                            for leaf in range(randint(3,6)):
                                self.animation_player.create_grass_particles(pos - offset, [self.visible_sprites])
                            target_sprite.kill()
                        else:
                            target_sprite.get_damage(self.player, attack_sprite.sprite_type)

    def damage_player(self, amount, attack_type):
        if self.player.vulnerable:
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            self.animation_player.create_particles(attack_type, self.player.rect.center, [self.visible_sprites])


    def trigger_death_particles(self, pos, particle_type):
        self.animation_player.create_particles(particle_type, pos, self.visible_sprites)
    
    def add_exp(self, amount):
        self.player.exp += amount
    
    def toggle_menu(self):
        self.game_paused = not self.game_paused

    def game_over_table(self):
        got_surf = self.font.render(('ПОТРАЧЕНО'),False,TEXT_COLOR)
        got_rect = got_surf.get_rect(center = (650, 350))

        pygame.draw.rect(self.display_surface, UI_BG_COLOR, got_rect.inflate(20,20))
        self.display_surface.blit(got_surf, got_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, got_rect.inflate(20,20), 3)

    def run(self):
        self.visible_sprites.custom_drow(self.player)                                                   # отрисовка спрайтов по игроку
        self.ui.display(self.player)

        if self.game_paused:
            self.upgrade.display()
        else:
            self.visible_sprites.update()                                                                   # обновление
            self.visible_sprites.enemy_update(self.player)
            self.player_attack_logic()
        
        if self.player.health <= 0:
            self.player.kill()
            self.game_over_table()
        #debug(self.player.direction)
        #debug(self.player.status)

class YSortCameraGroup(pygame.sprite.Group):                                                            # класс камеры
    def __init__(self):

        #general setup
        super().__init__()                                                                              # 
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2                                       # передача половины размера строки
        self.half_hight = self.display_surface.get_size()[1] // 2                                       # передача половины размера столбца
        self.offset = pygame.math.Vector2()                                                             # переменная оффсет становится вектором

        #creating the floor
        self.floor_surf = pygame.image.load('../graphics/tilemap/ground.png').convert()
        self.floor_rect = self.floor_surf.get_rect(topleft = (0,0))
    
    def custom_drow(self, player):
        
        #getting the offset
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_hight

        # drowing the floor
        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf, floor_offset_pos)

        #for sprite in self.sprites():
        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):                 # условия сортировки ставят тайл игрока выше тайла препятствия
            offset_pos = sprite.rect.topleft - self.offset                                              # положение камеры 
            self.display_surface.blit(sprite.image, offset_pos)                                         #
            
    def enemy_update(self,player):
        enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite,'sprite_type') and sprite.sprite_type == 'enemy']
        for enemy in enemy_sprites:
            enemy.enemy_update(player)