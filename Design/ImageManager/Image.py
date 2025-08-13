import pygame

class Image:
    def __init__(self, link, w, h, x, y, dir=0):
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.dir = dir

        self.image = pygame.image.load(link).convert_alpha()
        self.image = pygame.transform.scale(self.image, (w, h))
        if dir != 0:
            self.image = pygame.transform.rotate(self.image, dir)

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))


class ImageSprite:
    def __init__(self, link, w, h, x, y, frame_count=3, dir=0):
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.dir = dir

        self.frames = []
        for i in range(1, frame_count + 1):
            img = pygame.image.load(f"{link}{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (w, h))
            if dir != 0:
                img = pygame.transform.rotate(img, dir)
            self.frames.append(img)

        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.animation_speed = 0.15  # tốc độ animation
        self.frame_timer = 0

    def update(self):
        """Chuyển sang frame tiếp theo"""
        self.frame_timer += self.animation_speed
        if self.frame_timer >= 1:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            self.frame_timer = 0

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))
