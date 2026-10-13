import math
import os
import random
import string
import tkinter as tk
from pathlib import Path
from tkinter import font as tkfont

from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageTk

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame

ASSETS = Path(__file__).parent / "assets"
W, H = 960, 540
RED, GREEN, GREY = "#ff5555", "#55ff55", "#aaaaaa"
MARQUEE = (
    "* MINECRAFT KEYGEN * ЛР 3 - вариант 10 * greetz to Steve, Alex & all creepers"
    " * мы осуждаем пиратство *      "
)


def generate_key(number):
    if len(number) != 6 or any(symbol not in string.digits for symbol in number):
        raise ValueError("Введите ровно 6 цифр от 0 до 9")

    first_digits = "".join(random.sample(number[3:6], 3))
    second_digits = "".join(random.sample(number[0:3], 3))

    first_letters = "".join(random.choices(string.ascii_uppercase, k=2))
    second_letters = "".join(random.choices(string.ascii_uppercase, k=2))

    first_block = first_digits + first_letters
    second_block = second_digits + second_letters
    total = int(first_digits) + int(second_digits)

    return f"{first_block}-{second_block} {total:04d}"


def render_text(text, size, color):
    try:
        font = ImageFont.truetype(str(ASSETS / "font.ttf"), size)
    except OSError:
        font = ImageFont.load_default(size)
    shift = max(1, size // 8)
    right, bottom = font.getbbox(text)[2:]
    image = Image.new("RGBA", (right + shift, bottom + shift), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    shadow = tuple(c // 4 for c in ImageColor.getrgb(color))
    draw.text((shift, shift), text, font=font, fill=shadow)
    draw.text((0, 0), text, font=font, fill=color)
    return image


def text_photo(text, size, color):
    return ImageTk.PhotoImage(render_text(text, size, color))


def button_photo(text, width, height, size, hover):
    fill, color = ("#7e88bf", "#ffffa0") if hover else ("#6f6f6f", "#ffffff")
    image = Image.new("RGBA", (width, height), "black")
    draw = ImageDraw.Draw(image)
    draw.rectangle((2, 2, width - 3, height - 3), fill=fill)
    draw.rectangle((2, 2, width - 3, 3), fill="#ffffff55")
    draw.rectangle((2, 2, 3, height - 3), fill="#ffffff55")
    draw.rectangle((2, height - 4, width - 3, height - 3), fill="#00000066")
    draw.rectangle((width - 4, 2, width - 3, height - 3), fill="#00000066")
    label = render_text(text, size, color)
    image.alpha_composite(label, ((width - label.width) // 2, (height - label.height) // 2))
    return ImageTk.PhotoImage(image)


def load_scene():
    try:
        scene = Image.open(ASSETS / "background.jpg").convert("RGBA").resize((W, H))
    except OSError:
        scene = Image.new("RGBA", (W, H), "#2b2b2b")
    scene.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 40)))
    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(panel)
    draw.rectangle((230, 175, 729, 469), fill=(0, 0, 0, 170), outline="#a0a0a0", width=2)
    draw.rectangle((0, 504, W, 536), fill=(0, 0, 0, 150))
    scene.alpha_composite(panel)
    return scene


class Keygen:
    def __init__(self):
        self.window = window = tk.Tk()
        window.title("Minecraft Keygen — вариант 10")
        window.geometry(f"{W}x{H}")
        window.resizable(False, False)
        self.canvas = canvas = tk.Canvas(window, width=W, height=H, highlightthickness=0)
        canvas.pack()
        self.refs = []
        self.key = ""
        self.reveal = None
        self.tick_count = 0

        self.add(ImageTk.PhotoImage(load_scene()), W // 2, H // 2)
        self.logo_y = 85
        try:
            logo = Image.open(ASSETS / "logo.png").convert("RGBA")
        except OSError:
            logo = render_text("MINECRAFT", 48, "#ffffff")
        self.logo = self.add(ImageTk.PhotoImage(logo), W // 2, self.logo_y)
        self.splash_frames = self.make_splash()
        self.splash_x = W // 2 + logo.width // 2 - 60
        self.splash_y = self.logo_y + logo.height // 2 - 5
        self.splash = self.add(self.splash_frames[0], self.splash_x, self.splash_y)

        self.add(text_photo("Введите 6 цифр:", 14, "#ffffff"), W // 2, 205)
        fixed = tkfont.nametofont("TkFixedFont").copy()
        fixed.configure(size=20, weight="bold")
        self.font = fixed
        check = window.register(lambda s: len(s) <= 6 and all(c in string.digits for c in s))
        self.number = self.entry(12, 245, validate="key", validatecommand=(check, "%P"))
        self.number.focus_set()
        self.number.bind("<Return>", lambda event: self.generate())

        self.button("gen", "Сгенерировать", 300, 44, 16, W // 2, 300, self.generate)
        self.value = tk.StringVar(value="XXXXX-XXXXX XXXX")
        self.output = self.entry(
            18, 360, textvariable=self.value, state="readonly", fg=GREEN, readonlybackground="black"
        )
        self.output.bind("<Button-1>", lambda event: self.copy())
        self.status = self.add(text_photo(" ", 10, GREY), W // 2, 400)

        self.music_state = self.start_music()
        self.music_button = self.button("music", self.music_label(), 220, 34, 12, W // 2, 445, self.toggle_music)

        marquee = ImageTk.PhotoImage(render_text(MARQUEE * 2, 14, "#ffff55"))
        self.marquee_w = marquee.width() // 2
        self.marquee_x = 0
        self.marquee = [
            self.add(marquee, x, 520, anchor="w") for x in (0, self.marquee_w)
        ]
        window.protocol("WM_DELETE_WINDOW", self.close)
        self.tick()

    def add(self, photo, x, y, anchor="center"):
        self.refs.append(photo)
        return self.canvas.create_image(x, y, image=photo, anchor=anchor)

    def entry(self, width, y, **options):
        options = {"fg": "white", **options}
        entry = tk.Entry(
            self.window, width=width, font=self.font, justify="center", bg="black",
            insertbackground="white", relief="flat", highlightthickness=2,
            highlightbackground="#a0a0a0", highlightcolor="white", **options,
        )
        self.canvas.create_window(W // 2, y, window=entry)
        return entry

    def button(self, tag, text, width, height, size, x, y, command):
        item = self.canvas.create_image(x, y, tags=tag)

        def render(text):
            normal = button_photo(text, width, height, size, False)
            hover = button_photo(text, width, height, size, True)
            self.refs.extend((normal, hover))
            self.canvas.itemconfig(item, image=normal)
            self.canvas.tag_bind(tag, "<Enter>", lambda e: (self.canvas.itemconfig(item, image=hover), self.canvas.config(cursor="hand2")))
            self.canvas.tag_bind(tag, "<Leave>", lambda e: (self.canvas.itemconfig(item, image=normal), self.canvas.config(cursor="")))

        render(text)
        self.canvas.tag_bind(tag, "<Button-1>", lambda e: command())
        return render

    def make_splash(self):
        base = render_text("Мы осуждаем пиратство!", 14, "#ffff55")
        frames = []
        for i in range(12):
            scale = 1 + 0.08 * math.sin(2 * math.pi * i / 12)
            size = (round(base.width * scale), round(base.height * scale))
            frame = base.resize(size, Image.NEAREST).rotate(18, Image.BICUBIC, expand=True)
            frames.append(ImageTk.PhotoImage(frame))
        return frames

    def tick(self):
        self.tick_count += 1
        bob = round(4 * math.sin(self.tick_count / 10))
        self.canvas.coords(self.logo, W // 2, self.logo_y + bob)
        self.canvas.coords(self.splash, self.splash_x, self.splash_y + bob)
        self.canvas.itemconfig(self.splash, image=self.splash_frames[self.tick_count // 3 % 12])
        self.marquee_x = (self.marquee_x - 2) % self.marquee_w
        for i, item in enumerate(self.marquee):
            self.canvas.coords(item, i * self.marquee_w - self.marquee_x, 520)
        self.window.after(33, self.tick)

    def set_status(self, text, color):
        self.status_photo = text_photo(text or " ", 10, color)
        self.canvas.itemconfig(self.status, image=self.status_photo)

    def generate(self):
        try:
            key = generate_key(self.number.get())
        except ValueError as error:
            self.set_status(str(error), RED)
            return
        self.key = key
        self.set_status("", GREY)
        if self.reveal:
            self.window.after_cancel(self.reveal)
        self.reveal_step(key, 0)

    def reveal_step(self, key, step):
        shown = len(key) * step // 20
        chars = string.ascii_uppercase + string.digits
        self.value.set("".join(
            c if i < shown or c in "- " else random.choice(chars) for i, c in enumerate(key)
        ))
        self.reveal = self.window.after(35, self.reveal_step, key, step + 1) if step < 20 else None

    def copy(self):
        if not self.key:
            self.set_status("Сначала сгенерируйте ключ", RED)
            return
        self.window.clipboard_clear()
        self.window.clipboard_append(self.key)
        self.set_status("Ключ скопирован в буфер обмена", GREEN)

    def start_music(self):
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(str(ASSETS / "music.ogg"))
            pygame.mixer.music.set_volume(0.35)
            pygame.mixer.music.play(-1)
        except (pygame.error, FileNotFoundError):
            return None
        return True

    def music_label(self):
        if self.music_state is None:
            return "Музыка: нет"
        return "Музыка: вкл" if self.music_state else "Музыка: выкл"

    def toggle_music(self):
        if self.music_state is None:
            return
        self.music_state = not self.music_state
        (pygame.mixer.music.unpause if self.music_state else pygame.mixer.music.pause)()
        self.music_button(self.music_label())

    def close(self):
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
        pygame.mixer.quit()
        self.window.destroy()


def create_gui():
    Keygen().window.mainloop()


if __name__ == "__main__":
    create_gui()
