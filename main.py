import pygame, sys
from settings import *
from level import Level

class Game:
    def __init__(self):
  
        # general setup
        pygame.init()                                                           # инициализация
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))                  # установить параметры экрана
        pygame.display.set_caption('Zelda')                                     # имя экрана
        self.clock = pygame.time.Clock()                                        # присвоение таймера

        self.level = Level()                                                    # присвоение уровня
    
        #sound
        main_sound = pygame.mixer.Sound('../audio/main.ogg')
        main_sound.set_volume(0.5)
        main_sound.play(loops = -1)


    def run(self):                                                              # метод запуска игры
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        self.level.toggle_menu()
            
            self.screen.fill(WATER_COLOR)                                           # заполнить экран черным
            self.level.run()                                                    # запустить уровень
            pygame.display.update()                                             # обновить экран
            self.clock.tick(FPS)                                                # тик таймера соответсвует ФПС

if __name__ == '__main__':                                                      # точка входа в программу
    game = Game()                                                               # 
    game.run()                                                                  # запуск игры
