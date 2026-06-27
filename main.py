import pygame
import sys
import time
import math
import webbrowser
import random

pygame.init()

WIDTH, HEIGHT = 1550, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Рокет Бульба: Картофельный путь")
clock = pygame.time.Clock()

# === ШРИФТЫ ===
try:
    font_large = pygame.font.Font('fonts/main_font.ttf', 70)
    font_medium = pygame.font.Font('fonts/main_font.ttf', 40)
    font_small = pygame.font.Font('fonts/main_font.ttf', 25)
except:
    font_large = pygame.font.SysFont("Arial", 70, bold=True)
    font_medium = pygame.font.SysFont("Arial", 40, bold=True)
    font_small = pygame.font.SysFont("Arial", 25, bold=True)


def draw_text_outline(surface, text, font, x, y, color=(255, 255, 255)):
    for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (-2, 0), (2, 0), (0, -2), (0, 2)]:
        surface.blit(font.render(text, True, (0, 0, 0)), (x + dx, y + dy))
    surface.blit(font.render(text, True, color), (x, y))


def draw_centered_text(surface, text, font, y_pos, color=(255, 255, 255)):
    text_surf = font.render(text, True, color)
    rect = text_surf.get_rect(center=(WIDTH // 2, y_pos))
    for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (-2, 0), (2, 0), (0, -2), (0, 2)]:
        surface.blit(font.render(text, True, (0, 0, 0)), (rect.x + dx, rect.y + dy))
    surface.blit(text_surf, rect)


# === КЛАССЫ ИГРОВЫХ ОБЪЕКТОВ ===

class Button:
    def __init__(self, text, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self, surface, mouse_pos):
        hovered = self.rect.collidepoint(mouse_pos)
        color = (100, 100, 150) if hovered else (70, 70, 100)
        pygame.draw.rect(surface, color, self.rect)
        if hovered:
            pygame.draw.rect(surface, (255, 255, 255), self.rect, 3)

        text_surf = font_medium.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (-2, 0), (2, 0), (0, -2), (0, 2)]:
            surface.blit(font_medium.render(self.text, True, (0, 0, 0)), (text_rect.x + dx, text_rect.y + dy))
        surface.blit(text_surf, text_rect)

        return hovered


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.timer = random.randint(20, 40)
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.timer -= 1

    def draw(self, surface, cam_x=0, cam_y=0):
        if self.timer > 0:
            pygame.draw.circle(surface, self.color, (int(self.x - cam_x), int(self.y - cam_y)), max(1, self.timer // 5))


class Chip:
    def __init__(self):
        self.is_long = random.choice([True, False])
        if self.is_long:
            self.rect = pygame.Rect(WIDTH, random.randint(50, HEIGHT - 250), 30, 150)
        else:
            self.rect = pygame.Rect(WIDTH, random.randint(50, HEIGHT - 100), 60, 60)
        self.speed = random.randint(6, 10)

    def update(self):
        self.rect.x -= self.speed

    def draw(self, surface):
        if self.is_long:
            pygame.draw.rect(surface, (255, 200, 50), self.rect)
        else:
            pygame.draw.ellipse(surface, (255, 220, 100), self.rect)


class Knife:
    def __init__(self, y, side):
        self.side = side
        self.y = y
        self.width, self.height = 80, 15
        if self.side == 'left':
            self.rect = pygame.Rect(0, self.y, self.width, self.height)
            self.target_x = 500
        else:
            self.rect = pygame.Rect(WIDTH, self.y, self.width, self.height)
            self.target_x = 1050 - self.width
        self.speed = 15
        self.stopped = False

    def update(self):
        if not self.stopped:
            if self.side == 'left':
                self.rect.x += self.speed
                if self.rect.x >= self.target_x:
                    self.rect.x = self.target_x
                    self.stopped = True
            else:
                self.rect.x -= self.speed
                if self.rect.x <= self.target_x:
                    self.rect.x = self.target_x
                    self.stopped = True

    def draw(self, surface, cam_y):
        pygame.draw.rect(surface, (200, 200, 200), (self.rect.x, self.rect.y - cam_y, self.width, self.height))
        if self.side == 'left':
            pygame.draw.rect(surface, (100, 50, 0), (self.rect.x, self.rect.y - cam_y, 30, self.height))
        else:
            pygame.draw.rect(surface, (100, 50, 0), (self.rect.right - 30, self.rect.y - cam_y, 30, self.height))


# === ГЛАВНЫЙ КЛАСС ИГРЫ ===
class Game:
    def __init__(self):
        self.state = "MENU"
        self.particles = []

        btn_x = WIDTH // 2 - 150
        self.btn_play = Button("ИГРАТЬ", btn_x, 300, 300, 70)
        self.btn_help = Button("ПОМОЩЬ", btn_x, 400, 300, 70)
        self.btn_creators = Button("СОЗДАТЕЛИ", btn_x, 500, 300, 70)
        self.btn_back = Button("В ГЛАВНОЕ МЕНЮ", WIDTH - 400, HEIGHT - 100, 350, 60)
        self.btn_start_lvl = Button("НАЧАТЬ ИГРУ", WIDTH // 2 - 150, HEIGHT - 100, 300, 60)

        self.px, self.py = 0, 0
        self.p_rect = pygame.Rect(0, 0, 40, 40)
        self.vy = 0

        self.cutscene_timer = 0

        self.transition_timer = 0
        self.next_state = ""
        self.next_level = 1

        self.init_level(1)

    def trigger_death(self, level):
        self.init_level(level)

    def init_level(self, lvl):
        self.particles.clear()
        if lvl == 1:
            self.px, self.py = 300, HEIGHT // 2
            self.vy = 0
            self.chips = []
            self.spawn_timer = 0
            self.level_1_timer = 0
            self.portal_spawned = False
            # ПОРТАЛ НЕ ЗАДЕВАЕТ ФРИТЮР (обрезан на 50 пикселей снизу)
            self.portal_rect = pygame.Rect(WIDTH, 0, 80, HEIGHT - 50)
        elif lvl == 2:
            self.px, self.py = WIDTH // 2, HEIGHT - 120
            self.vy = 0
            self.cam_y = self.py - HEIGHT // 2
            self.knives = []
            current_y = HEIGHT - 200
            for i in range(30):
                side = 'left' if i % 2 == 0 else 'right'
                self.knives.append(Knife(current_y, side))
                current_y -= 160
            self.finish_y = current_y
            self.portal_rect_lvl2 = pygame.Rect(500, self.finish_y - 50, 550, 50)
        elif lvl == 3:
            self.px, self.py = 100, 100
            self.maze_walls = [
                pygame.Rect(0, 0, WIDTH, 20), pygame.Rect(0, HEIGHT - 20, WIDTH, 20),
                pygame.Rect(0, 0, 20, HEIGHT), pygame.Rect(WIDTH - 20, 0, 20, HEIGHT),
                pygame.Rect(200, 0, 40, 500), pygame.Rect(200, 650, 40, 150),
                pygame.Rect(400, 150, 40, 650), pygame.Rect(400, 150, 300, 40),
                pygame.Rect(600, 350, 40, 450), pygame.Rect(750, 0, 40, 600),
                pygame.Rect(950, 200, 40, 600), pygame.Rect(950, 200, 300, 40),
                pygame.Rect(1150, 400, 40, 400), pygame.Rect(1150, 400, 300, 40),
                pygame.Rect(1350, 0, 40, 300)
            ]
            self.exit_rect = pygame.Rect(1400, 650, 80, 80)

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        keys = pygame.key.get_pressed()

        for p in self.particles[:]:
            p.update()
            if p.timer <= 0: self.particles.remove(p)

        if self.state == "TRANSITION":
            if time.time() - self.transition_timer >= 2:
                self.state = self.next_state
                if self.next_state == "CUTSCENE":
                    self.cutscene_timer = time.time()
                else:
                    self.init_level(self.next_level)

        elif self.state == "LEVEL_1":
            self.vy += 0.5
            if keys[pygame.K_SPACE]:
                self.vy = -8
            self.py += self.vy

            if self.py < 0:
                self.py = 0
                self.vy = 0

            self.p_rect.topleft = (self.px, self.py)

            self.level_1_timer += 1
            if self.level_1_timer > 900:
                self.portal_spawned = True
                self.portal_rect.x -= 3
                if self.p_rect.colliderect(self.portal_rect):
                    self.state = "TRANSITION"
                    self.transition_timer = time.time()
                    self.next_state = "INTRO_2"
                    self.next_level = 2

            if not self.portal_spawned:
                self.spawn_timer += 1
                if self.spawn_timer > 60:
                    self.chips.append(Chip())
                    self.spawn_timer = 0

            for c in self.chips[:]:
                c.update()
                if c.rect.colliderect(self.p_rect):
                    self.trigger_death(1)
                if c.rect.right < 0:
                    self.chips.remove(c)

            if self.py > HEIGHT - 50:
                self.trigger_death(1)

        elif self.state == "LEVEL_2":
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.px -= 12
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.px += 12

            if self.px < 500: self.px = 500
            if self.px > 1010: self.px = 1010

            self.vy += 0.8
            self.py += self.vy
            self.p_rect.topleft = (self.px, self.py)

            self.cam_y += (self.py - HEIGHT // 2 - self.cam_y) * 0.1

            on_ground = False
            if self.py >= HEIGHT - 120 and self.cam_y > -100:
                self.py = HEIGHT - 120
                self.vy = 0
                on_ground = True

            for k in self.knives:
                if k.y > self.cam_y - 200 and k.y < self.cam_y + HEIGHT + 200:
                    k.update()
                if self.vy > 0 and self.p_rect.colliderect(k.rect) and self.p_rect.bottom <= k.rect.centery + 10:
                    self.py = k.rect.top - 40
                    self.vy = 0
                    on_ground = True

            if keys[pygame.K_SPACE] and on_ground:
                self.vy = -20

            if self.py > self.cam_y + HEIGHT + 50 or self.py > HEIGHT:
                self.trigger_death(2)

            if self.p_rect.colliderect(self.portal_rect_lvl2):
                self.state = "TRANSITION"
                self.transition_timer = time.time()
                self.next_state = "INTRO_3"
                self.next_level = 3

        elif self.state == "LEVEL_3":
            speed = 5
            old_x, old_y = self.px, self.py
            if keys[pygame.K_w] or keys[pygame.K_UP]: self.py -= speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]: self.py += speed
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.px -= speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.px += speed

            self.p_rect.topleft = (self.px, self.py)

            for w in self.maze_walls:
                if self.p_rect.colliderect(w):
                    self.px, self.py = old_x, old_y
                    self.p_rect.topleft = (self.px, self.py)

            for _ in range(2):
                self.particles.append(Particle(self.exit_rect.centerx + random.randint(-20, 20),
                                               self.exit_rect.centery + random.randint(-20, 20), (255, 255, 255)))

            if self.p_rect.colliderect(self.exit_rect):
                self.state = "TRANSITION"
                self.transition_timer = time.time()
                self.next_state = "CUTSCENE"
                self.next_level = 0

        elif self.state == "WIN":
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.px += 5
            self.p_rect.topleft = (self.px, HEIGHT - 150)

    def draw(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]

        screen.fill((20, 20, 30))

        if self.state == "MENU":
            draw_centered_text(screen, "РОКЕТ БУЛЬБА: ОБРАТНО В БЕЛАРУСЬ", font_large, 150, (255, 255, 255))
            if self.btn_play.draw(screen, mouse_pos) and mouse_click: self.state = "INTRO_1"
            if self.btn_help.draw(screen, mouse_pos) and mouse_click: self.state = "HELP"
            if self.btn_creators.draw(screen, mouse_pos) and mouse_click: self.state = "CREATORS"

        elif self.state == "HELP":
            lines = [
                "В этой игре ты играешь за рокет босса, который стал картошкой.",
                "Твоя задача — проходить разные испытания и выжить."
            ]
            for i, line in enumerate(lines):
                draw_centered_text(screen, line, font_medium, 300 + i * 60)
            if self.btn_back.draw(screen, mouse_pos) and mouse_click: self.state = "MENU"

        elif self.state == "CREATORS":
            draw_centered_text(screen, "- artem0804", font_medium, 300)
            draw_centered_text(screen, "- Daniel", font_medium, 380)
            if self.btn_back.draw(screen, mouse_pos) and mouse_click: self.state = "MENU"

        elif self.state.startswith("INTRO_"):
            lvl = self.state.split("_")[1]
            draw_centered_text(screen, f"ЛОКАЦИЯ {lvl}", font_large, 200)
            if lvl == "1":
                lines = ["Вам надо уклоняться от чипсов, вылетающих от фритюра,", "и не падать вниз во фритюр."]
            elif lvl == "2":
                lines = ["В вас с обеих сторон будут кидать ножи, чтоб нарезать вас.",
                         "Ваша цель — уклоняться от них и забраться по ним наверх."]
            elif lvl == "3":
                lines = ["Ты, к сожалению, стал упаковкой чипсов.",
                         "Но у тебя еще есть задача: выбраться из лабиринта других чипсов."]

            for i, line in enumerate(lines):
                draw_centered_text(screen, line, font_small, 400 + i * 40)

            self.btn_start_lvl.rect.x = WIDTH // 2 - 150
            if self.btn_start_lvl.draw(screen, mouse_pos) and mouse_click:
                self.state = f"LEVEL_{lvl}"
                time.sleep(0.2)

        elif self.state == "TRANSITION":
            screen.fill((255, 255, 255))

        elif self.state == "LEVEL_1":
            screen.fill((50, 20, 20))
            pygame.draw.rect(screen, (255, 100, 0), (0, HEIGHT - 50, WIDTH, 50))

            if self.portal_spawned:
                pygame.draw.rect(screen, (200, 50, 255), self.portal_rect)

            for c in self.chips: c.draw(screen)
            pygame.draw.rect(screen, (255, 200, 50), self.p_rect)

        elif self.state == "LEVEL_2":
            pygame.draw.rect(screen, (80, 50, 50), (500, 0, 550, HEIGHT))
            pygame.draw.rect(screen, (0, 0, 0), (500, HEIGHT - 80 - self.cam_y, 550, 800))

            pygame.draw.rect(screen, (200, 50, 255), (
            self.portal_rect_lvl2.x, self.portal_rect_lvl2.y - self.cam_y, self.portal_rect_lvl2.width,
            self.portal_rect_lvl2.height))

            for k in self.knives: k.draw(screen, self.cam_y)
            pygame.draw.rect(screen, (255, 200, 50), (self.px, self.py - self.cam_y, 40, 40))
            pygame.draw.rect(screen, (0, 0, 0), (0, 0, 500, HEIGHT))
            pygame.draw.rect(screen, (0, 0, 0), (1050, 0, 500, HEIGHT))

        elif self.state == "LEVEL_3":
            screen.fill((50, 50, 50))
            for w in self.maze_walls:
                pygame.draw.rect(screen, (100, 40, 40), w)

            pygame.draw.rect(screen, (255, 255, 255), self.exit_rect)
            for p in self.particles: p.draw(screen)

            pygame.draw.rect(screen, (255, 0, 0), self.p_rect)

            dark = pygame.Surface((WIDTH, HEIGHT))
            dark.fill((0, 0, 0))
            pygame.draw.circle(dark, (255, 255, 255), (self.px + 20, self.py + 20), 80)
            dark.set_colorkey((255, 255, 255))
            screen.blit(dark, (0, 0))

        elif self.state == "CUTSCENE":
            elapsed = time.time() - self.cutscene_timer

            ground_y = HEIGHT - 100
            pygame.draw.rect(screen, (135, 206, 235), (0, 0, WIDTH, ground_y))
            pygame.draw.rect(screen, (34, 139, 34), (0, ground_y, WIDTH, HEIGHT - ground_y))

            pygame.draw.circle(screen, (255, 255, 255), (WIDTH - 150, 150), 50)
            pygame.draw.circle(screen, (255, 255, 255), (WIDTH - 100, 150), 60)
            pygame.draw.rect(screen, (255, 255, 200), (WIDTH - 150, 120, 60, 60))

            p_color = (255, 0, 0) if elapsed < 12 else (255, 200, 50)
            pygame.draw.rect(screen, p_color, (WIDTH // 2 - 25, ground_y - 50, 50, 50))

            if elapsed < 5:
                draw_text_outline(screen, "Бульба бог: Здравствуй Бульба босс, я Бульба бог.", font_small, WIDTH - 800,
                                  50)
            elif elapsed < 10:
                draw_text_outline(screen, "Бульба бог: я видел твое страдание и решил тебе помочь.", font_small,
                                  WIDTH - 850, 50)
            elif elapsed < 12:
                screen.fill((255, 255, 255))
            elif elapsed < 17:
                draw_centered_text(screen, "Бульба босс: Спасибо тебе Бульба бог, из за тебя я снова картошка.",
                                   font_small, HEIGHT // 2 - 50)
            elif elapsed < 22:
                draw_text_outline(screen, "Бульба бог: не за что, продолжай свое путешествие Бульба босс.", font_small,
                                  WIDTH - 900, 50)
            elif elapsed < 24:
                screen.fill((255, 255, 255))
            else:
                self.state = "WIN"
                self.px = 100

        elif self.state == "WIN":
            ground_y = HEIGHT - 100
            pygame.draw.rect(screen, (135, 206, 235), (0, 0, WIDTH, ground_y))
            pygame.draw.rect(screen, (34, 139, 34), (0, ground_y, WIDTH, HEIGHT - ground_y))

            flag_x = 1300
            pygame.draw.rect(screen, (200, 200, 200), (flag_x, ground_y - 150, 10, 150))
            pygame.draw.rect(screen, (255, 0, 0), (flag_x + 10, ground_y - 150, 100, 40))
            pygame.draw.rect(screen, (0, 200, 0), (flag_x + 10, ground_y - 110, 100, 20))

            draw_text_outline(screen, "ИДИ ПРЯМО ->", font_medium, 50, 50)
            self.p_rect.y = ground_y - 40
            pygame.draw.rect(screen, (255, 200, 50), self.p_rect)

            if self.px >= flag_x - 50:
                self.px = flag_x - 50
                pygame.draw.rect(screen, (50, 50, 50), (WIDTH // 2 - 350, HEIGHT // 2 - 150, 700, 300))
                pygame.draw.rect(screen, (255, 255, 255), (WIDTH // 2 - 350, HEIGHT // 2 - 150, 700, 300), 5)
                draw_centered_text(screen, "ПОЗДРАВЛЯЕМ, ТЫ ПРОШЕЛ ИГРУ!", font_medium, HEIGHT // 2 - 50)

        pygame.display.flip()


game = Game()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    game.update()
    game.draw()
    clock.tick(60)