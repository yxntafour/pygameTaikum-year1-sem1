import os
import math
import time
import pygame

import audio
from game_logic import FLASH_SECONDS

# ---------------- ที่อยู่ไฟล์ (อิงจากโฟลเดอร์ที่ไฟล์โค้ดนี้อยู่ รันจากที่ไหนก็หาเจอ) ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))       # = โฟลเดอร์ pygameproject1
IMAGE_DIR = os.path.join(BASE_DIR, "images")               # รูปโจทย์
BG_PATH = os.path.join(BASE_DIR, "ui_images", "bg.png")    # รูปพื้นหลัง (ใช้ทุกหน้า) ขนาดแนะนำ 800x600


def _find_font(name="Sriracha-Regular.ttf"):
    """หาไฟล์ฟอนต์ในโฟลเดอร์โปรเจค หรือโฟลเดอร์ที่อยู่ถัดออกไป 1 ชั้น"""
    for folder in (BASE_DIR, os.path.dirname(BASE_DIR)):
        path = os.path.join(folder, name)
        if os.path.isfile(path):
            return path
    print("[ฟอนต์] ไม่เจอไฟล์", name, "ในโฟลเดอร์", BASE_DIR, "หรือโฟลเดอร์ที่อยู่ถัดออกไป")
    return name


FONT_PATH = _find_font()
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".webp", ".png")   # ถ้ามีหลายไฟล์ชื่อเดียวกัน ใช้ตามลำดับนี้

# ---------------- สีธีม "สดใสแบบเกมมือถือ" ----------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
NAVY = (30, 58, 95)            # สีตัวหนังสือหลัก
SKY_TOP = (66, 165, 245)       # พื้นหลังไล่สี บน
SKY_BOTTOM = (178, 235, 255)   # พื้นหลังไล่สี ล่าง
SHADOW = (52, 110, 170)        # สีเงา (ใช้สีทึบ ไม่ใช้แบบโปร่งแสง กันกรอบดำ)
PANEL = (226, 241, 252)        # สีแผงหลังแป้นพิมพ์
ORANGE = (255, 138, 61)
YELLOW = (255, 202, 40)
BLUE = (41, 121, 255)
GREEN = (46, 204, 113)
RED = (239, 83, 80)
GRAY = (176, 190, 197)
LIGHT_BLUE = (129, 212, 250)

# สีปุ่มแป้นพิมพ์ แยกตามชนิดตัวอักษร
KEY_COLOR_CONSONANT = (255, 255, 255)   # พยัญชนะ
KEY_COLOR_VOWEL = (255, 241, 179)       # สระ
KEY_COLOR_TONE = (255, 205, 178)        # วรรณยุกต์
KEY_COLOR_OTHER = (207, 226, 243)       # ตัวเลข / สัญลักษณ์
VOWELS = set("ะัาำิีึืุูเแโใไ็ๅฤฦํฺ")
TONES = set("่้๊๋์")

# กล่องแสดงคำที่พิมพ์ (main.py ใช้ค่านี้เช็กว่าพิมพ์จนเต็มกล่องหรือยัง)
ANS_BOX = pygame.Rect(40, 245, 430, 45)
ANS_PADDING = 15

# ขนาดและตำแหน่งปุ่มแป้นพิมพ์ (แถวยาวสุด 12 ปุ่ม)
KEY_W, KEY_H = 50, 44
KEY_STEP = 56                    # ระยะห่างปุ่มในแถว (กว้างปุ่ม + ช่องว่าง)
KEY_ROW_STEP = 50                # ระยะห่างระหว่างแถว
KEY_X0, KEY_Y0 = 67, 305
KEY_ROW_SHIFT = [0, 0, 28, 56]   # เลื่อนแต่ละแถวให้เหลื่อมกันเหมือน iPhone
SIDE_KEY_W = 72                  # ความกว้างปุ่ม Shift กับปุ่มลบ (แถวล่าง)

# กล่องรูปโจทย์: จำนวนกล่องเท่ากับจำนวนรูปที่มีจริง (1-4 รูป) จัดไว้กลางจอ
MAX_IMAGES = 4
IMG_W, IMG_H = 140, 105
IMG_Y = 68
IMG_GAP = 20


def image_boxes(count):
    """คืนกล่องรูป count กล่อง เรียงตรงกลางจอ"""
    count = max(1, min(count, MAX_IMAGES))
    total_w = count * IMG_W + (count - 1) * IMG_GAP
    start_x = 400 - total_w // 2
    return [pygame.Rect(start_x + i * (IMG_W + IMG_GAP), IMG_Y, IMG_W, IMG_H) for i in range(count)]


