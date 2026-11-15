import os
import pygame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_DIR = os.path.join(BASE_DIR, "sounds")
EXTENSIONS = (".wav", ".ogg", ".mp3")

# ชื่อไฟล์เสียงเอฟเฟกต์ : ความดัง (0.0 - 1.0)
SFX_VOLUME = {
    "hover": 0.25,      # เมาส์ชี้ปุ่ม
    "click": 0.6,       # กดปุ่ม
    "correct": 0.7,     # ตอบถูก
    "wrong": 0.7,       # ตอบผิด / หมดเวลา
    "countdown": 0.6,   # นับถอยหลัง 3-2-1
    "finish": 0.7,      # จบเกม หน้าสรุปคะแนน
}
MUSIC_NAME = "bgm"      # เพลงพื้นหลัง (เล่นวนตลอด)
MUSIC_VOLUME = 0.35

_sounds = {}
_ready = False


def _find(name):
    """หาไฟล์ชื่อนี้ในโฟลเดอร์ sounds/ ลองทุกนามสกุลที่รองรับ"""
    for ext in EXTENSIONS:
        path = os.path.join(SOUND_DIR, name + ext)
        if os.path.isfile(path):
            return path
    return None


def init():
    """โหลดเสียงทั้งหมด เรียกครั้งเดียวหลัง pygame.init()"""
    global _ready
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        _ready = True
    except pygame.error:
        _ready = False          # เครื่องไม่มีลำโพง/การ์ดเสียง ก็เล่นเกมต่อได้
        return
    for name, volume in SFX_VOLUME.items():
        path = _find(name)
        if path:
            try:
                sound = pygame.mixer.Sound(path)
                sound.set_volume(volume)
                _sounds[name] = sound
            except pygame.error:
                pass


def play(name):
    sound = _sounds.get(name)
    if sound:
        sound.play()


def play_music():
    if not _ready:
        return
    path = _find(MUSIC_NAME)
    if not path:
        return
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        pygame.mixer.music.play(-1)     # -1 = เล่นวนไม่หยุด
    except pygame.error:
        pass
