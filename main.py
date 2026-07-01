import pygame
import sys
import time
import math
import webbrowser
import random

pygame.init()
pygame.mixer.init()  # Инициализируем звуковой движок

WIDTH, HEIGHT = 1550, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Рокет Бульба: ОБРАТНО В БЕЛАРУСЬ")
clock = pygame.time.Clock()

# === ШРИФТЫ ===
font_large = pygame.font.Font('font.ttf', 45)
font_medium = pygame.font.Font('font.ttf', 24)
font_small = pygame.font.Font('font.ttf', 20)

# === ЗАГРУЗКА КАРТИНОК ===
potato_sprite_1 = pygame.image.load('images/sprite_1.png').convert_alpha()
potato_sprite_1 = pygame.transform.scale(potato_sprite_1, (40, 40))
potato_sprite_2 = pygame.image.load('images/sprite_2.png').convert_alpha()
potato_sprite_2 = pygame.transform.scale(potato_sprite_2, (40, 40))
potato_sprite_3 = pygame.image.load('images/sprite_3.png').convert_alpha()
potato_sprite_3 = pygame.transform.scale(potato_sprite_3, (40, 40))
chips_circle = pygame.image.load('images/chips_circle.png').convert_alpha()
chips_circle = pygame.transform.scale(chips_circle, (60, 60))
chips_long = pygame.image.load('images/chips_long.png').convert_alpha()
chips_long = pygame.transform.scale(chips_long, (30, 150))
wall = pygame.image.load('images/wall.png').convert_alpha()
wall = pygame.transform.scale(wall, (20, 20))
portal_1 = pygame.image.load('images/portal_1.png').convert_alpha()
portal_1 = pygame.transform.scale(portal_1, (80, 750))
portal_2 = pygame.image.load('images/portal_2.png').convert_alpha()
portal_2 = pygame.transform.scale(portal_2, (550, 50))
knife = pygame.image.load('images/knife.png').convert_alpha()
knife = pygame.transform.scale(knife, (80, 15))
knife_2 = pygame.transform.flip(knife, True, False)
bg_2 = pygame.image.load('images/bg_2.png').convert_alpha()
bg_2 = pygame.transform.scale(bg_2, (550, 800))
portal_3 = pygame.image.load('images/portal_3.png').convert_alpha()
portal_3 = pygame.transform.scale(portal_3, (80, 80))
bg_1 = pygame.image.load('images/fire.png').convert_alpha()
bg_1 = pygame.transform.scale(bg_1, (1550, 80))
bg_3 = pygame.image.load('images/bg_3.png').convert_alpha()
bg_3 = pygame.transform.scale(bg_3, (1550, 800))
intro = pygame.image.load('images/bg_5.png').convert_alpha()
intro = pygame.transform.scale(intro, (1550, 800))
flag = pygame.image.load('images/flag.png').convert_alpha()
flag = pygame.transform.scale(flag, (110, 150))
bolba_bog = pygame.image.load('images/bolba_bog.png').convert_alpha()
bolba_bog = pygame.transform.scale(bolba_bog, (150, 150))
final_bg = pygame.image.load('images/final_bg.png').convert_alpha()
final_bg = pygame.transform.scale(final_bg, (1550, 800))
grass = pygame.image.load('images/grass.png').convert_alpha()
grass = pygame.transform.scale(grass, (1550, 100))
bg_1_5 = pygame.image.load('images/final_bg.png').convert_alpha()
bg_1_5 = pygame.transform.scale(bg_1_5, (1550, 800))
maze_bg = pygame.image.load('images/maze.png').convert_alpha()
maze_bg = pygame.transform.scale(maze_bg, (1550, 800))


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
            surface.blit(chips_long, self.rect.topleft)
        else:
            surface.blit(chips_circle, self.rect.topleft)


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
        if self.side == 'left':
            surface.blit(knife, (self.rect.x, self.rect.y - cam_y))
        else:
            surface.blit(knife_2, (self.rect.x, self.rect.y - cam_y))


