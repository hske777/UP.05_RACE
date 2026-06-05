import tkinter as tk
from tkinter import messagebox
import random
import time
import json
import os

WIDTH = 1920
HEIGHT = 1080

ROAD_LEFT = 760
ROAD_RIGHT = 1160
ROAD_CENTER = (ROAD_LEFT + ROAD_RIGHT) // 2

# ФИКСИРОВАННЫЕ ПОЗИЦИИ ПОЛОС
LANE_POSITIONS = [
    ROAD_LEFT + 50,  # 0 - крайняя левая
    ROAD_LEFT + 150,  # 1 - левая
    ROAD_CENTER - 50,  # 2 - левая центральная
    ROAD_CENTER + 50,  # 3 - правая центральная
    ROAD_RIGHT - 150,  # 4 - правая
    ROAD_RIGHT - 50  # 5 - крайняя правая
]

# ФИКСИРОВАННЫЕ ПРЕПЯТСТВИЯ ДЛЯ ЛЕСНОЙ ТРАССЫ
FOREST_OBSTACLES = [
    (1, -500, "tree"), (2, -800, "rock"), (4, -1200, "tree"),
    (0, -1600, "rock"), (3, -2000, "tree"), (5, -2500, "block"),
    (2, -3000, "tree"), (4, -3500, "rock"), (1, -4000, "tree"),
    (3, -4500, "block"), (0, -5000, "tree"), (5, -5500, "rock"),
]

SAVE_FILE = "record.json"


class RacingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Гонки")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.state("zoomed")

        self.current_track = None
        self.menu_frame = tk.Frame(root, bg="black")  # ЧЕРНЫЙ ФОН
        self.menu_frame.pack(fill="both", expand=True)

        self.show_menu()

    def show_menu(self):
        for w in self.menu_frame.winfo_children():
            w.destroy()

        # ЧЕРНЫЙ ФОН через canvas
        menu_canvas = tk.Canvas(self.menu_frame, width=WIDTH, height=HEIGHT, bg="black", highlightthickness=0)
        menu_canvas.pack(fill="both", expand=True)

        # Заголовок
        menu_canvas.create_text(
            WIDTH // 2, 200,
            text="ГОНКИ",
            font=("Arial", 80, "bold"),
            fill="red"
        )

        best = self.load_best()
        if best:
            menu_canvas.create_text(
                WIDTH // 2, 300,
                text=f"Лучшее время: {best:.2f} сек",
                font=("Arial", 28),
                fill="yellow"
            )

        # Кнопка "ВЫБОР ТРАССЫ" (на canvas)
        btn_bg = tk.Frame(self.menu_frame, bg="black")
        btn_bg.place(x=WIDTH // 2 - 150, y=400, width=300, height=60)

        select_btn = tk.Button(
            btn_bg,
            text="ВЫБОР ТРАССЫ",
            font=("Arial", 24, "bold"),
            bg="blue",
            fg="white",
            cursor="hand2",
            command=self.show_track_selection
        )
        select_btn.pack(fill="both", expand=True)

        # Кнопка "ВЫХОД"
        btn_bg2 = tk.Frame(self.menu_frame, bg="black")
        btn_bg2.place(x=WIDTH // 2 - 150, y=490, width=300, height=60)

        exit_btn = tk.Button(
            btn_bg2,
            text="ВЫХОД",
            font=("Arial", 24, "bold"),
            bg="red",
            fg="white",
            cursor="hand2",
            command=self.root.destroy
        )
        exit_btn.pack(fill="both", expand=True)

        # Управление
        menu_canvas.create_text(
            WIDTH // 2, 600,
            text="Управление: ↑/↓ - скорость | ←/→ - поворот | ESC - выход в главное меню",
            font=("Arial", 20),
            fill="gray"
        )

        # Звезды на фоне для красоты
        for _ in range(100):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            menu_canvas.create_oval(x, y, x + 2, y + 2, fill="white", outline="")

    def show_track_selection(self):
        """Окно выбора трассы 1920x1080"""
        self.menu_frame.pack_forget()

        self.track_window = tk.Toplevel(self.root)
        self.track_window.title("Выбор трассы")
        self.track_window.geometry(f"{WIDTH}x{HEIGHT}")
        self.track_window.state("zoomed")
        self.track_window.configure(bg="black")
        self.track_window.transient(self.root)
        self.track_window.grab_set()

        # Фон с звездами
        track_canvas = tk.Canvas(self.track_window, width=WIDTH, height=HEIGHT, bg="black", highlightthickness=0)
        track_canvas.pack(fill="both", expand=True)

        for _ in range(100):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            track_canvas.create_oval(x, y, x + 2, y + 2, fill="white", outline="")

        track_canvas.create_text(
            WIDTH // 2, 150,
            text="ВЫБОР ТРАССЫ",
            font=("Arial", 60, "bold"),
            fill="yellow"
        )

        # Лесная трасса (квадрат)
        forest_x = WIDTH // 2 - 250
        forest_y = 300

        # Квадрат
        track_canvas.create_rectangle(
            forest_x, forest_y, forest_x + 500, forest_y + 400,
            fill="#228B22", outline="white", width=5
        )

        # Эмодзи дерева
        track_canvas.create_text(
            forest_x + 250, forest_y + 150,
            text="🌲",
            font=("Arial", 100)
        )

        track_canvas.create_text(
            forest_x + 250, forest_y + 250,
            text="ЛЕСНАЯ ТРАССА",
            font=("Arial", 28, "bold"),
            fill="white"
        )

        # Кнопка выбора
        select_btn = tk.Button(
            self.track_window,
            text="ВЫБРАТЬ",
            font=("Arial", 24, "bold"),
            bg="green",
            fg="white",
            width=15,
            cursor="hand2",
            command=lambda: self.select_track("forest")
        )
        select_btn.place(x=forest_x + 150, y=forest_y + 330, width=200, height=50)

        # Кнопка "Главное меню"
        menu_btn = tk.Button(
            self.track_window,
            text="ГЛАВНОЕ МЕНЮ",
            font=("Arial", 24, "bold"),
            bg="orange",
            fg="white",
            width=15,
            cursor="hand2",
            command=self.back_to_menu
        )
        menu_btn.place(x=WIDTH // 2 - 150, y=750, width=300, height=60)

        self.track_window.bind("<Escape>", lambda e: self.back_to_menu())
        self.track_window.focus_set()

    def back_to_menu(self):
        if hasattr(self, 'track_window'):
            self.track_window.destroy()
        self.menu_frame.pack(fill="both", expand=True)
        self.show_menu()

    def select_track(self, track_name):
        self.current_track = track_name
        if hasattr(self, 'track_window'):
            self.track_window.destroy()
        self.start_game()

    def start_game(self):
        self.menu_frame.pack_forget()

        self.game_frame = tk.Frame(self.root)
        self.game_frame.pack(fill="both", expand=True)

        self.info = tk.Label(self.game_frame, font=("Arial", 18), bg="black", fg="white")
        self.info.pack(fill="x")

        self.canvas = tk.Canvas(
            self.game_frame,
            width=WIDTH,
            height=HEIGHT - 50,
            bg="#1a1a2e"
        )
        self.canvas.pack()

        self.paused = False
        self.game_over = False
        self.race_started = False
        self.finished = False

        self.game_speed = 5
        self.player_position_index = 2
        self.enemy_position_index = 4

        self.player_distance = 0
        self.enemy_distance = 0
        self.total_distance = 7000

        self.key_up = False
        self.key_down = False
        self.key_left = False
        self.key_right = False

        self.obstacles = []

        self.start_time = 0
        self.finish_time = 0

        # Рисуем дорогу
        self.draw_road()

        car_y_position = HEIGHT - 150

        # Создаем игрока
        self.player = self.create_car(LANE_POSITIONS[self.player_position_index], car_y_position, "#3366FF")

        # Создаем противника
        self.enemy = self.create_car(LANE_POSITIONS[self.enemy_position_index], car_y_position, "#FF6600")

        # Загружаем препятствия
        self.obstacles = []
        if self.current_track == "forest":
            for lane, y_pos, obs_type in FOREST_OBSTACLES:
                self.spawn_fixed_obstacle(lane, y_pos, obs_type)

        # Линии разметки
        self.lines = []
        for y in range(0, HEIGHT + 200, 80):
            line = self.canvas.create_rectangle(
                ROAD_CENTER - 5, y,
                ROAD_CENTER + 5, y + 40,
                fill="white"
            )
            self.lines.append(line)

        # Финишная линия (Y = 100)
        self.finish_line_y = 100
        self.finish_line = None
        self.finish_visible = False

        self.root.bind("<KeyPress>", self.key_press)
        self.root.bind("<KeyRelease>", self.key_release)
        self.root.bind("<space>", self.pause)
        self.root.bind("<Escape>", lambda e: self.exit_to_menu())

        self.root.focus_set()

        # Запускаем обратный отсчет
        self.countdown()

    def countdown(self):
        self.countdown_value = 3

        self.countdown_text = self.canvas.create_text(
            WIDTH // 2, HEIGHT // 2,
            text=str(self.countdown_value),
            font=("Arial", 120, "bold"),
            fill="yellow"
        )

        self.update_countdown()

    def update_countdown(self):
        if self.countdown_value > 0:
            self.canvas.itemconfig(self.countdown_text, text=str(self.countdown_value))
            self.countdown_value -= 1
            self.root.after(1000, self.update_countdown)
        else:
            self.canvas.delete(self.countdown_text)
            self.race_started = True
            self.start_time = time.time()
            self.update()

    def create_car(self, x, y, color):
        w, h = 50, 80
        car = self.canvas.create_rectangle(
            x - w // 2, y - h // 2,
            x + w // 2, y + h // 2,
            fill=color, outline="white", width=2
        )
        window1 = self.canvas.create_rectangle(
            x - 15, y - 20, x + 15, y + 5,
            fill="#88CCFF", outline="white", width=1
        )
        window2 = self.canvas.create_rectangle(
            x - 15, y + 10, x + 15, y + 30,
            fill="#88CCFF", outline="white", width=1
        )
        return {"body": car, "window1": window1, "window2": window2, "x": x, "y": y}

    def move_car(self, car, dx, dy):
        self.canvas.move(car["body"], dx, dy)
        self.canvas.move(car["window1"], dx, dy)
        self.canvas.move(car["window2"], dx, dy)
        car["x"] += dx
        car["y"] += dy

    def move_car_to_position(self, car, position_index):
        dx = LANE_POSITIONS[position_index] - car["x"]
        if dx != 0:
            self.move_car(car, dx, 0)

    def get_car_coords(self, car):
        return self.canvas.coords(car["body"])

    def draw_road(self):
        self.canvas.create_rectangle(
            ROAD_LEFT, 0, ROAD_RIGHT, HEIGHT,
            fill="#333333", outline=""
        )
        self.canvas.create_line(ROAD_LEFT, 0, ROAD_LEFT, HEIGHT, fill="yellow", width=5)
        self.canvas.create_line(ROAD_RIGHT, 0, ROAD_RIGHT, HEIGHT, fill="yellow", width=5)
        self.canvas.create_rectangle(0, 0, ROAD_LEFT, HEIGHT, fill="#228B22", outline="")
        self.canvas.create_rectangle(ROAD_RIGHT, 0, WIDTH, HEIGHT, fill="#228B22", outline="")

    def spawn_fixed_obstacle(self, lane, y_pos, obs_type):
        if obs_type == "block":
            color = "#8B4513"
            w, h = 25, 25
        elif obs_type == "rock":
            color = "#696969"
            w, h = 22, 22
        elif obs_type == "tree":
            color = "#006400"
            w, h = 20, 35
        else:
            color = "#FFA500"
            w, h = 20, 20

        x = LANE_POSITIONS[lane]

        obs = self.canvas.create_rectangle(
            x - w // 2, y_pos - h // 2,
            x + w // 2, y_pos + h // 2,
            fill=color, outline="yellow", width=2
        )

        self.obstacles.append({
            "id": obs,
            "x": x,
            "y": y_pos,
            "lane": lane,
            "type": obs_type,
            "width": w,
            "height": h
        })

    def spawn_finish_line(self):
        """Создание финишной линии на Y = 100"""
        if self.finish_line:
            for item in self.finish_line:
                self.canvas.delete(item)

        self.finish_line = []
        for i in range(ROAD_LEFT, ROAD_RIGHT, 50):
            rect = self.canvas.create_rectangle(
                i, self.finish_line_y, i + 40, self.finish_line_y + 15,
                fill="#FFA500", outline="white", width=2
            )
            self.finish_line.append(rect)

        text = self.canvas.create_text(ROAD_CENTER, self.finish_line_y - 20, text="ФИНИШ",
                                       font=("Arial", 30, "bold"), fill="#FFA500")
        self.finish_line.append(text)
        self.finish_visible = True

    def update_enemy_ai(self):
        """ИИ противника - пытается обогнать игрока"""
        if not self.enemy:
            return

        self.move_car(self.enemy, 0, self.game_speed)

        enemy_coords = self.get_car_coords(self.enemy)
        player_coords = self.get_car_coords(self.player)

        if not enemy_coords or not player_coords:
            return

        enemy_y = enemy_coords[1]
        player_y = player_coords[1]
        enemy_center_x = (enemy_coords[0] + enemy_coords[2]) / 2

        current_pos = 2
        for i, lane_x in enumerate(LANE_POSITIONS):
            if abs(enemy_center_x - lane_x) < 60:
                current_pos = i
                break

        # Обгон
        if enemy_y >= player_y - 30:
            if current_pos != self.player_position_index:
                self.move_car_to_position(self.enemy, self.player_position_index)

        # Уклонение от препятствий
        danger_zone = 200
        pos_danger = {0: False, 1: False, 2: False, 3: False, 4: False, 5: False}

        for obs in self.obstacles:
            if obs["y"] > enemy_y - danger_zone and obs["y"] < enemy_y + 50:
                pos_danger[obs["lane"]] = True

        if pos_danger[current_pos]:
            safe_positions = [p for p in range(6) if not pos_danger[p]]
            if safe_positions:
                new_pos = min(safe_positions, key=lambda p: abs(p - current_pos))
                if new_pos != current_pos:
                    self.move_car_to_position(self.enemy, new_pos)

    def check_collision(self, car, obstacles_list):
        car_coords = self.get_car_coords(car)
        if not car_coords:
            return False

        for obs in obstacles_list:
            obs_coords = self.canvas.coords(obs["id"])
            if obs_coords:
                if not (car_coords[2] < obs_coords[0] or
                        car_coords[0] > obs_coords[2] or
                        car_coords[3] < obs_coords[1] or
                        car_coords[1] > obs_coords[3]):
                    return True
        return False

    def load_best(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f).get("best_time")
            except:
                pass
        return None

    def save_best(self, current):
        best = self.load_best()
        if best is None or current < best:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump({"best_time": current}, f, ensure_ascii=False)
            return True
        return False

    def show_finish_window(self, victory, race_time):
        finish_window = tk.Toplevel(self.root)
        finish_window.title("Результат гонки")
        finish_window.geometry(f"{WIDTH}x{HEIGHT}")
        finish_window.state("zoomed")
        finish_window.configure(bg="#1a1a2e")
        finish_window.transient(self.root)
        finish_window.grab_set()

        center_frame = tk.Frame(finish_window, bg="#1a1a2e")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        if victory:
            title = "ПОБЕДА!"
            title_color = "#00FF00"
            message = "Вы финишировали первым!"
        else:
            title = "ПОРАЖЕНИЕ!"
            title_color = "#FF0000"
            message = "Соперник финишировал первым!"

        tk.Label(
            center_frame,
            text=title,
            font=("Arial", 80, "bold"),
            fg=title_color,
            bg="#1a1a2e"
        ).pack(pady=50)

        tk.Label(
            center_frame,
            text=message,
            font=("Arial", 40, "bold"),
            fg="white",
            bg="#1a1a2e"
        ).pack(pady=30)

        tk.Label(
            center_frame,
            text=f"Ваше время: {race_time:.2f} сек",
            font=("Arial", 36),
            fg="yellow",
            bg="#1a1a2e"
        ).pack(pady=20)

        best = self.load_best()
        if best:
            if victory and race_time < best:
                tk.Label(
                    center_frame,
                    text="★ НОВЫЙ РЕКОРД! ★",
                    font=("Arial", 32, "bold"),
                    fg="#FFD700",
                    bg="#1a1a2e"
                ).pack(pady=20)
            else:
                tk.Label(
                    center_frame,
                    text=f"Рекорд: {best:.2f} сек",
                    font=("Arial", 28),
                    fg="#FFD700",
                    bg="#1a1a2e"
                ).pack(pady=20)

        tk.Button(
            center_frame,
            text="ПОПРОБОВАТЬ СНОВА",
            font=("Arial", 28, "bold"),
            bg="green",
            fg="white",
            width=20,
            cursor="hand2",
            command=lambda: self.restart_game(finish_window)
        ).pack(pady=30)

        tk.Button(
            center_frame,
            text="ГЛАВНОЕ МЕНЮ",
            font=("Arial", 28, "bold"),
            bg="orange",
            fg="white",
            width=20,
            cursor="hand2",
            command=lambda: self.exit_to_menu_from_window(finish_window)
        ).pack(pady=15)

        finish_window.bind("<Escape>", lambda e: self.exit_to_menu_from_window(finish_window))
        finish_window.focus_set()

    def check_finish(self):
        """Проверка достижения Y = 100 - ФИНИШ"""
        if self.finished or not self.race_started:
            return

        player_coords = self.get_car_coords(self.player)
        enemy_coords = self.get_car_coords(self.enemy)

        player_finished = False
        enemy_finished = False

        if player_coords and player_coords[1] <= self.finish_line_y:
            player_finished = True

        if enemy_coords and enemy_coords[1] <= self.finish_line_y:
            enemy_finished = True

        if player_finished or enemy_finished:
            self.finished = True
            self.race_started = False
            self.finish_time = time.time() - self.start_time
            self.game_speed = 0

            if player_finished and not enemy_finished:
                self.save_best(self.finish_time)
                self.show_finish_window(True, self.finish_time)
            elif enemy_finished and not player_finished:
                self.show_finish_window(False, self.finish_time)
            else:
                if player_coords and enemy_coords:
                    if player_coords[1] <= enemy_coords[1]:
                        self.save_best(self.finish_time)
                        self.show_finish_window(True, self.finish_time)
                    else:
                        self.show_finish_window(False, self.finish_time)

    def show_game_over_window(self):
        game_over_window = tk.Toplevel(self.root)
        game_over_window.title("Поражение")
        game_over_window.geometry(f"{WIDTH}x{HEIGHT}")
        game_over_window.state("zoomed")
        game_over_window.configure(bg="#1a1a2e")
        game_over_window.transient(self.root)
        game_over_window.grab_set()

        center_frame = tk.Frame(game_over_window, bg="#1a1a2e")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            center_frame,
            text="ПОРАЖЕНИЕ!",
            font=("Arial", 80, "bold"),
            fg="red",
            bg="#1a1a2e"
        ).pack(pady=50)

        race_time = time.time() - self.start_time
        tk.Label(
            center_frame,
            text=f"Вы врезались в препятствие!\nВремя: {race_time:.2f} сек",
            font=("Arial", 36),
            fg="white",
            bg="#1a1a2e"
        ).pack(pady=30)

        tk.Button(
            center_frame,
            text="ПОПРОБОВАТЬ СНОВА",
            font=("Arial", 28, "bold"),
            bg="green",
            fg="white",
            width=20,
            cursor="hand2",
            command=lambda: self.restart_game(game_over_window)
        ).pack(pady=30)

        tk.Button(
            center_frame,
            text="ГЛАВНОЕ МЕНЮ",
            font=("Arial", 28, "bold"),
            bg="orange",
            fg="white",
            width=20,
            cursor="hand2",
            command=lambda: self.exit_to_menu_from_window(game_over_window)
        ).pack(pady=15)

        game_over_window.bind("<Escape>", lambda e: self.exit_to_menu_from_window(game_over_window))
        game_over_window.focus_set()

    def restart_game(self, window):
        window.destroy()
        self.game_over = False
        self.finished = False

        if hasattr(self, 'game_frame'):
            self.game_frame.destroy()

        self.start_game()

    def exit_to_menu_from_window(self, window):
        window.destroy()
        self.game_over = False
        self.finished = False

        if hasattr(self, 'game_frame'):
            self.game_frame.destroy()

        self.menu_frame.pack(fill="both", expand=True)
        self.show_menu()

    def key_press(self, event):
        key = event.keysym

        if self.race_started and not self.game_over and not self.finished:
            if key == 'Up':
                self.key_up = True
            elif key == 'Down':
                self.key_down = True
            elif key == 'Left':
                self.key_left = True
            elif key == 'Right':
                self.key_right = True

    def key_release(self, event):
        key = event.keysym

        if key == 'Up':
            self.key_up = False
        elif key == 'Down':
            self.key_down = False
        elif key == 'Left':
            self.key_left = False
        elif key == 'Right':
            self.key_right = False

    def pause(self, event=None):
        if self.race_started and not self.game_over and not self.finished:
            self.paused = not self.paused

    def exit_to_menu(self):
        self.game_over = True
        self.finished = True

        self.root.unbind("<KeyPress>")
        self.root.unbind("<KeyRelease>")
        self.root.unbind("<space>")
        self.root.unbind("<Escape>")

        if hasattr(self, 'game_frame'):
            self.game_frame.destroy()

        self.menu_frame.pack(fill="both", expand=True)
        self.show_menu()

    def update(self):
        if self.game_over or self.finished or not self.race_started:
            return

        if not self.paused:

            # Управление скоростью
            if self.key_up:
                self.game_speed = min(15, self.game_speed + 0.2)
            if self.key_down:
                self.game_speed = max(2, self.game_speed - 0.2)

            # Управление поворотами
            if self.key_left and self.player_position_index > 0:
                self.player_position_index -= 1
                self.move_car_to_position(self.player, self.player_position_index)
                self.root.after(80, lambda: None)
            if self.key_right and self.player_position_index < 5:
                self.player_position_index += 1
                self.move_car_to_position(self.player, self.player_position_index)
                self.root.after(80, lambda: None)

            # Обновление расстояния
            self.player_distance += self.game_speed
            self.enemy_distance += self.game_speed

            # Движение линий разметки
            for line in self.lines:
                self.canvas.move(line, 0, self.game_speed)
                coords = self.canvas.coords(line)
                if coords and coords[1] > HEIGHT:
                    self.canvas.coords(line, ROAD_CENTER - 5, -80, ROAD_CENTER + 5, -40)

            # Движение препятствий
            for obs in self.obstacles[:]:
                self.canvas.move(obs["id"], 0, self.game_speed)
                obs["y"] += self.game_speed

                if obs["y"] > HEIGHT + 200:
                    self.canvas.delete(obs["id"])
                    self.obstacles.remove(obs)

            # Движение противника
            self.update_enemy_ai()

            # Проверка столкновения
            if self.check_collision(self.player, self.obstacles):
                self.game_over = True
                self.race_started = False
                self.show_game_over_window()
                return

            # Появление финишной линии
            remaining = self.total_distance - self.player_distance
            if remaining <= 500 and not self.finish_visible:
                self.spawn_finish_line()

            # Движение финишной линии
            if self.finish_visible and self.finish_line:
                for item in self.finish_line:
                    self.canvas.move(item, 0, self.game_speed)

            # Проверка финиша
            self.check_finish()

            # Обновление UI
            player_coords = self.get_car_coords(self.player)
            enemy_coords = self.get_car_coords(self.enemy)

            if player_coords and enemy_coords:
                if player_coords[1] < enemy_coords[1]:
                    place = "1/2"
                    place_color = "#00FF00"
                else:
                    place = "2/2"
                    place_color = "#FFA500"
            else:
                place = "?/2"
                place_color = "#FFFFFF"

            race_time = time.time() - self.start_time
            speed_kmh = int(self.game_speed * 12)
            best = self.load_best()
            remaining_m = int((self.total_distance - self.player_distance) / 10)

            txt = f"МЕСТО: {place}   |   ВРЕМЯ: {race_time:.2f} сек   |   СКОРОСТЬ: {speed_kmh} км/ч   |   ДО ФИНИША: {remaining_m} м"
            if best:
                txt += f"   |   РЕКОРД: {best:.2f} сек"

            self.info.config(text=txt, fg=place_color)

            # Прогресс-бар
            self.canvas.delete("progress")
            progress_width = 400
            progress = min(1.0, self.player_distance / self.total_distance)
            bar_x = WIDTH // 2 - progress_width // 2
            self.canvas.create_rectangle(bar_x, 20, bar_x + progress_width, 35, fill="#444", outline="white",
                                         tags="progress")
            self.canvas.create_rectangle(bar_x, 20, bar_x + progress_width * progress, 35, fill="#00FF00", outline="",
                                         tags="progress")

        self.root.after(16, self.update)


if __name__ == "__main__":
    root = tk.Tk()
    game = RacingGame(root)
    root.mainloop()