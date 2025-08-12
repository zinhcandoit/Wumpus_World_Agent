import pygame

class Image:
    def __init__(self, link, w, h, x, y, dir=0):  # dir mặc định = 0 độ
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.dir = dir

        self.image = pygame.image.load(link)
        self.image = pygame.transform.scale(self.image, (w, h))
        if dir != 0:
            self.image = pygame.transform.rotate(self.image, dir)

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