# === ГЛАВНЫЙ КЛАСС ИГРЫ ===
class Game:
    def __init__(self):
        self.state = "MENU"
        self.particles = []

        btn_w = 600
        btn_x = WIDTH // 2 - btn_w // 2

        self.btn_play = Button("ИГРАТЬ", btn_x, 300, btn_w, 70)
        self.btn_help = Button("ПОМОЩЬ", btn_x, 400, btn_w, 70)
        self.btn_creators = Button("СОЗДАТЕЛИ", btn_x, 500, btn_w, 70)

        self.btn_back = Button("В ГЛАВНОЕ МЕНЮ", WIDTH - btn_w - 50, HEIGHT - 100, btn_w, 60)
        self.btn_start_lvl = Button("НАЧАТЬ ИГРУ", btn_x, HEIGHT - 100, btn_w, 60)

        self.px, self.py = 0, 0
        self.p_rect = pygame.Rect(0, 0, 40, 40)
        self.vy = 0

        self.facing_right = True

        self.cutscene_timer = 0
        self.transition_timer = 0
        self.next_state = ""
        self.next_level = 1

        # Переменная для отслеживания текущей музыки
        self.current_music = None

        self.dark_surf = pygame.Surface((WIDTH, HEIGHT))
        self.dark_surf.set_colorkey((255, 255, 255))

        self.init_level(1)

    # Функция для переключения музыки
    def change_music(self, filename):
        if self.current_music != filename:
            self.current_music = filename
            try:
                # Добавляем путь 'music/' перед именем файла
                pygame.mixer.music.load(f"music/{filename}")
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"Не удалось загрузить музыку music/{filename}: {e}")

    def trigger_death(self, level):
        self.init_level(level)

    def init_level(self, lvl):
        self.particles.clear()
        self.facing_right = True
        if lvl == 1:
            self.px, self.py = 300, HEIGHT // 2
            self.vy = 0
            self.chips = []
            self.spawn_timer = 0
            self.level_1_timer = 0
            self.portal_spawned = False
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
        # === УПРАВЛЕНИЕ МУЗЫКОЙ ===
        if self.state in ["MENU", "HELP", "CREATORS"] or self.state.startswith("INTRO_"):
            self.change_music("menu_music.mp3")
        elif self.state == "TRANSITION":
            self.change_music("cutscene.mp3")
        elif self.state == "LEVEL_1":
            self.change_music("location_1.mp3")
        elif self.state == "LEVEL_2":
            self.change_music("location_2.mp3")
        elif self.state == "LEVEL_3":
            self.change_music("location_3.mp3")
        elif self.state in ["CUTSCENE", "WIN"]:
            self.change_music("final.mp3")
        # ==========================

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
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.px -= 12
                self.facing_right = False
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.px += 12
                self.facing_right = True

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

            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.px -= speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.px += speed

            if keys[pygame.K_w] or keys[pygame.K_UP]: self.py -= speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]: self.py += speed

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
                draw_centered_text(screen, line, font_small, 400 + i * 50)

            self.btn_start_lvl.rect.x = WIDTH // 2 - 300
            if self.btn_start_lvl.draw(screen, mouse_pos) and mouse_click:
                self.state = f"LEVEL_{lvl}"
                time.sleep(0.2)

        elif self.state == "TRANSITION":
            screen.fill((255, 255, 255))

        elif self.state == "LEVEL_1":
            screen.blit(bg_1_5, (0, 0))
            screen.blit(bg_1, (0, HEIGHT - 80))

            if self.portal_spawned:
                screen.blit(portal_1, self.portal_rect)

            for c in self.chips: c.draw(screen)
            screen.blit(potato_sprite_1, self.p_rect.topleft)

        elif self.state == "LEVEL_2":
            screen.blit(bg_2, (500, 0))
            pygame.draw.rect(screen, (0, 0, 0), (500, HEIGHT - 80 - self.cam_y, 550, 800))
            screen.blit(portal_2, (self.portal_rect_lvl2.x, self.portal_rect_lvl2.y - self.cam_y))

            for k in self.knives: k.draw(screen, self.cam_y)

            img = potato_sprite_2
            if not self.facing_right: img = pygame.transform.flip(img, True, False)
            screen.blit(img, (self.px, self.py - self.cam_y))

            pygame.draw.rect(screen, (0, 0, 0), (0, 0, 500, HEIGHT))
            pygame.draw.rect(screen, (0, 0, 0), (1050, 0, 500, HEIGHT))

        elif self.state == "LEVEL_3":
            screen.blit(maze_bg, (0, 0))

            for w in self.maze_walls:
                for wx in range(w.x, w.x + w.width, 20):
                    for wy in range(w.y, w.y + w.height, 20):
                        screen.blit(wall, (wx, wy))

            screen.blit(portal_3, self.exit_rect)

            for p in self.particles: p.draw(screen)
            screen.blit(potato_sprite_3, self.p_rect.topleft)

            self.dark_surf.fill((0, 0, 0))
            pygame.draw.circle(self.dark_surf, (255, 255, 255), (self.px + 20, self.py + 20), 80)
            screen.blit(self.dark_surf, (0, 0))

        elif self.state == "CUTSCENE":
            elapsed = time.time() - self.cutscene_timer
            ground_y = HEIGHT - 100

            screen.blit(final_bg, (0, 0))
            screen.blit(grass, (0, ground_y))
            screen.blit(bolba_bog, (1350, 90))

            if elapsed < 12:
                screen.blit(potato_sprite_3, (WIDTH // 2 - 25, ground_y - 40))
            else:
                scaled_img = pygame.transform.scale(potato_sprite_2, (50, 50))
                screen.blit(scaled_img, (WIDTH // 2 - 25, ground_y - 50))

            if elapsed < 5:
                draw_text_outline(screen, "Бульба бог: Здравствуй Бульба босс, я Бульба бог.", font_small, 50, 50)
            elif elapsed < 10:
                draw_text_outline(screen, "Бульба бог: я видел твое страдание и решил тебе помочь.", font_small, 50, 50)
            elif elapsed < 12:
                screen.fill((255, 255, 255))
            elif elapsed < 17:
                draw_centered_text(screen, "Бульба босс: Спасибо тебе Бульба бог, из за тебя я снова картошка.",
                                   font_small, HEIGHT // 2 - 50)
            elif elapsed < 22:
                draw_text_outline(screen, "Бульба бог: не за что, продолжай свое путешествие Бульба босс.", font_small,
                                  50, 50)
            elif elapsed < 24:
                screen.fill((255, 255, 255))
            else:
                self.state = "WIN"
                self.px = 100

        elif self.state == "WIN":
            ground_y = HEIGHT - 100
            screen.blit(final_bg, (0, 0))
            screen.blit(grass, (0, ground_y))
            screen.blit(flag, (1300, 550))

            draw_text_outline(screen, "ИДИ ПРЯМО ->", font_medium, 50, 50)

            self.p_rect.y = ground_y - 40
            screen.blit(potato_sprite_2, self.p_rect.topleft)

            if self.px >= 1250:
                self.px = 1250
                pygame.draw.rect(screen, (50, 50, 50), (WIDTH // 2 - 400, HEIGHT // 2 - 150, 800, 300))
                pygame.draw.rect(screen, (255, 255, 255), (WIDTH // 2 - 400, HEIGHT // 2 - 150, 800, 300), 5)
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