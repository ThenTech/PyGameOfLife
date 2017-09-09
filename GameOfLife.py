import pygame
import sys, os, random
import copy

pygame.init()
pygame.font.init()
# pygame.key.set_repeat(10, 10)

from Elements import Fonts, Keymap
from Segment import Segment
from Patterns import Patterns

class GameOfLife:
    EMPTY = 0
    CELL  = 1

    def __init__(self, width=803, height=803, cell=10):
        self.cell_size   = cell
        self.cell_margin = 1
        self.size        = self.width, self.height = width, height
        self.target_fps  = 30

        pygame.display.set_caption("Game of Life")

        self.screen = pygame.display.set_mode(self.size)
        self.clock  = pygame.time.Clock()

        Segment.WIDTH, Segment.HEIGHT = self.cell_size, self.cell_size
        self.grid_width  = self.width  // (self.cell_size + self.cell_margin)
        self.grid_height = self.height // (self.cell_size + self.cell_margin)

        self.setup         = True
        self.start_drawing = False
        self.start_add     = False
        self.start_remove  = False
        self.generation    = 0

        self.all_cells   = [[]]
        self.all_sprites = pygame.sprite.Group()
        
        self.clearCells()

        # Fill all
        # for x in xrange(self.grid_width):
            # for y in xrange(self.grid_height):
                # self.createCell(x, y)
        print self.grid_width, self.grid_height


    def _draw_text(self):
        self.screen.blit(Fonts.courier12.render("{0}/{1}".format(int(self.clock.get_fps()), self.target_fps), False, (255, 0, 0)), (5, 5))
        self.screen.blit(Fonts.courier12.render("Gen: {0}".format(self.generation), True, (255, 0, 0)), (5, 20))
        
        secs = pygame.time.get_ticks() // 1000
        self.screen.blit(Fonts.courier12.render("Time: {0:02d}:{1:02d}".format(secs // 60, secs % 60), True, (255, 100, 100)), (5, 35))

        
    def _cell_from_coord(self, pos):
        r = self.cell_size + self.cell_margin
        return min((pos[0] - self.cell_margin) // r, self.grid_width - 1), \
               min((pos[1] - self.cell_margin) // r, self.grid_height - 1)

               
    def loadPattern(self, str_pattern, x=None, y=None):
        p = str_pattern.strip().split("\n")
        
        x = x or (self.grid_width  // 2 - len(p[0]) // 2)
        y = y or (self.grid_height // 2 - len(p) // 2)

        for py, row in enumerate((map(int, line) for line in p)):
            for px, col in enumerate(row):
                if col: self.createCell (px + x, py + y)
                else:   self.destroyCell(px + x, py + y)
                
    def loadPatternFile(self, fpath, x=None, y=None):
        if os.path.isfile(fpath):
            with file(fpath, 'r') as f:
                ptrn = f.read()
                self.loadPattern(ptrn, x, y)
    
    def savePattern(self):
        first_col, last_col, first_row, last_row = self.grid_width + 1, -1, -1, -1
        for y, row in enumerate(self.all_cells):
            if last_row < 0 and not all(row):
                first_row = y
            if any(row):
                last_row = y+1
                first_col = min(first_col, next(i for i,v in enumerate(row) if v))
                last_col  = max(last_col , next(i+1 for i,v in reversed(list(enumerate(row))) if v))
                

        # Any content
        if first_col < last_col and first_row < last_row:
            ptrn = "\n".join(["".join(map(lambda c: "1" if c else "0", row[first_col:last_col])) for row in self.all_cells[first_row:last_row]])
            print ptrn
            
            with file('saved.txt', 'w') as f:
                f.write(ptrn)

               
    def clearCells(self):
        self.all_cells = [[None for x in xrange(self.grid_width)] for y in xrange(self.grid_height)]
        self.all_sprites.empty()
          
          
    def createCell(self, x, y):
        if self.hasNoCell(x, y):
            cell = Segment(x * (self.cell_size + self.cell_margin) + self.cell_margin,
                           y * (self.cell_size + self.cell_margin) + self.cell_margin)
            self.all_cells[y][x] = cell
            self.all_sprites.add(cell)


    def destroyCell(self, x, y):
        if self.hasCell(x, y):
            cell = self.all_cells[y][x]
            self.all_sprites.remove(cell)
            self.all_cells[y][x] = None


    def hasCell(self, x, y, grid=None):
        grid = grid or self.all_cells
        return 0 <= x < self.grid_width and 0 <= y < self.grid_height and grid[y][x]

    def hasNoCell(self, x, y):
        return 0 <= x < self.grid_width and 0 <= y < self.grid_height and not self.all_cells[y][x]

    def countNeighbours(self, x, y, grid=None):
        grid  = grid or self.all_cells
        count = 0

        for cx in xrange(x - 1, x + 2):
            for cy in xrange(y - 1, y + 2):
                if not (cx == x and cy == y) and self.hasCell(cx, cy, grid):
                    count += 1

        return count

    def progressCells(self):
        old_cells = copy.deepcopy(self.all_cells)

        for x in xrange(self.grid_width):
            for y in xrange(self.grid_height):
                count = self.countNeighbours(x, y, old_cells)
                if count < 2 or count > 3:
                    self.destroyCell(x, y)
                elif count == 3:
                    self.createCell(x, y)
                    
        self.generation += 1


    def start(self):
        while 1:
            mposx, mposy = -1, -1

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == Keymap.UP:
                        self.target_fps += 1
                    elif event.key == Keymap.DOWN:
                        self.target_fps -= 1
                    elif event.key == Keymap.C and self.setup:
                        self.clearCells()
                    elif event.key == Keymap.S and self.setup:
                        self.savePattern()
                    elif event.key == Keymap.SPACE:
                        self.setup = not self.setup
                elif self.setup:
                    mposx, mposy = self._cell_from_coord(pygame.mouse.get_pos())

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.start_drawing = True
                        self.start_add     = self.hasNoCell(mposx, mposy)
                        self.start_remove  = self.hasCell(mposx, mposy)
                    elif event.type == pygame.MOUSEBUTTONUP:
                        self.start_drawing = False


            if self.setup:
                if self.start_drawing:
                    # colour cells on click
                    if   self.start_add:    self.createCell(mposx, mposy)
                    elif self.start_remove: self.destroyCell(mposx, mposy)
            else:
                # Main logic
                self.progressCells()


            # Start redraw
            self.screen.fill(0)

            self.all_sprites.draw(self.screen)

            # Draw buffer to screen
            self._draw_text()
            pygame.display.flip()
            self.clock.tick(200 if self.setup else self.target_fps)


if __name__ == '__main__':
    g = GameOfLife()
    # g.loadPattern(Patterns.glidergun)
    # g.loadPattern(Patterns.rpentomino)
    # g.loadPattern(Patterns.pufferup, y=g.grid_height-8)
    g.loadPatternFile('saved.txt')
    g.start()
