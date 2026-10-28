import math
import os
import random
import string
import tkinter as tk
from pathlib import Path
from tkinter import font as tkfont

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame
from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageTk

ASSETS = Path(__file__).parent / "assets"
W, H = 960, 540
RED, GREEN, GREY = "#ff5555", "#55ff55", "#aaaaaa"
MARQUEE = (
    "* MINECRAFT KEYGEN * ЛР 3 - вариант 10 * greetz to Steve, Alex & all creepers"
    " * мы осуждаем пиратство *      "
)


def generate_key(number):
    """Генерирует ключ вида XXXXX-XXXXX XXXX из 6 введённых цифр."""
    # Проверяем ввод: ровно 6 символов и все они цифры 0-9
    if len(number) != 6 or any(symbol not in string.digits for symbol in number):
        raise ValueError("Введите ровно 6 цифр от 0 до 9")

    # 1 блок получает цифры 4,5,6, а 2 блок цифры 1,2,3 (в случайном порядке)
    first_digits = "".join(random.sample(number[3:6], 3))
    second_digits = "".join(random.sample(number[0:3], 3))

    # Добиваем каждый блок до 5 символов двумя случайными буквами A-Z
    first_letters = "".join(random.choices(string.ascii_uppercase, k=2))
    second_letters = "".join(random.choices(string.ascii_uppercase, k=2))

    first_block = first_digits + first_letters
    second_block = second_digits + second_letters
    total = int(first_digits) + int(second_digits) # 3 блок: сумма трёхзначных чисел из 1 и 2 блоков

    return f"{first_block}-{second_block} {total:04d}" # :04d дополняет сумму нулями слева до 4 знаков (например 467 -> 0467)


