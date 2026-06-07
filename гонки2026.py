import tkinter as tk
from tkinter import messagebox
import random
import time
import json
import os
import math


class RacingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Гонки")

        # Получаем размер экрана
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Устанавливаем окно на весь экран
        self.root.geometry(f"{self.screen_width}x{self.screen_height}")
        self.root.state("zoomed")

        # Пропорциональные размеры (относительно базового разрешения 1920x1080)
        self.base_width = 1920
        self.base_height = 1080

        # Коэффициенты масштабирования
        self.scale_x = self.screen_width / self.base_width
        self.scale_y = self.screen_height / self.base_height

        # Масштабируем все координаты
        self.WIDTH = self.screen_width
        self.HEIGHT = self.screen_height

        # Масштабируем дорогу
        self.ROAD_LEFT = int(760 * self.scale_x)
        self.ROAD_RIGHT = int(1160 * self.scale_x)
        self.ROAD_CENTER = (self.ROAD_LEFT + self.ROAD_RIGHT) // 2

        # Масштабируем позиции полос
        self.LANE_POSITIONS = [
            self.ROAD_LEFT + int(50 * self.scale_x),
            self.ROAD_LEFT + int(150 * self.scale_x),
            self.ROAD_CENTER - int(50 * self.scale_x),
            self.ROAD_CENTER + int(50 * self.scale_x),
            self.ROAD_RIGHT - int(150 * self.scale_x),
            self.ROAD_RIGHT - int(50 * self.scale_x)
        ]

        # Масштабируем фиксированные препятствия
        self.FOREST_OBSTACLES = self.scale_obstacles([
            (1, -500, "tree"), (2, -800, "rock"), (4, -1200, "tree"),
            (0, -1600, "rock"), (3, -2000, "tree"), (5, -2500, "block"),
            (2, -3000, "tree"), (4, -3500, "rock"), (1, -4000, "tree"),
            (3, -4500, "block"), (0, -5000, "tree"), (5, -5500, "rock"),
        ])

        self.CITY_OBSTACLES = self.scale_obstacles([
            (2, -400, "cone"), (4, -700, "cone"), (1, -1100, "box"),
            (3, -1500, "cone"), (0, -1900, "box"), (5, -2300, "cone"),
            (2, -2700, "box"), (4, -3100, "cone"), (1, -3500, "box"),
            (3, -3900, "cone"), (5, -4300, "box"), (0, -4700, "cone"),
            (2, -5100, "box"), (4, -5500, "cone"), (1, -5900, "box"),
        ])

        self.SAVE_FILE_FOREST = "record_forest.json"
        self.SAVE_FILE_CITY = "record_city.json"

        self.current_track = None
        self.menu_frame = tk.Frame(root, bg="black")
        self.menu_frame.pack(fill="both", expand=True)

        # Обновляем bind для изменения размера окна
        self.root.bind("<Configure>", self.on_window_resize)

        self.show_menu()

    def scale_obstacles(self, obstacles):
        """Масштабирует координаты препятствий"""
        scaled = []
        for lane, y_pos, obs_type in obstacles:
            scaled_y = int(y_pos * self.scale_y)
            scaled.append((lane, scaled_y, obs_type))
        return scaled

    def scale_finish_line_y(self):
        """Масштабирует позицию финишной линии"""
        return int(100 * self.scale_y)

    def on_window_resize(self, event):
        """Обработчик изменения размера окна"""
        if event.widget == self.root:
            # Обновляем размеры
            self.WIDTH = event.width
            self.HEIGHT = event.height
            self.scale_x = self.WIDTH / self.base_width
            self.scale_y = self.HEIGHT / self.base_height

            # Пересчитываем координаты дороги
            self.ROAD_LEFT = int(760 * self.scale_x)
            self.ROAD_RIGHT = int(1160 * self.scale_x)
            self.ROAD_CENTER = (self.ROAD_LEFT + self.ROAD_RIGHT) // 2

            # Пересчитываем позиции полос
            self.LANE_POSITIONS = [
                self.ROAD_LEFT + int(50 * self.scale_x),
                self.ROAD_LEFT + int(150 * self.scale_x),
                self.ROAD_CENTER - int(50 * self.scale_x),
                self.ROAD_CENTER + int(50 * self.scale_x),
                self.ROAD_RIGHT - int(150 * self.scale_x),
                self.ROAD_RIGHT - int(50 * self.scale_x)
            ]

            # Пересоздаем игру, если она запущена
            if hasattr(self, 'race_started') and self.race_started:
                self.restart_game_on_resize()

    def restart_game_on_resize(self):
        """Перезапускает игру при изменении размера окна"""
        if hasattr(self, 'game_frame') and self.game_frame.winfo_exists():
            self.game_over = True
            self.finished = True
            if hasattr(self, 'game_frame'):
                self.game_frame.destroy()
            self.start_game()

    def show_menu(self):
        for w in self.menu_frame.winfo_children():
            w.destroy()

        menu_canvas = tk.Canvas(self.menu_frame, width=self.WIDTH, height=self.HEIGHT, bg="black", highlightthickness=0)
        menu_canvas.pack(fill="both", expand=True)

        # Масштабируем размеры шрифтов и отступов
        title_font_size = int(80 * min(self.scale_x, self.scale_y))
        btn_font_size = int(24 * min(self.scale_x, self.scale_y))
        text_font_size = int(20 * min(self.scale_x, self.scale_y))

        menu_canvas.create_text(
            self.WIDTH // 2, int(200 * self.scale_y),
            text="ГОНКИ",
            font=("Arial", title_font_size, "bold"),
            fill="red"
        )

        btn_width = int(300 * self.scale_x)
        btn_height = int(60 * self.scale_y)

        btn_bg = tk.Frame(self.menu_frame, bg="black")
        btn_bg.place(x=self.WIDTH // 2 - btn_width // 2, y=int(400 * self.scale_y), width=btn_width, height=btn_height)

        select_btn = tk.Button(
            btn_bg,
            text="ВЫБОР ТРАССЫ",
            font=("Arial", btn_font_size, "bold"),
            bg="blue",
            fg="white",
            cursor="hand2",
            command=self.show_track_selection
        )
        select_btn.pack(fill="both", expand=True)

        btn_bg2 = tk.Frame(self.menu_frame, bg="black")
        btn_bg2.place(x=self.WIDTH // 2 - btn_width // 2, y=int(490 * self.scale_y), width=btn_width, height=btn_height)

        exit_btn = tk.Button(
            btn_bg2,
            text="ВЫХОД",
            font=("Arial", btn_font_size, "bold"),
            bg="red",
            fg="white",
            cursor="hand2",
            command=self.root.destroy
        )
        exit_btn.pack(fill="both", expand=True)

        menu_canvas.create_text(
            self.WIDTH // 2, int(600 * self.scale_y),
            text="Управление: ↑/↓ - скорость | ←/→ - поворот | ESC - выход в главное меню",
            font=("Arial", text_font_size),
            fill="gray"
        )

        # Звездное небо
        for _ in range(100):
            x = random.randint(0, self.WIDTH)
            y = random.randint(0, self.HEIGHT)
            menu_canvas.create_oval(x, y, x + 2, y + 2, fill="white", outline="")

    def show_track_selection(self):
        self.menu_frame.pack_forget()

        self.track_window = tk.Toplevel(self.root)
        self.track_window.title("Выбор трассы")
        self.track_window.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.track_window.state("zoomed")
        self.track_window.configure(bg="black")
        self.track_window.transient(self.root)
        self.track_window.grab_set()

        track_canvas = tk.Canvas(self.track_window, width=self.WIDTH, height=self.HEIGHT, bg="black",
                                 highlightthickness=0)
        track_canvas.pack(fill="both", expand=True)

        # Звездное небо
        for _ in range(100):
            x = random.randint(0, self.WIDTH)
            y = random.randint(0, self.HEIGHT)
            track_canvas.create_oval(x, y, x + 2, y + 2, fill="white", outline="")

        title_font_size = int(60 * min(self.scale_x, self.scale_y))
        track_canvas.create_text(
            self.WIDTH // 2, int(150 * self.scale_y),
            text="ВЫБОР ТРАССЫ",
            font=("Arial", title_font_size, "bold"),
            fill="yellow"
        )

        # Лесная трасса
        forest_width = int(500 * self.scale_x)
        forest_height = int(450 * self.scale_y)
        forest_x = self.WIDTH // 2 - forest_width - int(50 * self.scale_x)
        forest_y = int(300 * self.scale_y)

        track_canvas.create_rectangle(
            forest_x, forest_y, forest_x + forest_width, forest_y + forest_height,
            fill="#228B22", outline="white", width=int(5 * min(self.scale_x, self.scale_y))
        )

        emoji_font_size = int(100 * min(self.scale_x, self.scale_y))
        track_canvas.create_text(
            forest_x + forest_width // 2, forest_y + int(150 * self.scale_y),
            text="🌲",
            font=("Arial", emoji_font_size)
        )

        track_font_size = int(28 * min(self.scale_x, self.scale_y))
        track_canvas.create_text(
            forest_x + forest_width // 2, forest_y + int(250 * self.scale_y),
            text="ЛЕСНАЯ ТРАССА",
            font=("Arial", track_font_size, "bold"),
            fill="white"
        )

        # Рекорд лесной трассы
        record_font_size = int(20 * min(self.scale_x, self.scale_y))
        forest_best = self.load_best("forest")
        if forest_best:
            track_canvas.create_text(
                forest_x + forest_width // 2, forest_y + int(320 * self.scale_y),
                text=f"Рекорд: {forest_best:.2f} сек",
                font=("Arial", record_font_size),
                fill="#FFD700"
            )
        else:
            track_canvas.create_text(
                forest_x + forest_width // 2, forest_y + int(320 * self.scale_y),
                text="Рекорд: ---",
                font=("Arial", record_font_size),
                fill="#FFD700"
            )

        btn_width = int(200 * self.scale_x)
        btn_height = int(50 * self.scale_y)
        select_btn_forest = tk.Button(
            self.track_window,
            text="ВЫБРАТЬ",
            font=("Arial", int(24 * min(self.scale_x, self.scale_y)), "bold"),
            bg="green",
            fg="white",
            cursor="hand2",
            command=lambda: self.select_track("forest")
        )
        select_btn_forest.place(x=forest_x + forest_width // 2 - btn_width // 2,
                                y=forest_y + int(370 * self.scale_y),
                                width=btn_width, height=btn_height)

        # Городская трасса
        city_width = int(500 * self.scale_x)
        city_height = int(450 * self.scale_y)
        city_x = self.WIDTH // 2 + int(50 * self.scale_x)
        city_y = int(300 * self.scale_y)

        track_canvas.create_rectangle(
            city_x, city_y, city_x + city_width, city_y + city_height,
            fill="#808080", outline="white", width=int(5 * min(self.scale_x, self.scale_y))
        )

        track_canvas.create_text(
            city_x + city_width // 2, city_y + int(150 * self.scale_y),
            text="🏙️",
            font=("Arial", emoji_font_size)
        )

        track_canvas.create_text(
            city_x + city_width // 2, city_y + int(250 * self.scale_y),
            text="ГОРОДСКАЯ ТРАССА",
            font=("Arial", track_font_size, "bold"),
            fill="white"
        )

        # Рекорд городской трассы
        city_best = self.load_best("city")
        if city_best:
            track_canvas.create_text(
                city_x + city_width // 2, city_y + int(320 * self.scale_y),
                text=f"Рекорд: {city_best:.2f} сек",
                font=("Arial", record_font_size),
                fill="#FFD700"
            )
        else:
            track_canvas.create_text(
                city_x + city_width // 2, city_y + int(320 * self.scale_y),
                text="Рекорд: ---",
                font=("Arial", record_font_size),
                fill="#FFD700"
            )

        select_btn_city = tk.Button(
            self.track_window,
            text="ВЫБРАТЬ",
            font=("Arial", int(24 * min(self.scale_x, self.scale_y)), "bold"),
            bg="blue",
            fg="white",
            cursor="hand2",
            command=lambda: self.select_track("city")
        )
        select_btn_city.place(x=city_x + city_width // 2 - btn_width // 2,
                              y=city_y + int(370 * self.scale_y),
                              width=btn_width, height=btn_height)

        menu_btn_width = int(300 * self.scale_x)
        menu_btn_height = int(60 * self.scale_y)
        menu_btn = tk.Button(
            self.track_window,
            text="ГЛАВНОЕ МЕНЮ",
            font=("Arial", int(24 * min(self.scale_x, self.scale_y)), "bold"),
            bg="orange",
            fg="white",
            cursor="hand2",
            command=self.back_to_menu
        )
        menu_btn.place(x=self.WIDTH // 2 - menu_btn_width // 2,
                       y=int(800 * self.scale_y),
                       width=menu_btn_width, height=menu_btn_height)

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

        info_font_size = int(18 * min(self.scale_x, self.scale_y))
        self.info = tk.Label(self.game_frame, font=("Arial", info_font_size), bg="black", fg="white")
        self.info.pack(fill="x")

        # Выбор цвета фона в зависимости от трассы
        if self.current_track == "forest":
            bg_color = "#1a3a1a"
        elif self.current_track == "city":
            bg_color = "#2a2a3a"
        else:
            bg_color = "#1a1a2e"

        self.canvas = tk.Canvas(
            self.game_frame,
            width=self.WIDTH,
            height=self.HEIGHT - int(50 * self.scale_y),
            bg=bg_color
        )
        self.canvas.pack()

        self.paused = False
        self.game_over = False
        self.finished = False
        self.race_started = False

        self.game_speed = 5
        self.player_position_index = 2

        self.player_distance = 0
        self.total_distance = int(7000 * self.scale_y)

        self.key_up = False
        self.key_down = False
        self.key_left = False
        self.key_right = False

        self.obstacles = []

        self.start_time = 0
        self.finish_time = 0

        self.draw_road()

        # Y-ПОЗИЦИЯ ДЛЯ МАШИНЫ
        player_y_position = self.HEIGHT - int(150 * self.scale_y)

        self.player = self.create_car(self.LANE_POSITIONS[self.player_position_index], player_y_position, "#3366FF")

        self.obstacles = []
        if self.current_track == "forest":
            for lane, y_pos, obs_type in self.FOREST_OBSTACLES:
                self.spawn_fixed_obstacle(lane, y_pos, obs_type)
        elif self.current_track == "city":
            for lane, y_pos, obs_type in self.CITY_OBSTACLES:
                self.spawn_fixed_obstacle(lane, y_pos, obs_type)

        # Добавляем городские декорации для городской трассы
        self.buildings = []
        if self.current_track == "city":
            self.spawn_city_buildings()

        self.lines = []
        line_spacing = int(80 * self.scale_y)
        for y in range(0, self.HEIGHT + int(200 * self.scale_y), line_spacing):
            line = self.canvas.create_rectangle(
                self.ROAD_CENTER - int(5 * self.scale_x), y,
                self.ROAD_CENTER + int(5 * self.scale_x), y + int(40 * self.scale_y),
                fill="white"
            )
            self.lines.append(line)

        self.finish_line_y = self.scale_finish_line_y()
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
            if (x < building["x"] + building["width"] + int(20 * self.scale_x) and
                    x + width + int(20 * self.scale_x) > building["x"] and
                    y < building["y"] + building["height"] + int(30 * self.scale_y) and
                    y + height + int(30 * self.scale_y) > building["y"]):
                return True
        return False

    def spawn_city_buildings(self):
        """Создает городские здания по бокам дороги на безопасном расстоянии"""

        left_area_start = int(30 * self.scale_x)
        left_area_end = self.ROAD_LEFT - int(60 * self.scale_x)

        right_area_start = self.ROAD_RIGHT + int(60 * self.scale_x)
        right_area_end = self.WIDTH - int(100 * self.scale_x)

        left_buildings = []
        right_buildings = []

        building_count = int(12 * min(self.scale_x, self.scale_y))

        # Генерируем здания слева
        for i in range(building_count):
            max_attempts = 50
            for attempt in range(max_attempts):
                width = random.randint(int(70 * self.scale_x), int(140 * self.scale_x))
                height = random.randint(int(130 * self.scale_y), int(250 * self.scale_y))

                x = random.randint(left_area_start, left_area_end - width)
                y = random.randint(-self.HEIGHT, self.HEIGHT + int(500 * self.scale_y))

                if not self.check_building_collision(x, y, width, height, left_buildings, "left"):
                    building_color = random.choice(["#4a4a4a", "#5a5a5a", "#6a6a6a", "#3a3a3a", "#585858", "#707070"])

                    building = self.canvas.create_rectangle(
                        x, y, x + width, y + height,
                        fill=building_color,
                        outline="#888888",
                        width=int(2 * min(self.scale_x, self.scale_y)),
                        tags="building"
                    )

                    windows = []
                    window_size = int(15 * min(self.scale_x, self.scale_y))
                    window_spacing = int(22 * min(self.scale_x, self.scale_y))

                    for wx in range(x + int(12 * self.scale_x), x + width - int(12 * self.scale_x), window_spacing):
                        for wy in range(y + int(15 * self.scale_y), y + height - int(15 * self.scale_y),
                                        window_spacing):
                            if wx + window_size <= x + width - int(
                                    5 * self.scale_x) and wy + window_size <= y + height - int(5 * self.scale_y):
                                window_color = random.choice(["#ffffaa", "#ffcc66", "#ffaa66", "#ffee88"])
                                window = self.canvas.create_rectangle(
                                    wx, wy, wx + window_size, wy + window_size,
                                    fill=window_color,
                                    outline="#ccccaa",
                                    width=int(1 * min(self.scale_x, self.scale_y)),
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
        for i in range(building_count):
            max_attempts = 50
            for attempt in range(max_attempts):
                width = random.randint(int(70 * self.scale_x), int(140 * self.scale_x))
                height = random.randint(int(130 * self.scale_y), int(250 * self.scale_y))

                x = random.randint(right_area_start, right_area_end - width)
                y = random.randint(-self.HEIGHT, self.HEIGHT + int(500 * self.scale_y))

                if not self.check_building_collision(x, y, width, height, right_buildings, "right"):
                    building_color = random.choice(["#4a4a4a", "#5a5a5a", "#6a6a6a", "#3a3a3a", "#585858", "#707070"])

                    building = self.canvas.create_rectangle(
                        x, y, x + width, y + height,
                        fill=building_color,
                        outline="#888888",
                        width=int(2 * min(self.scale_x, self.scale_y)),
                        tags="building"
                    )

                    windows = []
                    window_size = int(15 * min(self.scale_x, self.scale_y))
                    window_spacing = int(22 * min(self.scale_x, self.scale_y))

                    for wx in range(x + int(12 * self.scale_x), x + width - int(12 * self.scale_x), window_spacing):
                        for wy in range(y + int(15 * self.scale_y), y + height - int(15 * self.scale_y),
                                        window_spacing):
                            if wx + window_size <= x + width - int(
                                    5 * self.scale_x) and wy + window_size <= y + height - int(5 * self.scale_y):
                                window_color = random.choice(["#ffffaa", "#ffcc66", "#ffaa66", "#ffee88"])
                                window = self.canvas.create_rectangle(
                                    wx, wy, wx + window_size, wy + window_size,
                                    fill=window_color,
                                    outline="#ccccaa",
                                    width=int(1 * min(self.scale_x, self.scale_y)),
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

        self.buildings = left_buildings + right_buildings

    def countdown(self):
        self.countdown_value = 3

        font_size = int(120 * min(self.scale_x, self.scale_y))
        self.countdown_text = self.canvas.create_text(
            self.WIDTH // 2, self.HEIGHT // 2,
            text=str(self.countdown_value),
            font=("Arial", font_size, "bold"),
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
        w = int(50 * self.scale_x)
        h = int(80 * self.scale_y)
        car = self.canvas.create_rectangle(
            x - w // 2, y - h // 2,
            x + w // 2, y + h // 2,
            fill=color, outline="white", width=int(2 * min(self.scale_x, self.scale_y))
        )
        window_width = int(30 * self.scale_x)
        window_height = int(25 * self.scale_y)
        window1 = self.canvas.create_rectangle(
            x - window_width // 2, y - int(20 * self.scale_y),
            x + window_width // 2, y + int(5 * self.scale_y),
            fill="#88CCFF", outline="white", width=int(1 * min(self.scale_x, self.scale_y))
        )
        window2 = self.canvas.create_rectangle(
            x - window_width // 2, y + int(10 * self.scale_y),
            x + window_width // 2, y + int(30 * self.scale_y),
            fill="#88CCFF", outline="white", width=int(1 * min(self.scale_x, self.scale_y))
        )
        return {"body": car, "window1": window1, "window2": window2, "x": x, "y": y}

    def move_car(self, car, dx, dy):
        self.canvas.move(car["body"], dx, dy)
        self.canvas.move(car["window1"], dx, dy)
        self.canvas.move(car["window2"], dx, dy)
        car["x"] += dx
        car["y"] += dy

    def move_car_to_position(self, car, position_index):
        dx = self.LANE_POSITIONS[position_index] - car["x"]
        if dx != 0:
            self.move_car(car, dx, 0)

    def get_car_coords(self, car):
        return self.canvas.coords(car["body"])

    def draw_road(self):
        if self.current_track == "forest":
            roadside_color = "#1a5c1a"
        elif self.current_track == "city":
            roadside_color = "#3a3a4a"
        else:
            roadside_color = "#228B22"

        self.canvas.create_rectangle(
            self.ROAD_LEFT, 0, self.ROAD_RIGHT, self.HEIGHT,
            fill="#333333", outline=""
        )
        line_width = int(5 * min(self.scale_x, self.scale_y))
        self.canvas.create_line(self.ROAD_LEFT, 0, self.ROAD_LEFT, self.HEIGHT, fill="yellow", width=line_width)
        self.canvas.create_line(self.ROAD_RIGHT, 0, self.ROAD_RIGHT, self.HEIGHT, fill="yellow", width=line_width)
        self.canvas.create_rectangle(0, 0, self.ROAD_LEFT, self.HEIGHT, fill=roadside_color, outline="")
        self.canvas.create_rectangle(self.ROAD_RIGHT, 0, self.WIDTH, self.HEIGHT, fill=roadside_color, outline="")

    def spawn_fixed_obstacle(self, lane, y_pos, obs_type):
        if obs_type == "block":
            color = "#8B4513"
            w = int(25 * self.scale_x)
            h = int(25 * self.scale_y)
        elif obs_type == "rock":
            color = "#696969"
            w = int(22 * self.scale_x)
            h = int(22 * self.scale_y)
        elif obs_type == "tree":
            color = "#006400"
            w = int(20 * self.scale_x)
            h = int(35 * self.scale_y)
        elif obs_type == "cone":
            color = "#FF6600"
            w = int(18 * self.scale_x)
            h = int(25 * self.scale_y)
        elif obs_type == "box":
            color = "#8B6914"
            w = int(25 * self.scale_x)
            h = int(25 * self.scale_y)
        else:
            color = "#FFA500"
            w = int(20 * self.scale_x)
            h = int(20 * self.scale_y)

        x = self.LANE_POSITIONS[lane]

        obs = self.canvas.create_rectangle(
            x - w // 2, y_pos - h // 2,
            x + w // 2, y_pos + h // 2,
            fill=color, outline="yellow", width=int(2 * min(self.scale_x, self.scale_y))
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
        step = int(50 * self.scale_x)
        for i in range(self.ROAD_LEFT, self.ROAD_RIGHT, step):
            rect = self.canvas.create_rectangle(
                i, self.finish_line_y, i + int(40 * self.scale_x), self.finish_line_y + int(15 * self.scale_y),
                fill="#FFA500", outline="white", width=int(2 * min(self.scale_x, self.scale_y))
            )
            self.finish_line.append(rect)

        font_size = int(30 * min(self.scale_x, self.scale_y))
        text = self.canvas.create_text(self.ROAD_CENTER, self.finish_line_y - int(20 * self.scale_y),
                                       text="ФИНИШ",
                                       font=("Arial", font_size, "bold"), fill="#FFA500")
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
            save_file = self.SAVE_FILE_FOREST
        else:
            save_file = self.SAVE_FILE_CITY

        if os.path.exists(save_file):
            try:
                with open(save_file, "r", encoding="utf-8") as f:
                    return json.load(f).get("best_time")
            except:
                pass
        return None

    def save_best(self, current):
        if self.current_track == "forest":
            save_file = self.SAVE_FILE_FOREST
        else:
            save_file = self.SAVE_FILE_CITY

        best = self.load_best(self.current_track)
        if best is None or current < best:
            with open(save_file, "w", encoding="utf-8") as f:
                json.dump({"best_time": current}, f, ensure_ascii=False)
            return True
        return False

    def show_finish_window(self, race_time, is_new_record=False):
        finish_window = tk.Toplevel(self.root)
        finish_window.title("Финиш!")
        finish_window.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        finish_window.state("zoomed")
        finish_window.configure(bg="#1a1a2e")
        finish_window.transient(self.root)
        finish_window.grab_set()

        center_frame = tk.Frame(finish_window, bg="#1a1a2e")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        title_font_size = int(80 * min(self.scale_x, self.scale_y))
        tk.Label(
            center_frame,
            text="ФИНИШ!",
            font=("Arial", title_font_size, "bold"),
            fg="#00FF00",
            bg="#1a1a2e"
        ).pack(pady=int(50 * self.scale_y))

        time_font_size = int(48 * min(self.scale_x, self.scale_y))
        tk.Label(
            center_frame,
            text=f"Ваше время: {race_time:.2f} сек",
            font=("Arial", time_font_size),
            fg="yellow",
            bg="#1a1a2e"
        ).pack(pady=int(30 * self.scale_y))

        best = self.load_best(self.current_track)
        record_font_size = int(36 * min(self.scale_x, self.scale_y))
        if best:
            if is_new_record:
                tk.Label(
                    center_frame,
                    text="★ НОВЫЙ РЕКОРД! ★",
                    font=("Arial", record_font_size, "bold"),
                    fg="#FFD700",
                    bg="#1a1a2e"
                ).pack(pady=int(20 * self.scale_y))
            else:
                tk.Label(
                    center_frame,
                    text=f"Рекорд трассы: {best:.2f} сек",
                    font=("Arial", int(32 * min(self.scale_x, self.scale_y))),
                    fg="#FFD700",
                    bg="#1a1a2e"
                ).pack(pady=int(20 * self.scale_y))
        else:
            tk.Label(
                center_frame,
                text="★ НОВЫЙ РЕКОРД! ★",
                font=("Arial", record_font_size, "bold"),
                fg="#FFD700",
                bg="#1a1a2e"
            ).pack(pady=int(20 * self.scale_y))

        btn_font_size = int(28 * min(self.scale_x, self.scale_y))
        btn_width = int(400 * self.scale_x)
        btn_height = int(60 * self.scale_y)

        tk.Button(
            center_frame,
            text="ПОПРОБОВАТЬ СНОВА",
            font=("Arial", btn_font_size, "bold"),
            bg="green",
            fg="white",
            width=int(20 * self.scale_x),
            cursor="hand2",
            command=lambda: self.restart_game(finish_window)
        ).pack(pady=int(30 * self.scale_y))

        tk.Button(
            center_frame,
            text="ГЛАВНОЕ МЕНЮ",
            font=("Arial", btn_font_size, "bold"),
            bg="orange",
            fg="white",
            width=int(20 * self.scale_x),
            cursor="hand2",
            command=lambda: self.exit_to_menu_from_window(finish_window)
        ).pack(pady=int(15 * self.scale_y))

        finish_window.bind("<Escape>", lambda e: self.exit_to_menu_from_window(finish_window))
        finish_window.focus_set()

    def check_finish_by_distance(self):
        """Проверка достижения финиша"""
        if self.finished or not self.race_started or self.finish_triggered:
            return

        player_remaining = self.total_distance - self.player_distance

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
        game_over_window.title("Авария")
        game_over_window.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        game_over_window.state("zoomed")
        game_over_window.configure(bg="#1a1a2e")
        game_over_window.transient(self.root)
        game_over_window.grab_set()

        center_frame = tk.Frame(game_over_window, bg="#1a1a2e")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        title_font_size = int(80 * min(self.scale_x, self.scale_y))
        tk.Label(
            center_frame,
            text="АВАРИЯ!",
            font=("Arial", title_font_size, "bold"),
            fg="red",
            bg="#1a1a2e"
        ).pack(pady=int(50 * self.scale_y))

        race_time = time.time() - self.start_time
        text_font_size = int(36 * min(self.scale_x, self.scale_y))
        tk.Label(
            center_frame,
            text=f"Вы врезались в препятствие!\nВремя: {race_time:.2f} сек",
            font=("Arial", text_font_size),
            fg="white",
            bg="#1a1a2e"
        ).pack(pady=int(30 * self.scale_y))

        btn_font_size = int(28 * min(self.scale_x, self.scale_y))
        btn_width = int(400 * self.scale_x)
        btn_height = int(60 * self.scale_y)

        tk.Button(
            center_frame,
            text="ПОПРОБОВАТЬ СНОВА",
            font=("Arial", btn_font_size, "bold"),
            bg="green",
            fg="white",
            width=int(20 * self.scale_x),
            cursor="hand2",
            command=lambda: self.restart_game(game_over_window)
        ).pack(pady=int(30 * self.scale_y))

        tk.Button(
            center_frame,
            text="ГЛАВНОЕ МЕНЮ",
            font=("Arial", btn_font_size, "bold"),
            bg="orange",
            fg="white",
            width=int(20 * self.scale_x),
            cursor="hand2",
            command=lambda: self.exit_to_menu_from_window(game_over_window)
        ).pack(pady=int(15 * self.scale_y))

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

            if self.key_up:
                self.game_speed = min(15, self.game_speed + 0.2)
            if self.key_down:
                self.game_speed = max(2, self.game_speed - 0.2)

            if self.key_left and self.player_position_index > 0:
                self.player_position_index -= 1
                self.move_car_to_position(self.player, self.player_position_index)
                self.root.after(80, lambda: None)
            if self.key_right and self.player_position_index < 5:
                self.player_position_index += 1
                self.move_car_to_position(self.player, self.player_position_index)
                self.root.after(80, lambda: None)

            if not self.finished:
                self.player_distance += self.game_speed

            scroll_speed = self.game_speed
            for line in self.lines:
                self.canvas.move(line, 0, scroll_speed)
                coords = self.canvas.coords(line)
                if coords and coords[1] > self.HEIGHT:
                    self.canvas.coords(line, self.ROAD_CENTER - int(5 * self.scale_x),
                                       -int(80 * self.scale_y),
                                       self.ROAD_CENTER + int(5 * self.scale_x),
                                       -int(40 * self.scale_y))

            if hasattr(self, 'buildings'):
                for building in self.buildings:
                    self.canvas.move(building["id"], 0, scroll_speed)
                    for window in building["windows"]:
                        self.canvas.move(window, 0, scroll_speed)

                    building["y"] += scroll_speed

                    coords = self.canvas.coords(building["id"])
                    if coords and coords[1] > self.HEIGHT + int(300 * self.scale_y):
                        new_y = -building["height"] - random.randint(0, int(500 * self.scale_y))
                        dy = new_y - building["y"]
                        self.canvas.move(building["id"], 0, dy)
                        for window in building["windows"]:
                            self.canvas.move(window, 0, dy)
                        building["y"] = new_y

            for obs in self.obstacles[:]:
                self.canvas.move(obs["id"], 0, scroll_speed)
                obs["y"] += scroll_speed

                if obs["y"] > self.HEIGHT + int(200 * self.scale_y):
                    self.canvas.delete(obs["id"])
                    self.obstacles.remove(obs)

            if not self.finished and self.check_collision(self.player, self.obstacles):
                self.game_over = True
                self.race_started = False
                self.show_game_over_window()
                return

            remaining = self.total_distance - self.player_distance
            if remaining <= int(500 * self.scale_y) and not self.finish_visible:
                self.spawn_finish_line()

            if not self.finished and self.finish_visible and self.finish_line:
                for item in self.finish_line:
                    self.canvas.move(item, 0, scroll_speed)

            self.check_finish_by_distance()

            if not self.finished:
                race_time = time.time() - self.start_time
                speed_kmh = int(self.game_speed * 12)
                best = self.load_best(self.current_track)
                remaining_m = max(-10, int((self.total_distance - self.player_distance) / 10))

                txt = f"ВРЕМЯ: {race_time:.2f} сек   |   СКОРОСТЬ: {speed_kmh} км/ч   |   ДО ФИНИША: {remaining_m} м"
                if best:
                    txt += f"   |   РЕКОРД: {best:.2f} сек"

                self.info.config(text=txt, fg="white")

                self.canvas.delete("progress")
                progress_width = int(400 * self.scale_x)
                player_progress = min(1.0, self.player_distance / self.total_distance)
                bar_x = self.WIDTH // 2 - progress_width // 2

                self.canvas.create_rectangle(bar_x, int(20 * self.scale_y),
                                             bar_x + progress_width, int(35 * self.scale_y),
                                             fill="#444", outline="white",
                                             tags="progress")
                self.canvas.create_rectangle(bar_x, int(20 * self.scale_y),
                                             bar_x + progress_width * player_progress, int(35 * self.scale_y),
                                             fill="#3366FF", outline="", tags="progress")

        self.root.after(16, self.update)


if __name__ == "__main__":
    root = tk.Tk()
    game = RacingGame(root)
    root.mainloop()