# ---------------- ตัวช่วยเรื่องสีและฟอนต์ ----------------
def _shade(color, factor):
    """factor < 1 = เข้มขึ้น, factor > 1 = สว่างขึ้น"""
    if factor < 1:
        return tuple(int(c * factor) for c in color)
    return tuple(int(c + (255 - c) * (factor - 1)) for c in color)


_font_cache = {}


def get_font(size):
    """ฟอนต์ Sriracha ขนาดที่ต้องการ (โหลดครั้งเดียวแล้วเก็บไว้)"""
    if size not in _font_cache:
        font = pygame.font.Font(FONT_PATH, size)
        try:
            font.set_script("Thai")
        except (AttributeError, pygame.error):
            pass
        _font_cache[size] = font
    return _font_cache[size]


def draw_text(surface, text, font, color, center, shadow=True):
    """วาดตัวหนังสือตรงกลางจุดที่กำหนด มีเงาสีทึบให้อ่านง่ายบนพื้นหลัง"""
    if shadow:
        sh = font.render(text, True, SHADOW)
        surface.blit(sh, sh.get_rect(center=(center[0] + 2, center[1] + 3)))
    txt = font.render(text, True, color)
    surface.blit(txt, txt.get_rect(center=center))


_bg_image = None
_bg_loaded = False


def draw_background(surface):
    """พื้นหลังจากรูป ui_images/bg.png (ถ้าไม่มีรูป ใช้สีฟ้าเรียบๆ แทน)"""
    global _bg_image, _bg_loaded
    if not _bg_loaded:
        _bg_loaded = True
        if not os.path.isfile(BG_PATH):
            print("[พื้นหลัง] ไม่เจอไฟล์:", BG_PATH)
        else:
            try:
                img = pygame.image.load(BG_PATH)
                if img.get_size() != surface.get_size():
                    try:
                        img = pygame.transform.smoothscale(img, surface.get_size())
                    except (pygame.error, ValueError):
                        img = pygame.transform.scale(img, surface.get_size())   # ย่อแบบธรรมดาแทน
                _bg_image = img.convert()   # convert() = รูปทึบ กันตัวหนังสือกลายเป็นกล่อง
            except Exception as e:
                print("[พื้นหลัง] โหลดรูปไม่ได้:", repr(e))   # ดูข้อความนี้ในหน้าต่าง Terminal
                _bg_image = None
    surface.fill(SKY_TOP)
    if _bg_image:
        surface.blit(_bg_image, (0, 0))


def draw_card(surface, rect, color=WHITE, radius=16, border=None):
    """กล่องมุมโค้ง มีเงาสีทึบด้านล่าง"""
    pygame.draw.rect(surface, SHADOW, rect.move(0, 6), border_radius=radius)
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border:
        pygame.draw.rect(surface, border, rect, width=3, border_radius=radius)