def render_text(text, size, color):
    """Рисует текст пиксельным шрифтом с тенью, как в Minecraft. Возвращает картинку Pillow."""
    try:
        font = ImageFont.truetype(str(ASSETS / "font.ttf"), size)
    except OSError: # Если шрифта нет, берём стандартный
        font = ImageFont.load_default(size)
    shift = max(1, size // 8)  # насколько сдвинута тень
    right, bottom = font.getbbox(text)[2:]  # размер, который займёт текст
    # Прозрачная картинка под текст + место под тень
    image = Image.new("RGBA", (right + shift, bottom + shift), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    shadow = tuple(c // 4 for c in ImageColor.getrgb(color))  # тень в 4 раза темнее текста
    draw.text((shift, shift), text, font=font, fill=shadow)  # сначала тень
    draw.text((0, 0), text, font=font, fill=color)  # потом сам текст поверх
    return image


def text_photo(text, size, color):
    """То же, что render_text, но сразу в формате tkinter."""
    return ImageTk.PhotoImage(render_text(text, size, color))


def button_photo(text, width, height, size, hover):
    """Рисует каменную кнопку в стиле Minecraft. hover=True — вариант при наведении мыши."""
    fill, color = ("#7e88bf", "#ffffa0") if hover else ("#6f6f6f", "#ffffff")
    image = Image.new("RGBA", (width, height), "black")  # чёрный фон = рамка
    draw = ImageDraw.Draw(image)
    draw.rectangle((2, 2, width - 3, height - 3), fill=fill)  # заливка кнопки
    # Светлые полоски сверху и слева, тёмные снизу и справа — эффект объёма
    draw.rectangle((2, 2, width - 3, 3), fill="#ffffff55")
    draw.rectangle((2, 2, 3, height - 3), fill="#ffffff55")
    draw.rectangle((2, height - 4, width - 3, height - 3), fill="#00000066")
    draw.rectangle((width - 4, 2, width - 3, height - 3), fill="#00000066")
    # Надпись ставим ровно по центру кнопки
    label = render_text(text, size, color)
    image.alpha_composite(label, ((width - label.width) // 2, (height - label.height) // 2))
    return ImageTk.PhotoImage(image)


def load_scene():
    """Собирает фон: картинка + затемнение + полупрозрачная панель под кнопками."""
    try:
        scene = Image.open(ASSETS / "background.jpg").convert("RGBA").resize((W, H))
    except OSError:
        # Нет картинки — просто тёмно-серый фон
        scene = Image.new("RGBA", (W, H), "#2b2b2b")
    scene.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 40)))  # слегка затемняет
    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(panel)
    # Тёмная панель в центре, чтобы текст читался на пёстром фоне
    draw.rectangle((230, 175, 729, 469), fill=(0, 0, 0, 170), outline="#a0a0a0", width=2)
    # Тёмная полоса внизу под бегущей строкой
    draw.rectangle((0, 504, W, 536), fill=(0, 0, 0, 150))
    scene.alpha_composite(panel)
    return scene


class Keygen:
    """Окно кейгена."""

    def __init__(self):
        # Создаём окно фиксированного размера
        self.window = window = tk.Tk()
        window.title("Minecraft Keygen")
        window.geometry(f"{W}x{H}")
        window.resizable(False, False)
        self.canvas = tk.Canvas(window, width=W, height=H, highlightthickness=0)
        self.canvas.pack()
        self.refs = []  # храним все картинки, иначе python их удалит из памяти
        self.key = ""  # последний сгенерированный ключ
        self.reveal = None  # id запланированного шага анимации ключа
        self.tick_count = 0  # счётчик кадров общей анимации

        # Фон
        self.add(ImageTk.PhotoImage(load_scene()), W // 2, H // 2)

        # Логотип сверху
        self.logo_y = 85
        try:
            logo = Image.open(ASSETS / "logo.png").convert("RGBA")
        except OSError:
            logo = render_text("MINECRAFT", 48, "#ffffff")
        self.logo = self.add(ImageTk.PhotoImage(logo), W // 2, self.logo_y)

        # Жёлтая пульсирующая надпись у правого нижнего края логотипа
        self.splash_frames = self.make_splash()
        self.splash_x = W // 2 + logo.width // 2 - 60
        self.splash_y = self.logo_y + logo.height // 2 - 5
        self.splash = self.add(self.splash_frames[0], self.splash_x, self.splash_y)

        # Подпись и поле ввода числа
        self.add(text_photo("Введите 6 цифр:", 14, "#ffffff"), W // 2, 205)
        fixed = tkfont.nametofont("TkFixedFont").copy()  # системный моноширинный шрифт
        fixed.configure(size=20, weight="bold")
        self.font = fixed
        # Проверка при каждом нажатии клавиши: не больше 6 символов и только цифры.
        # "%P" — так tkinter передаёт текст поля, каким он станет после нажатия
        check = window.register(lambda s: len(s) <= 6 and all(c in string.digits for c in s))
        self.number = self.entry(12, 245, validate="key", validatecommand=(check, "%P"))
        self.number.focus_set()  # курсор сразу в поле
        self.number.bind("<Return>", lambda event: self.generate())  # Enter = сгенерировать

        # Кнопка генерации
        self.button("gen", "Сгенерировать", 300, 44, 16, W // 2, 300, self.generate)

        # Поле с ключом: только для чтения, клик копирует ключ
        self.value = tk.StringVar(value="XXXXX-XXXXX XXXX")
        self.output = self.entry(
            18, 360, textvariable=self.value, state="readonly", fg=GREEN, readonlybackground="black"
        )
        self.output.bind("<Button-1>", lambda event: self.copy())

        # Строка статуса (ошибки и подсказки)
        self.status = self.add(text_photo(" ", 10, GREY), W // 2, 400)

        # Музыка и кнопка её включения/выключения
        self.music_state = self.start_music()
        self.music_button = self.button("music", self.music_label(), 220, 34, 12, W // 2, 445, self.toggle_music)

        marquee = ImageTk.PhotoImage(render_text(MARQUEE * 2, 14, "#ffff55"))
        self.marquee_w = marquee.width() // 2
        self.marquee_x = 0
        self.marquee = [
            self.add(marquee, x, 520, anchor="w") for x in (0, self.marquee_w)
        ]

        # При закрытии окна сначала выключаем музыку
        window.protocol("WM_DELETE_WINDOW", self.close)
        self.tick()  # запускаем анимацию

    def add(self, photo, x, y, anchor="center"):
        """Кладёт картинку на canvas и запоминает её. Возвращает id элемента."""
        self.refs.append(photo)
        return self.canvas.create_image(x, y, image=photo, anchor=anchor)

    def entry(self, width, y, **options):
        """Создаёт чёрное поле ввода в стиле Minecraft по центру окна на высоте y."""
        options = {"fg": "white", **options}
        entry = tk.Entry(
            self.window, width=width, font=self.font, justify="center", bg="black",
            insertbackground="white", relief="flat", highlightthickness=2,
            highlightbackground="#a0a0a0", highlightcolor="white", **options,
        )
        self.canvas.create_window(W // 2, y, window=entry)  # вставляем виджет внутрь canvas
        return entry

    def button(self, tag, text, width, height, size, x, y, command):
        """Делает кнопку из картинки. Возвращает функцию для смены надписи на кнопке."""
        item = self.canvas.create_image(x, y, tags=tag)

        def render(text):
            # Две картинки: обычная и при наведении
            normal = button_photo(text, width, height, size, False)
            hover = button_photo(text, width, height, size, True)
            self.refs.extend((normal, hover))
            self.canvas.itemconfig(item, image=normal)
            # Мышь навели — светлая кнопка и курсор-рука; увели — обратно
            self.canvas.tag_bind(tag, "<Enter>", lambda e: (self.canvas.itemconfig(item, image=hover), self.canvas.config(cursor="hand2")))
            self.canvas.tag_bind(tag, "<Leave>", lambda e: (self.canvas.itemconfig(item, image=normal), self.canvas.config(cursor="")))

        render(text)
        self.canvas.tag_bind(tag, "<Button-1>", lambda e: command())  # клик = действие
        return render

    def make_splash(self):
        """Заранее рисует 12 кадров надписи разного размера (эффект пульсации)."""
        base = render_text("Мы осуждаем пиратство!", 14, "#ffff55")
        frames = []
        for i in range(12):
            # Масштаб плавно меняется от 0.92 до 1.08
            scale = 1 + 0.08 * math.sin(2 * math.pi * i / 12)
            size = (round(base.width * scale), round(base.height * scale))
            # NEAREST сохраняет пиксельность, rotate наклоняет надпись на 18 градусов
            frame = base.resize(size, Image.NEAREST).rotate(18, Image.BICUBIC, expand=True)
            frames.append(ImageTk.PhotoImage(frame))
        return frames

    def tick(self):
        """Один кадр анимации. Вызывает сам себя каждые 33 мс (~30 кадров в секунду)."""
        self.tick_count += 1
        # Логотип и надпись плавно качаются вверх-вниз на 4 пикселя
        bob = round(4 * math.sin(self.tick_count / 10))
        self.canvas.coords(self.logo, W // 2, self.logo_y + bob)
        self.canvas.coords(self.splash, self.splash_x, self.splash_y + bob)
        # Каждые 3 тика показываем следующий кадр пульсации
        self.canvas.itemconfig(self.splash, image=self.splash_frames[self.tick_count // 3 % 12])
        # Сдвигаем бегущую строку на 2 пикселя влево (% зацикливает движение)
        self.marquee_x = (self.marquee_x + 2) % self.marquee_w
        for i, item in enumerate(self.marquee):
            self.canvas.coords(item, i * self.marquee_w - self.marquee_x, 520)
        self.window.after(33, self.tick)

    def set_status(self, text, color):
        """Показывает сообщение в строке статуса."""
        self.status_photo = text_photo(text or " ", 10, color)
        self.canvas.itemconfig(self.status, image=self.status_photo)

    def generate(self):
        """Обработчик кнопки «Сгенерировать» и клавиши Enter."""
        try:
            key = generate_key(self.number.get())
        except ValueError as error:
            self.set_status(str(error), RED)  # неверный ввод — пишем ошибку красным
            return
        self.key = key
        self.set_status("", GREY)
        # Если прошлая анимация ещё идёт — останавливаем её, чтобы не было двух сразу
        if self.reveal:
            self.window.after_cancel(self.reveal)
        self.reveal_step(key, 0)

    def reveal_step(self, key, step):
        """Анимация появления ключа: 20 шагов, символы открываются слева направо."""
        shown = len(key) * step // 20  # сколько символов уже открыто
        chars = string.ascii_uppercase + string.digits
        # Открытые символы и разделители показываем как есть, остальные — случайные
        self.value.set("".join(
            c if i < shown or c in "- " else random.choice(chars) for i, c in enumerate(key)
        ))
        # Планируем следующий шаг через 35 мс, пока не дойдём до 20
        self.reveal = self.window.after(35, self.reveal_step, key, step + 1) if step < 20 else None

    def copy(self):
        """Копирует ключ в буфер обмена (по клику на поле с ключом)."""
        if not self.key:
            self.set_status("Сначала сгенерируйте ключ", RED)
            return
        self.window.clipboard_clear()
        self.window.clipboard_append(self.key)
        self.set_status("Ключ скопирован в буфер обмена", GREEN)

    def start_music(self):
        """Запускает музыку по кругу. True — играет, None — звука нет (нет файла или колонок)."""
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(str(ASSETS / "music.ogg"))
            pygame.mixer.music.set_volume(0.35)
            pygame.mixer.music.play(-1)
        except (pygame.error, FileNotFoundError):
            return None
        return True

    def music_label(self):
        """Текст для кнопки музыки в зависимости от её состояния."""
        if self.music_state is None:
            return "Музыка: нет"
        return "Музыка: вкл" if self.music_state else "Музыка: выкл"

    def toggle_music(self):
        """Ставит музыку на паузу или снимает с паузы."""
        if self.music_state is None:
            return
        self.music_state = not self.music_state
        (pygame.mixer.music.unpause if self.music_state else pygame.mixer.music.pause)()
        self.music_button(self.music_label())  # перерисовываем надпись на кнопке

    def close(self):
        """Выключает музыку и закрывает окно."""
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
        pygame.mixer.quit()
        self.window.destroy()


def create_gui():
    Keygen().window.mainloop()  # mainloop держит окно открытым и обрабатывает события


if __name__ == "__main__":
    create_gui()
