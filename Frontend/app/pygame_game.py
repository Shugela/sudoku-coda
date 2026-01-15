import pygame
import sys
from level_generator import LevelGenerator
from constants import *

class SudokuPygame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((540, 600))
        self.font = pygame.font.SysFont("Arial", 32)
        self.small_font = pygame.font.SysFont("Arial", 20)
        self.load_level(1)

    def load_level(self, level):
        data = LevelGenerator.generate(level)
        self.grid = data["puzzle"]
        self.solution = data["solution"]
        self.target = data["target"]
        self.level = level
        self.mistakes = 0
        self.guesses = 0
        self.selected = None
        self.message = f"Level {level}: Find the Target!"

    def draw(self):
        self.screen.fill(WHITE)
        # Draw Grid
        for i in range(10):
            width = 4 if i % 3 == 0 else 1
            pygame.draw.line(self.screen, BLACK, (i * 60, 0), (i * 60, 540), width)
            pygame.draw.line(self.screen, BLACK, (0, i * 60), (540, i * 60), width)

        # Draw Numbers and Target
        for r in range(9):
            for c in range(9):
                val = self.grid[r][c]
                if (r, c) == self.target:
                    pygame.draw.rect(self.screen, GOLD, (c*60+5, r*60+5, 50, 50), 3)
                if val != 0:
                    text = self.font.render(str(val), True, BLACK)
                    self.screen.blit(text, (c * 60 + 20, r * 60 + 10))

        # UI Info
        info = self.small_font.render(f"Mistakes: {self.mistakes}/{MAX_MISTAKES} | Level: {self.level}", True, RED)
        self.screen.blit(info, (10, 550))
        msg = self.small_font.render(self.message, True, BLUE)
        self.screen.blit(msg, (250, 550))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    self.selected = (pos[1] // 60, pos[0] // 60)
                
                if event.type == pygame.KEYDOWN and self.selected:
                    if event.unicode.isdigit() and event.unicode != '0':
                        val = int(event.unicode)
                        r, c = self.selected
                        
                        if self.grid[r][c] == 0:
                            self.guesses += 1
                            if self.solution[r][c] == val:
                                self.grid[r][c] = val
                                if (r, c) == self.target:
                                    self.message = "Success! Next Level..."
                                    pygame.display.flip()
                                    pygame.time.delay(2000)
                                    self.load_level(self.level + 1)
                            else:
                                self.mistakes += 1
                                if self.mistakes >= MAX_MISTAKES:
                                    self.message = "Game Over!"
                                    # Reset logic here
            self.draw()
            pygame.display.flip()