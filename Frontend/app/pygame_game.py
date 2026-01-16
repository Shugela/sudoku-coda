import pygame
import sys
import time
from level_generator import LevelGenerator
from constants import *

class SudokuPygame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((540, 650)) # Extra height for UI
        pygame.display.set_caption("Sudoku Target: Pro Edition")
        self.font = pygame.font.SysFont("Arial", 32)
        self.small_font = pygame.font.SysFont("Arial", 20)
        self.pencil_font = pygame.font.SysFont("Arial", 14)
        
        # Game State
        self.pencil_mode = False
        self.pencil_marks = [[[set() for _ in range(9)] for _ in range(9)] for _ in range(1)] # Using sets for 1-9
        self.streak = 0
        self.start_time = 0
        self.elapsed_time = 0
        
        self.load_level(1)

    def load_level(self, level):
        data = LevelGenerator.generate(level)
        self.grid = data["puzzle"]
        self.solution = data["solution"]
        self.target = data["target"]
        self.hints_pool = data["hints_available"]
        
        self.level = level
        self.mistakes = 0
        self.selected = None
        self.message = f"Level {level}: Find the Target!"
        
        # Reset pencil marks for the new grid
        self.pencil_marks = [[set() for _ in range(9)] for _ in range(9)]
        self.start_time = time.time()

    def draw(self):
        self.screen.fill(WHITE)
        current_time = int(time.time() - self.start_time)
        
        # Draw Grid Lines
        for i in range(10):
            width = 4 if i % 3 == 0 else 1
            pygame.draw.line(self.screen, BLACK, (i * 60, 0), (i * 60, 540), width)
            pygame.draw.line(self.screen, BLACK, (0, i * 60), (540, i * 60), width)

        # Draw Cells
        for r in range(9):
            for c in range(9):
                x, y = c * 60, r * 60
                
                # Highlight Selected
                if self.selected == (r, c):
                    pygame.draw.rect(self.screen, (207, 226, 255), (x+1, y+1, 58, 58))

                # Target Highlight
                if (r, c) == self.target:
                    pygame.draw.rect(self.screen, GOLD, (x+5, y+5, 50, 50), 3)

                val = self.grid[r][c]
                if val != 0:
                    # Draw Fixed/Correct Numbers
                    color = BLACK if self.solution[r][c] == val else RED
                    text = self.font.render(str(val), True, color)
                    self.screen.blit(text, (x + 20, y + 10))
                else:
                    # Draw Pencil Marks
                    for m in self.pencil_marks[r][c]:
                        # Calculate mini-grid position for the tiny number
                        mx = x + ((m - 1) % 3) * 20 + 5
                        my = y + ((m - 1) // 3) * 20 + 2
                        m_text = self.pencil_font.render(str(m), True, GRAY)
                        self.screen.blit(m_text, (mx, my))

        # UI Panel (Bottom)
        mode_text = "PENCIL" if self.pencil_mode else "SOLVE"
        mode_color = BLUE if self.pencil_mode else BLACK
        
        ui_y = 550
        info = self.small_font.render(f"Mistakes: {self.mistakes}/{MAX_MISTAKES}  |  Level: {self.level}", True, RED)
        stats = self.small_font.render(f"Streak: {self.streak}  |  Time: {current_time}s", True, BLACK)
        mode_display = self.small_font.render(f"MODE: {mode_text} (P to toggle)", True, mode_color)
        
        self.screen.blit(info, (10, ui_y))
        self.screen.blit(stats, (10, ui_y + 25))
        self.screen.blit(mode_display, (320, ui_y + 25))
        self.screen.blit(self.small_font.render(self.message, True, BLUE), (10, ui_y + 50))

    def handle_input(self, r, c, val):
        if self.grid[r][c] != 0: return

        if self.pencil_mode:
            if val in self.pencil_marks[r][c]:
                self.pencil_marks[r][c].remove(val)
            else:
                self.pencil_marks[r][c].add(val)
        else:
            if self.solution[r][c] == val:
                self.grid[r][c] = val
                # Check if we hit the target
                if (r, c) == self.target:
                    self.streak += 1
                    self.message = f"Success! +1 Streak. Next Level..."
                    # In a real app, you'd save to DB here
                    pygame.display.flip()
                    pygame.time.delay(1500)
                    self.load_level(self.level + 1)
            else:
                self.mistakes += 1
                if self.mistakes >= MAX_MISTAKES:
                    self.streak = 0 # Reset streak on fail
                    self.message = "Game Over! Resetting..."
                    pygame.display.flip()
                    pygame.time.delay(2000)
                    self.load_level(1)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if pos[1] < 540: # Only select inside the grid
                        self.selected = (pos[1] // 60, pos[0] // 60)
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p: # Toggle Pencil Mode
                        self.pencil_mode = not self.pencil_mode
                    
                    if event.key == pygame.K_h: # Hint Key
                        if self.hints_pool:
                            hr, hc = self.hints_pool.pop(0)
                            self.grid[hr][hc] = self.solution[hr][hc]

                    if self.selected and event.unicode.isdigit() and event.unicode != '0':
                        self.handle_input(self.selected[0], self.selected[1], int(event.unicode))
                    
                    # Keyboard Navigation
                    if self.selected:
                        r, c = self.selected
                        if event.key == pygame.K_UP: self.selected = (max(0, r-1), c)
                        if event.key == pygame.K_DOWN: self.selected = (min(8, r+1), c)
                        if event.key == pygame.K_LEFT: self.selected = (r, max(0, c-1))
                        if event.key == pygame.K_RIGHT: self.selected = (r, min(8, c+1))

            self.draw()
            pygame.display.flip()