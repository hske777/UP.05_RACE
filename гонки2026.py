import tkinter as tk
from tkinter import messagebox
import random
import time
import json
import os
import math

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

# ФИКСИРОВАННЫЕ ПРЕПЯТСТВИЯ ДЛЯ ГОРОДСКОЙ ТРАССЫ
CITY_OBSTACLES = [
    (2, -400, "cone"), (4, -700, "cone"), (1, -1100, "box"),
    (3, -1500, "cone"), (0, -1900, "box"), (5, -2300, "cone"),
    (2, -2700, "box"), (4, -3100, "cone"), (1, -3500, "box"),
    (3, -3900, "cone"), (5, -4300, "box"), (0, -4700, "cone"),
    (2, -5100, "box"), (4, -5500, "cone"), (1, -5900, "box"),
]

SAVE_FILE_FOREST = "record_forest.json"
SAVE_FILE_CITY = "record_city.json"


class RacingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Гонки")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.state("zoomed")

        self.current_track = None
        self.menu_frame = tk.Frame(root, bg="black")
        self.menu_frame.pack(fill="both", expand=True)

        self.show_menu()

    def show_menu(self):
        for w in self.menu_frame.winfo_children():
            w.destroy()

        menu_canvas = tk.Canvas(self.menu_frame, width=WIDTH, height=HEIGHT, bg="black", highlightthickness=0)
        menu_canvas.pack(fill="both", expand=True)

        menu_canvas.create_text(
            WIDTH // 2, 200,
            text="ГОНКИ",
            font=("Arial", 80, "bold"),
            fill="red"
        )

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

        menu_canvas.create_text(
            WIDTH // 2, 600,
            text="Управление: ↑/↓ - скорость | ←/→ - поворот | ESC - выход в главное меню",
            font=("Arial", 20),
            fill="gray"
        )

        for _ in range(100):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            menu_canvas.create_oval(x, y, x + 2, y + 2, fill="white", outline="")

    def show_track_selection(self):
        self.menu_frame.pack_forget()

        self.track_window = tk.Toplevel(self.root)
        self.track_window.title("Выбор трассы")
        self.track_window.geometry(f"{WIDTH}x{HEIGHT}")
        self.track_window.state("zoomed")
        self.track_window.configure(bg="black")
        self.track_window.transient(self.root)
        self.track_window.grab_set()

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

        # Лесная трасса
        forest_x = WIDTH // 2 - 550
        forest_y = 300
        forest_width = 500
        forest_height = 450

        track_canvas.create_rectangle(
            forest_x, forest_y, forest_x + forest_width, forest_y + forest_height,
            fill="#228B22", outline="white", width=5
        )

        track_canvas.create_text(
            forest_x + forest_width // 2, forest_y + 150,
            text="🌲",
            font=("Arial", 100)
        )

        track_canvas.create_text(
            forest_x + forest_width // 2, forest_y + 250,
            text="ЛЕСНАЯ ТРАССА",
            font=("Arial", 28, "bold"),
            fill="white"
        )

        # Рекорд лесной трассы
        forest_best = self.load_best("forest")
        if forest_best:
            track_canvas.create_text(
                forest_x + forest_width // 2, forest_y + 320,
                text=f"Рекорд: {forest_best:.2f} сек",
                font=("Arial", 20),
                fill="#FFD700"
            )
        else:
            track_canvas.create_text(
                forest_x + forest_width // 2, forest_y + 320,
                text="Рекорд: ---",
                font=("Arial", 20),
                fill="#FFD700"
            )

        select_btn_forest = tk.Button(
            self.track_window,
            text="ВЫБРАТЬ",
            font=("Arial", 24, "bold"),
            bg="green",
            fg="white",
            width=15,
            cursor="hand2",
            command=lambda: self.select_track("forest")
        )
        select_btn_forest.place(x=forest_x + 150, y=forest_y + 370, width=200, height=50)

        # Городская трасса
        city_x = WIDTH // 2 + 50
        city_y = 300
        city_width = 500
        city_height = 450

        track_canvas.create_rectangle(
            city_x, city_y, city_x + city_width, city_y + city_height,
            fill="#808080", outline="white", width=5
        )

        track_canvas.create_text(
            city_x + city_width // 2, city_y + 150,
            text="🏙️",
            font=("Arial", 100)
        )

        track_canvas.create_text(
            city_x + city_width // 2, city_y + 250,
            text="ГОРОДСКАЯ ТРАССА",
            font=("Arial", 28, "bold"),
            fill="white"
        )

        # Рекорд городской трассы
        city_best = self.load_best("city")
        if city_best:
            track_canvas.create_text(
                city_x + city_width // 2, city_y + 320,
                text=f"Рекорд: {city_best:.2f} сек",
                font=("Arial", 20),
                fill="#FFD700"
            )
        else:
            track_canvas.create_text(
                city_x + city_width // 2, city_y + 320,
                text="Рекорд: ---",
                font=("Arial", 20),
                fill="#FFD700"
            )

        select_btn_city = tk.Button(
            self.track_window,
            text="ВЫБРАТЬ",
            font=("Arial", 24, "bold"),
            bg="blue",
            fg="white",
            width=15,
            cursor="hand2",
            command=lambda: self.select_track("city")
        )
        select_btn_city.place(x=city_x + 150, y=city_y + 370, width=200, height=50)

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
        menu_btn.place(x=WIDTH // 2 - 150, y=800, width=300, height=60)

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

        # Выбор цвета фона в зависимости от трассы
        if self.current_track == "forest":
            bg_color = "#1a3a1a"  # Темно-зеленый для лесной трассы
        elif self.current_track == "city":
            bg_color = "#2a2a3a"  # Темно-синий/серый для городской трассы
        else:
            bg_color = "#1a1a2e"  # Стандартный цвет

        self.canvas = tk.Canvas(
            self.game_frame,
            width=WIDTH,
            height=HEIGHT - 50,
            bg=bg_color
        )
        self.canvas.pack()

        self.paused = False
        self.game_over = False
        self.finished = False
        self.race_started = False

        self.game_speed = 5  # начальная скорость игрока
        self.player_position_index = 2

        self.player_distance = 0
        self.total_distance = 7000

        self.key_up = False
        self.key_down = False
        self.key_left = False
        self.key_right = False

        self.obstacles = []

        self.start_time = 0
        self.finish_time = 0

        self.draw_road()

        # Y-ПОЗИЦИЯ ДЛЯ МАШИНЫ
        player_y_position = HEIGHT - 150

        self.player = self.create_car(LANE_POSITIONS[self.player_position_index], player_y_position, "#3366FF")

        self.obstacles = []
        if self.current_track == "forest":
            for lane, y_pos, obs_type in FOREST_OBSTACLES:
                self.spawn_fixed_obstacle(lane, y_pos, obs_type)
        elif self.current_track == "city":
            for lane, y_pos, obs_type in CITY_OBSTACLES:
                self.spawn_fixed_obstacle(lane, y_pos, obs_type)

        # Добавляем городские декорации (здания) для городской трассы
        self.buildings = []
        if self.current_track == "city":
            self.spawn_city_buildings()

        self.lines = []
        for y in range(0, HEIGHT + 200, 80):
            line = self.canvas.create_rectangle(
                ROAD_CENTER - 5, y,
                ROAD_CENTER + 5, y + 40,
                fill="white"
            )
            self.lines.append(line)

        self.finish_line_y = 100
        self.finish_line = None
        self.finish_visible = False
        self.finish_triggered = False

        self.root.bind("<KeyPress>", self.key_press)
        self.root.bind("<KeyRelease>", self.key_release)
        self.root.bind("<space>", self.pause)
        self.root.bind("<Escape>", lambda e: self.exit_to_menu())

        self.root.focus_set()

        self.countdown()

    def check_building_collision(self, x, y, width, height, existing_buildings, side):
        """Проверяет, не пересекается ли новое здание с существующими"""
        for building in existing_buildings:
            # Проверяем пересечение прямоугольников
            if (x < building["x"] + building["width"] + 20 and
                    x + width + 20 > building["x"] and
                    y < building["y"] + building["height"] + 30 and
                    y + height + 30 > building["y"]):
                return True
        return False

    def spawn_city_buildings(self):
        """Создает городские здания по бокам дороги на безопасном расстоянии"""

        # Параметры отступов
        left_area_start = 30  # Начало левой зоны
        left_area_end = ROAD_LEFT - 60  # Конец левой зоны (отступ от дороги)

        right_area_start = ROAD_RIGHT + 60  # Начало правой зоны (отступ от дороги)
        right_area_end = WIDTH - 100  # Конец правой зоны

        left_buildings = []
        right_buildings = []

        # Генерируем здания слева
        for i in range(12):
            max_attempts = 50
            for attempt in range(max_attempts):
                width = random.randint(70, 140)
                height = random.randint(130, 250)

                # X координата в безопасной зоне слева
                x = random.randint(left_area_start, left_area_end - width)

                # Y координата (разбрасываем по всей высоте)
                y = random.randint(-HEIGHT, HEIGHT + 500)

                # Проверяем пересечение с другими зданиями слева
                if not self.check_building_collision(x, y, width, height, left_buildings, "left"):
                    # Создаем здание
                    building_color = random.choice(["#4a4a4a", "#5a5a5a", "#6a6a6a", "#3a3a3a", "#585858", "#707070"])

                    # Основное здание
                    building = self.canvas.create_rectangle(
                        x, y, x + width, y + height,
                        fill=building_color,
                        outline="#888888",
                        width=2,
                        tags="building"
                    )

                    # Окна
                    windows = []
                    window_size = 15
                    window_spacing = 22

                    for wx in range(x + 12, x + width - 12, window_spacing):
                        for wy in range(y + 15, y + height - 15, window_spacing):
                            # Пропускаем окна, которые могут вылезти за пределы
                            if wx + window_size <= x + width - 5 and wy + window_size <= y + height - 5:
                                window_color = random.choice(["#ffffaa", "#ffcc66", "#ffaa66", "#ffee88"])
                                window = self.canvas.create_rectangle(
                                    wx, wy, wx + window_size, wy + window_size,
                                    fill=window_color,
                                    outline="#ccccaa",
                                    width=1,
                                    tags="building"
                                )
                                windows.append(window)

                    left_buildings.append({
                        "id": building,
                        "windows": windows,
                        "x": x,
                        "y": y,
                        "width": width,
                        "height": height
                    })
                    break

        # Генерируем здания справа
        for i in range(12):
            max_attempts = 50
            for attempt in range(max_attempts):
                width = random.randint(70, 140)
                height = random.randint(130, 250)

                # X координата в безопасной зоне справа
                x = random.randint(right_area_start, right_area_end - width)

                # Y координата (разбрасываем по всей высоте)
                y = random.randint(-HEIGHT, HEIGHT + 500)

                # Проверяем пересечение с другими зданиями справа
                if not self.check_building_collision(x, y, width, height, right_buildings, "right"):
                    # Создаем здание
                    building_color = random.choice(["#4a4a4a", "#5a5a5a", "#6a6a6a", "#3a3a3a", "#585858", "#707070"])

                    # Основное здание
                    building = self.canvas.create_rectangle(
                        x, y, x + width, y + height,
                        fill=building_color,
                        outline="#888888",
                        width=2,
                        tags="building"
                    )

                    # Окна
                    windows = []
                    window_size = 15
                    window_spacing = 22

                    for wx in range(x + 12, x + width - 12, window_spacing):
                        for wy in range(y + 15, y + height - 15, window_spacing):
                            # Пропускаем окна, которые могут вылезти за пределы
                            if wx + window_size <= x + width - 5 and wy + window_size <= y + height - 5:
                                window_color = random.choice(["#ffffaa", "#ffcc66", "#ffaa66", "#ffee88"])
                                window = self.canvas.create_rectangle(
                                    wx, wy, wx + window_size, wy + window_size,
                                    fill=window_color,
                                    outline="#ccccaa",
                                    width=1,
                                    tags="building"
                                )
                                windows.append(window)

                    right_buildings.append({
                        "id": building,
                        "windows": windows,
                        "x": x,
                        "y": y,
                        "width": width,
                        "height": height
                    })
                    break

        # Объединяем оба списка
        self.buildings = left_buildings + right_buildings

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
        # Выбор цвета обочин в зависимости от трассы
        if self.current_track == "forest":
            roadside_color = "#1a5c1a"  # Темно-зеленый для леса
        elif self.current_track == "city":
            roadside_color = "#3a3a4a"  # Темно-серый для города
        else:
            roadside_color = "#228B22"

        self.canvas.create_rectangle(
            ROAD_LEFT, 0, ROAD_RIGHT, HEIGHT,
            fill="#333333", outline=""
        )
        self.canvas.create_line(ROAD_LEFT, 0, ROAD_LEFT, HEIGHT, fill="yellow", width=5)
        self.canvas.create_line(ROAD_RIGHT, 0, ROAD_RIGHT, HEIGHT, fill="yellow", width=5)
        self.canvas.create_rectangle(0, 0, ROAD_LEFT, HEIGHT, fill=roadside_color, outline="")
        self.canvas.create_rectangle(ROAD_RIGHT, 0, WIDTH, HEIGHT, fill=roadside_color, outline="")

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
        elif obs_type == "cone":
            color = "#FF6600"
            w, h = 18, 25
        elif obs_type == "box":
            color = "#8B6914"
            w, h = 25, 25
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

    def load_best(self, track_name):
        if track_name == "forest":
            save_file = SAVE_FILE_FOREST
        else:
            save_file = SAVE_FILE_CITY

        if os.path.exists(save_file):
            try:
                with open(save_file, "r", encoding="utf-8") as f:
                    return json.load(f).get("best_time")
            except:
                pass
        return None

    def save_best(self, current):
        if self.current_track == "forest":
            save_file = SAVE_FILE_FOREST
        else:
            save_file = SAVE_FILE_CITY

        best = self.load_best(self.current_track)
        if best is None or current < best:
            with open(save_file, "w", encoding="utf-8") as f:
                json.dump({"best_time": current}, f, ensure_ascii=False)
            return True
        return False

    def show_finish_window(self, race_time, is_new_record=False):
        finish_window = tk.Toplevel(self.root)
        finish_window.title("Победа!")
        finish_window.geometry(f"{WIDTH}x{HEIGHT}")
        finish_window.state("zoomed")
        finish_window.configure(bg="#1a1a2e")
        finish_window.transient(self.root)
        finish_window.grab_set()

        center_frame = tk.Frame(finish_window, bg="#1a1a2e")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            center_frame,
            text="ФИНИШ!",
            font=("Arial", 80, "bold"),
            fg="#00FF00",
            bg="#1a1a2e"
        ).pack(pady=50)

        tk.Label(
            center_frame,
            text=f"Ваше время: {race_time:.2f} сек",
            font=("Arial", 48),
            fg="yellow",
            bg="#1a1a2e"
        ).pack(pady=30)

        best = self.load_best(self.current_track)
        if best:
            if is_new_record:
                tk.Label(
                    center_frame,
                    text="★ НОВЫЙ РЕКОРД! ★",
                    font=("Arial", 36, "bold"),
                    fg="#FFD700",
                    bg="#1a1a2e"
                ).pack(pady=20)
            else:
                tk.Label(
                    center_frame,
                    text=f"Рекорд трассы: {best:.2f} сек",
                    font=("Arial", 32),
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

    def check_finish_by_distance(self):
        """Проверка достижения финиша"""
        if self.finished or not self.race_started or self.finish_triggered:
            return

        # Проверяем для игрока
        player_remaining = self.total_distance - self.player_distance

        # Если игрок достиг финиша
        if player_remaining <= -10:
            self.finish_triggered = True
            self.finished = True
            self.race_started = False
            self.game_speed = 0
            self.finish_time = time.time() - self.start_time
            is_new_record = self.save_best(self.finish_time)
            self.show_finish_window(self.finish_time, is_new_record)

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
            text="АВАРИЯ!",
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
        self.finish_triggered = False

        if hasattr(self, 'game_frame'):
            self.game_frame.destroy()

        self.start_game()

    def exit_to_menu_from_window(self, window):
        window.destroy()
        self.game_over = False
        self.finished = False
        self.finish_triggered = False

        if hasattr(self, 'game_frame'):
            self.game_frame.destroy()

        self.menu_frame.pack(fill="both", expand=True)
        self.show_menu()

    def key_press(self, event):
        key = event.keysym

        if hasattr(self, 'race_started') and self.race_started and not self.game_over and not self.finished:
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
        if hasattr(self, 'race_started') and self.race_started and not self.game_over and not self.finished:
            self.paused = not self.paused

    def exit_to_menu(self):
        self.game_over = True
        self.finished = True
        self.finish_triggered = True

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

            # Управление скоростью игрока
            if self.key_up:
                self.game_speed = min(15, self.game_speed + 0.2)
            if self.key_down:
                self.game_speed = max(2, self.game_speed - 0.2)

            # Управление поворотами игрока
            if self.key_left and self.player_position_index > 0:
                self.player_position_index -= 1
                self.move_car_to_position(self.player, self.player_position_index)
                self.root.after(80, lambda: None)
            if self.key_right and self.player_position_index < 5:
                self.player_position_index += 1
                self.move_car_to_position(self.player, self.player_position_index)
                self.root.after(80, lambda: None)

            # Обновление расстояния
            if not self.finished:
                self.player_distance += self.game_speed

            # Движение линий разметки
            scroll_speed = self.game_speed
            for line in self.lines:
                self.canvas.move(line, 0, scroll_speed)
                coords = self.canvas.coords(line)
                if coords and coords[1] > HEIGHT:
                    self.canvas.coords(line, ROAD_CENTER - 5, -80, ROAD_CENTER + 5, -40)

            # Движение городских зданий
            if hasattr(self, 'buildings'):
                for building in self.buildings:
                    self.canvas.move(building["id"], 0, scroll_speed)
                    for window in building["windows"]:
                        self.canvas.move(window, 0, scroll_speed)

                    building["y"] += scroll_speed

                    coords = self.canvas.coords(building["id"])
                    if coords and coords[1] > HEIGHT + 300:
                        new_y = -building["height"] - random.randint(0, 500)
                        dy = new_y - building["y"]
                        self.canvas.move(building["id"], 0, dy)
                        for window in building["windows"]:
                            self.canvas.move(window, 0, dy)
                        building["y"] = new_y

            # Движение препятствий
            for obs in self.obstacles[:]:
                self.canvas.move(obs["id"], 0, scroll_speed)
                obs["y"] += scroll_speed

                if obs["y"] > HEIGHT + 200:
                    self.canvas.delete(obs["id"])
                    self.obstacles.remove(obs)

            # Проверка столкновений
            if not self.finished and self.check_collision(self.player, self.obstacles):
                self.game_over = True
                self.race_started = False
                self.show_game_over_window()
                return

            # Финишная линия
            remaining = self.total_distance - self.player_distance
            if remaining <= 500 and not self.finish_visible:
                self.spawn_finish_line()

            if not self.finished and self.finish_visible and self.finish_line:
                for item in self.finish_line:
                    self.canvas.move(item, 0, scroll_speed)

            self.check_finish_by_distance()

            # Обновление UI
            if not self.finished:
                race_time = time.time() - self.start_time
                speed_kmh = int(self.game_speed * 12)
                best = self.load_best(self.current_track)
                remaining_m = max(-10, int((self.total_distance - self.player_distance) / 10))

                txt = f"ВРЕМЯ: {race_time:.2f} сек   |   СКОРОСТЬ: {speed_kmh} км/ч   |   ДО ФИНИША: {remaining_m} м"
                if best:
                    txt += f"   |   РЕКОРД: {best:.2f} сек"

                self.info.config(text=txt, fg="white")

                # Прогресс-бар
                self.canvas.delete("progress")
                progress_width = 400
                player_progress = min(1.0, self.player_distance / self.total_distance)
                bar_x = WIDTH // 2 - progress_width // 2

                # Прогресс игрока (синий)
                self.canvas.create_rectangle(bar_x, 20, bar_x + progress_width, 35, fill="#444", outline="white",
                                             tags="progress")
                self.canvas.create_rectangle(bar_x, 20, bar_x + progress_width * player_progress, 35, fill="#3366FF",
                                             outline="", tags="progress")

        self.root.after(16, self.update)


if __name__ == "__main__":
    root = tk.Tk()
    game = RacingGame(root)
    root.mainloop()