def draw_pill(surface, text, font, center, bg, fg=WHITE):
    """ป้ายมุมมนเล็กๆ เช่น '3 พยางค์'"""
    txt = font.render(text, True, fg)
    rect = txt.get_rect(center=center).inflate(22, 8)
    pygame.draw.rect(surface, bg, rect, border_radius=rect.h // 2)
    surface.blit(txt, txt.get_rect(center=rect.center))


def draw_star(surface, center, radius, color, outline=None):
    points = []
    for i in range(10):
        r = radius if i % 2 == 0 else radius * 0.45
        angle = math.radians(-90 + i * 36)
        points.append((center[0] + r * math.cos(angle), center[1] + r * math.sin(angle)))
    pygame.draw.polygon(surface, color, points)
    if outline:
        pygame.draw.polygon(surface, outline, points, width=3)


# ---------------- เสียง hover (ดังครั้งเดียวตอนเมาส์เข้าปุ่ม) ----------------
_last_hover = None
_this_hover = None


def begin_frame():
    """main.py เรียกตอนต้นทุกเฟรม เพื่อจำว่าเฟรมก่อนเมาส์อยู่บนปุ่มไหน"""
    global _last_hover, _this_hover
    _last_hover = _this_hover
    _this_hover = None


def _on_hover(button_id):
    global _this_hover
    _this_hover = button_id
    if button_id != _last_hover:
        audio.play("hover")


# ---------------- ปุ่ม ----------------
class Button:
    def __init__(self, x, y, w, h, text, font, bg_color=WHITE, text_color=NAVY,
                 border_color=None, enabled=True, radius=12):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.border_color = border_color
        self.enabled = enabled
        self.radius = radius

    def draw(self, surface):
        hovered = self.enabled and self.rect.collidepoint(pygame.mouse.get_pos())
        if hovered:
            _on_hover((self.text, self.rect.topleft))

        base = self.bg_color if self.enabled else _shade(GRAY, 1.2)
        lift = 3 if hovered else 0                          # ชี้แล้วปุ่มลอยขึ้น
        body = self.rect.move(0, -lift)

        pygame.draw.rect(surface, _shade(base, 0.7), self.rect.move(0, 4), border_radius=self.radius)  # เงา
        pygame.draw.rect(surface, _shade(base, 1.15) if hovered else base, body, border_radius=self.radius)
        pygame.draw.rect(surface, self.border_color or _shade(base, 0.8), body, width=2, border_radius=self.radius)

        color = self.text_color if self.enabled else _shade(NAVY, 1.5)
        txt_surf = self.font.render(self.text, True, color)
        surface.blit(txt_surf, txt_surf.get_rect(center=body.center))

    def is_clicked(self, event):
        if self.enabled and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                audio.play("click")
                return True
        return False


# ---------------- รูปภาพโจทย์ ----------------
_image_cache = {}


def _image_path(category, answer, number):
    """images/<หมวด>/<คำตอบ>_<เลขรูป>.png (หรือ .jpg .jpeg .webp)"""
    for ext in IMAGE_EXTENSIONS:
        path = os.path.join(IMAGE_DIR, category, f"{answer}_{number}{ext}")
        if os.path.isfile(path):
            return path
    return None


def get_question_images(category, answer):
    """โหลดรูปทั้งหมดของข้อนี้ (_1 ถึง _4 เฉพาะไฟล์ที่มีจริง) ย่อให้พอดีกล่องโดยคงสัดส่วน"""
    key = (category, answer)
    if key not in _image_cache:
        images = []
        for number in range(1, MAX_IMAGES + 1):
            path = _image_path(category, answer, number)
            if not path:
                continue            # ไม่มีรูปเลขนี้ ข้ามไป (เช่น มีแค่ _1 กับ _2)
            try:
                img = pygame.image.load(path)
                scale = min((IMG_W - 10) / img.get_width(), (IMG_H - 10) / img.get_height())
                size = (max(1, int(img.get_width() * scale)), max(1, int(img.get_height() * scale)))
                images.append(pygame.transform.smoothscale(img, size).convert_alpha())
            except Exception as e:
                print("[รูปโจทย์] โหลดไม่ได้:", path, repr(e))
        _image_cache[key] = images
    return _image_cache[key]


# ---------------- หน้าแรก ----------------
def draw_title_subscreen(surface, font_title, font_btn):
    draw_background(surface)
    t = time.time()
    bob = math.sin(t * 2) * 6                       # ชื่อเกมลอยขึ้นลงเบาๆ
    draw_text(surface, "เกมทายคำ", get_font(80), WHITE, (400, 190 + bob))
    draw_text(surface, "ดูภาพ แล้วทายให้ถูก!", font_btn, NAVY, (400, 265), shadow=False)
    start_btn = Button(290, 330, 220, 70, "เริ่มเล่น", get_font(30), bg_color=ORANGE, text_color=WHITE, radius=20)
    start_btn.draw(surface)
    return {"start": start_btn}


# ---------------- หน้าเลือกหมวดและความยาก ----------------
DIFF_COLORS = {"ง่าย": GREEN, "ปานกลาง": YELLOW, "ยาก": RED}


def draw_menu_subscreen(surface, font_title, font_btn, categories, cat_offset, sel_cat, sel_diff):
    draw_background(surface)
    buttons = {}

    draw_text(surface, "เลือกหมวดหมู่", font_title, WHITE, (400, 50))

    btn_prev = Button(95, 125, 45, 70, "<", font_btn, bg_color=WHITE, enabled=cat_offset > 0)
    btn_next = Button(660, 125, 45, 70, ">", font_btn, bg_color=WHITE,
                      enabled=cat_offset < len(categories) - 3)
    btn_prev.draw(surface)
    btn_next.draw(surface)
    buttons["prev_cat"] = btn_prev
    buttons["next_cat"] = btn_next

    visible_cats = categories[cat_offset: cat_offset + 3]
    for i, cat_name in enumerate(visible_cats):
        x = 160 + i * 165
        selected = sel_cat == cat_name
        btn = Button(x, 115, 150, 90, cat_name, font_btn,
                     bg_color=ORANGE if selected else WHITE,
                     text_color=WHITE if selected else NAVY, radius=16)
        btn.draw(surface)
        buttons[f"cat_{cat_name}"] = btn

    draw_text(surface, "เลือกระดับความยาก", font_title, WHITE, (400, 265))

    for i, diff_name in enumerate(["ง่าย", "ปานกลาง", "ยาก"]):
        x = 190 + i * 145
        selected = sel_diff == diff_name
        btn = Button(x, 305, 130, 55, diff_name, font_btn,
                     bg_color=DIFF_COLORS[diff_name] if selected else WHITE,
                     text_color=WHITE if selected else NAVY, radius=28)
        btn.draw(surface)
        buttons[f"diff_{diff_name}"] = btn

    if sel_cat and sel_diff:
        btn_go = Button(290, 420, 220, 65, "เริ่มเกม!", get_font(28), bg_color=ORANGE, text_color=WHITE, radius=20)
        btn_go.draw(surface)
        buttons["go_game"] = btn_go
    else:
        draw_text(surface, "เลือกหมวดและระดับก่อนนะ", font_btn, NAVY, (400, 450), shadow=False)

    return buttons


# ---------------- หน้านับถอยหลัง ----------------
def draw_countdown_screen(surface, font_title, font_btn, number, progress=0.0):
    """progress = เวลาที่ผ่านไปของเลขนี้ (0.0 - 1.0) ใช้ทำแอนิเมชันเลขเด้ง"""
    draw_background(surface)
    draw_text(surface, "เตรียมตัว!", font_title, WHITE, (400, 160))

    progress = max(0.0, min(1.0, progress))
    num = get_font(140).render(str(number), True, ORANGE)
    scale = 1.4 - 0.4 * min(1.0, progress * 3)          # เด้งจากใหญ่ลงมาขนาดปกติ
    size = (int(num.get_width() * scale), int(num.get_height() * scale))
    num = pygame.transform.smoothscale(num, size)
    surface.blit(num, num.get_rect(center=(400, 320)))


# ---------------- หน้าเกม ----------------
def _key_color(char):
    if char in VOWELS:
        return KEY_COLOR_VOWEL
    if char in TONES:
        return KEY_COLOR_TONE
    if "ก" <= char <= "ฮ":
        return KEY_COLOR_CONSONANT
    return KEY_COLOR_OTHER


def _draw_timer_bar(surface, font_small, game):
    total = game.rules["time"]
    if game.timer_running and game.reveal is None:
        remaining = max(0.0, total - (time.time() - game.q_start_time))   # ทศนิยม ให้หลอดหดลื่นๆ
    else:
        remaining = game.time_left()
    ratio = remaining / total
    color = GREEN if ratio > 0.5 else YELLOW if ratio > 0.2 else RED

    bar = pygame.Rect(600, 22, 170, 26)
    pygame.draw.rect(surface, _shade(NAVY, 1.6), bar, border_radius=13)
    if ratio > 0:
        fill = bar.copy()
        fill.w = max(26, int(bar.w * ratio))
        pygame.draw.rect(surface, color, fill, border_radius=13)
    pygame.draw.rect(surface, WHITE, bar, width=2, border_radius=13)
    draw_text(surface, f"{game.time_left()} วิ", font_small, WHITE, bar.center)


def _draw_banner(surface, font_title, font_btn, title, subtitle, color, started_at, shake):
    """แถบแจ้งผล: เด้งขึ้นมาตอนแรก ถ้า shake=True จะสั่น (ตอนผิด)"""
    w, h = 560, 110
    banner = pygame.Surface((w, h + 6), pygame.SRCALPHA)
    pygame.draw.rect(banner, SHADOW, (0, 6, w, h), border_radius=18)
    pygame.draw.rect(banner, WHITE, (0, 0, w, h), border_radius=18)
    pygame.draw.rect(banner, color, (0, 0, w, h), width=5, border_radius=18)
    if subtitle:
        draw_text(banner, title, font_title, color, (w // 2, 38), shadow=False)
        draw_text(banner, subtitle, font_btn, NAVY, (w // 2, 80), shadow=False)
    else:
        draw_text(banner, title, font_title, color, (w // 2, h // 2), shadow=False)

    t = time.time() - started_at
    scale = 0.7 + 0.3 * min(1.0, t / 0.15)
    if 0.15 <= t < 0.3:
        scale = 1.0 + 0.06 * math.sin((t - 0.15) / 0.15 * math.pi)   # เด้งเกินนิดนึงแล้วกลับ
    offset_x = 0
    if shake and t < 0.4:
        offset_x = int(math.sin(t * 60) * 10 * (1 - t / 0.4))

    if scale != 1.0:
        banner = pygame.transform.smoothscale(banner, (int(w * scale), int((h + 6) * scale)))
    surface.blit(banner, banner.get_rect(center=(400 + offset_x, 130)))


def draw_game_screen(surface, font_title, font_btn, font_small, game, keyboard_layout, shift_on=False):
    draw_background(surface)
    buttons = {}

    # ---- แถบบน ----
    btn_close = Button(20, 16, 44, 40, "X", font_btn, bg_color=RED, text_color=WHITE)
    btn_close.draw(surface)
    buttons["close"] = btn_close

    draw_text(surface, f"ข้อที่ {game.q_index + 1} / {game.total_questions}", font_title, WHITE, (400, 35))
    _draw_timer_bar(surface, font_small, game)

    # ---- กล่องรูป 3 กล่อง ----
    images = get_question_images(game.category, game.current_q["answer"])
    for i, box in enumerate(image_boxes(len(images))):
        draw_card(surface, box, radius=14)
        img = images[i] if i < len(images) else None    # ไม่มีรูปเลย = โชว์กล่อง "?" กล่องเดียว
        if img:
            surface.blit(img, img.get_rect(center=box.center))
        else:
            draw_text(surface, "?", get_font(54), _shade(GRAY, 1.1), box.center, shadow=False)

    # ---- ป้ายสถานะ ----
    draw_pill(surface, f"{game.current_q['syllables']} พยางค์", font_small, (255, 200), BLUE)
    draw_pill(surface, f"โอกาสตอบ {game.lives_left} ครั้ง", font_small, (400, 200), RED)
    draw_pill(surface, f"คำใบ้เหลือ {game.hints_left} ครั้ง", font_small, (550, 200), ORANGE)

    if game.current_hint_text:
        draw_text(surface, f"คำใบ้: {game.current_hint_text}", font_small, NAVY, (400, 230), shadow=False)

    # ---- กล่องพิมพ์คำตอบ ----
    draw_card(surface, ANS_BOX, radius=12, border=ORANGE)
    user_txt = font_btn.render(game.user_input, True, NAVY)
    surface.blit(user_txt, (ANS_BOX.x + ANS_PADDING, ANS_BOX.y + 8))
    if not game.locked and int(time.time() * 2) % 2 == 0:             # เคอร์เซอร์กะพริบ
        cx = ANS_BOX.x + ANS_PADDING + user_txt.get_width() + 2
        pygame.draw.line(surface, ORANGE, (cx, ANS_BOX.y + 10), (cx, ANS_BOX.bottom - 10), 2)

    btn_reset = Button(480, 245, 80, 45, "ล้าง", font_btn, bg_color=LIGHT_BLUE, text_color=NAVY)
    btn_reset.draw(surface)
    buttons["reset"] = btn_reset

    can_hint = not game.hint_used_this_q and game.hints_left > 0
    btn_hint = Button(570, 245, 90, 45, "คำใบ้", font_btn, bg_color=YELLOW, text_color=NAVY, enabled=can_hint)
    btn_hint.draw(surface)
    buttons["hint"] = btn_hint

    btn_submit = Button(670, 245, 90, 45, "ยืนยัน", font_btn, bg_color=GREEN, text_color=WHITE)
    btn_submit.draw(surface)
    buttons["submit"] = btn_submit

    # ---- แป้นพิมพ์แบบ iPhone ----
    draw_card(surface, pygame.Rect(30, 296, 740, 214), color=PANEL, radius=20)
    for r_idx, row in enumerate(keyboard_layout):
        row_x = KEY_X0 + KEY_ROW_SHIFT[r_idx]
        for c_idx, char in enumerate(row):
            btn_key = Button(row_x + c_idx * KEY_STEP, KEY_Y0 + r_idx * KEY_ROW_STEP,
                             KEY_W, KEY_H, char, font_btn, bg_color=_key_color(char), radius=10)
            btn_key.draw(surface)
            buttons[f"key_{char}"] = btn_key

    # แถวล่าง: Shift อยู่ซ้าย ปุ่มลบอยู่ขวา เหมือน iPhone (Shift สีฟ้า = กำลังเปิดอยู่)
    bottom_y = KEY_Y0 + 3 * KEY_ROW_STEP
    bottom_x = KEY_X0 + KEY_ROW_SHIFT[3]
    btn_shift = Button(bottom_x - SIDE_KEY_W - 8, bottom_y, SIDE_KEY_W, KEY_H, "Shift", font_small,
                       bg_color=BLUE if shift_on else GRAY, text_color=WHITE, radius=10)
    btn_shift.draw(surface)
    buttons["shift"] = btn_shift

    last_key_end = bottom_x + (len(keyboard_layout[3]) - 1) * KEY_STEP + KEY_W
    btn_back = Button(last_key_end + 8, bottom_y, SIDE_KEY_W, KEY_H, "ลบ", font_small,
                      bg_color=GRAY, text_color=WHITE, radius=10)
    btn_back.draw(surface)
    buttons["backspace"] = btn_back

    # ---- แถบแจ้งผล (ทับกล่องรูป) ----
    if game.reveal is not None:
        result = game.reveal["result"]
        if result == "correct":
            title, color = "ถูกต้อง!", GREEN
        elif result == "timeout":
            title, color = "หมดเวลา!", RED
        else:
            title, color = "ผิด! หมดโอกาสตอบ", RED
        _draw_banner(surface, font_title, font_btn, title, f"คำตอบคือ: {game.reveal['answer']}",
                     color, game.reveal_start, shake=(result != "correct"))
    elif game.flash_message():
        _draw_banner(surface, font_title, font_btn, game.flash_message(), None, RED,
                     game.flash_until - FLASH_SECONDS, shake=True)

    return buttons


# ---------------- กล่องยืนยันออกจากเกม ----------------
def draw_exit_modal(surface, font_btn):
    overlay = pygame.Surface(surface.get_size())
    overlay.fill((10, 25, 50))
    overlay.set_alpha(160)
    surface.blit(overlay, (0, 0))

    modal_rect = pygame.Rect(240, 190, 320, 190)
    draw_card(surface, modal_rect, radius=20, border=ORANGE)
    draw_text(surface, "จะออกจากเกมจริงๆ เหรอ?", font_btn, NAVY, (400, 240), shadow=False)

    btn_yes = Button(270, 295, 120, 50, "ออกเลย", font_btn, bg_color=RED, text_color=WHITE)
    btn_no = Button(410, 295, 120, 50, "เล่นต่อ", font_btn, bg_color=GREEN, text_color=WHITE)
    btn_yes.draw(surface)
    btn_no.draw(surface)

    return {"yes": btn_yes, "no": btn_no}


# ---------------- หน้าสรุปคะแนน ----------------
def draw_summary_screen(surface, font_title, font_btn, game):
    draw_background(surface)
    draw_text(surface, "จบเกม!", get_font(48), WHITE, (400, 60))

    box = pygame.Rect(150, 110, 500, 240)
    draw_card(surface, box, radius=22)

    # ดาว 0-3 ดวงตามคะแนน
    ratio = game.score / game.total_questions if game.total_questions else 0
    stars = 3 if ratio == 1 else 2 if ratio >= 0.6 else 1 if ratio > 0 else 0
    for i in range(3):
        center = (320 + i * 80, 165 - (12 if i == 1 else 0))
        filled = i < stars
        draw_star(surface, center, 32, YELLOW if filled else (225, 230, 235), outline=_shade(ORANGE, 0.9) if filled else GRAY)

    draw_text(surface, f"หมวด {game.category}  |  ระดับ {game.difficulty}", font_btn, NAVY, (400, 230), shadow=False)
    draw_text(surface, f"ได้ {game.score} / {game.total_questions} คะแนน", get_font(40), ORANGE, (400, 290), shadow=False)

    btn_replay = Button(190, 390, 200, 65, "เล่นซ้ำอีกครั้ง", font_btn, bg_color=ORANGE, text_color=WHITE, radius=18)
    btn_home = Button(410, 390, 200, 65, "กลับหน้าหลัก", font_btn, bg_color=BLUE, text_color=WHITE, radius=18)
    btn_replay.draw(surface)
    btn_home.draw(surface)

    return {"replay": btn_replay, "home": btn_home}