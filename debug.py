import pygame
pygame.init()
font = pygame.font.Font(None, 30)                                   # размер текста 30

def debug(info, y=10, x=10):                                        # метод отладки 
    display_surface = pygame.display.get_surface()                  # запрос окна
    debug_surf = font.render(str(info), True, 'White')              # текстовое окно с белым текстом
    debug_rect = debug_surf.get_rect(topleft = (x,y))               # расположеник текста на экране
    pygame.draw.rect(display_surface, 'Black', debug_rect)          # черный фон окна
    display_surface.blit(debug_surf, debug_rect)                    #