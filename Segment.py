
import pygame

class Segment(pygame.sprite.Sprite):

    WIDTH, HEIGHT = 10, 10
    COLOUR        = (255, 255, 255)
    
    # Constructor function
    def __init__(self, x, y):
        # Call the parent's constructor
        pygame.sprite.Sprite.__init__(self)

        # Set height, width
        self.image = pygame.Surface((Segment.WIDTH, Segment.HEIGHT))
        self.image.fill(Segment.COLOUR)
 
        # Make our top-left corner the passed-in location.
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
