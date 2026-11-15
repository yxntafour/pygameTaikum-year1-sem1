import random
import time

CATEGORIES = ["สำนวนไทย", "สิ่งของ", "อาหาร", "สถานที่", "กีฬา", "จังหวัด"]

DIFFICULTY = {
    "ง่าย":    {"time": 60, "lives": 3, "hints": 5},
    "ปานกลาง": {"time": 45, "lives": 2, "hints": 3},
    "ยาก":     {"time": 30, "lives": 1, "hints": 1},
}

# คลังโจทย์ (ใส่เพิ่มได้เรื่อยๆ ระบบจะสุ่มมาเล่นรอบละ 5 ข้อ)
# รูป: วางไฟล์ไว้ที่ images/<ชื่อหมวด>/<คำตอบ>_1.png, _2.png, _3.png (ข้อละไม่เกิน 3 รูป)
#      ถ้ายังไม่มีไฟล์ เกมจะแสดงกล่องว่างแทน ไม่ error
QUESTION_BANK = {
    "สำนวนไทย": [
        {"images": ["images/สำนวนไทย/แกะดำ_1.png", "images/สำนวนไทย/แกะดำ_2.png", "images/สำนวนไทย/แกะดำ_3.png"], "answer": "แกะดำ", "syllables": 2, "hint": "คนที่ทำตัวแตกต่างจากคนอื่นในกลุ่ม"},
        {"images": ["images/สำนวนไทย/เข็นครกขึ้นภูเขา_1.png", "images/สำนวนไทย/เข็นครกขึ้นภูเขา_2.png", "images/สำนวนไทย/เข็นครกขึ้นภูเขา_3.png"], "answer": "เข็นครกขึ้นภูเขา", "syllables": 5, "hint": "ทำงานที่ยากลำบากอย่างยิ่งเกินกำลังความสามารถของตน"},
        {"images": ["images/สำนวนไทย/ขวานผ่าซาก_1.png", "images/สำนวนไทย/ขวานผ่าซาก_2.png", "images/สำนวนไทย/ขวานผ่าซาก_3.png"], "answer": "ขวานผ่าซาก", "syllables": 3, "hint": "พูดจาตรงๆ โผงผางไม่เกรงใจใคร"},
        {"images": ["images/สำนวนไทย/กิ้งก่าได้พลอย_1.png", "images/สำนวนไทย/กิ้งก่าได้พลอย_2.png", "images/สำนวนไทย/กิ้งก่าได้พลอย_3.png"], "answer": "กิ้งก่าได้พลอย", "syllables": 4, "hint": "ได้ของมีค่าแต่ไม่รู้คุณค่า"},
        {"images": ["images/สำนวนไทย/ขี่ช้างจับตั๊กแตน_1.png", "images/สำนวนไทย/ขี่ช้างจับตั๊กแตน_2.png", "images/สำนวนไทย/ขี่ช้างจับตั๊กแตน_3.png"], "answer": "ขี่ช้างจับตั๊กแตน", "syllables": 6, "hint": "ใช้ทรัพยากรจำนวนมากเกินความจำเป็นเพื่อทำเรื่องเล็กๆน้อยๆ"},
        {"images": ["images/สำนวนไทย/จับปลาสองมือ_1.png", "images/สำนวนไทย/จับปลาสองมือ_2.png", "images/สำนวนไทย/จับปลาสองมือ_3.png"], "answer": "จับปลาสองมือ", "syllables": 4, "hint": "ทำสองอย่างพร้อมกันจนไม่ได้ดีสักอย่าง"},
    ],
    "สิ่งของ": [
        {"images": ["images/สิ่งของ/กรรไกร_1.png", "images/สิ่งของ/กรรไกร_2.png", "images/สิ่งของ/กรรไกร_3.png"], "answer": "กรรไกร", "syllables": 2, "hint": "เครื่องมือใช้สำหรับตัดกระดาษหรือผ้า"},
        {"images": ["images/สิ่งของ/แปรงสีฟัน_1.png", "images/สิ่งของ/แปรงสีฟัน_2.png", "images/สิ่งของ/แปรงสีฟัน_3.png"], "answer": "แปรงสีฟัน", "syllables": 3, "hint": "ใช้ทำความสะอาดฟันทุกเช้าเย็น"},
        {"images": ["images/สิ่งของ/นาฬิกา_1.png", "images/สิ่งของ/นาฬิกา_2.png", "images/สิ่งของ/นาฬิกา_3.png"], "answer": "นาฬิกา", "syllables": 3, "hint": "เครื่องบอกเวลา"},
        {"images": ["images/สิ่งของ/ตู้เย็น_1.png", "images/สิ่งของ/ตู้เย็น_2.png", "images/สิ่งของ/ตู้เย็น_3.png"], "answer": "ตู้เย็น", "syllables": 2, "hint": "เครื่องใช้ไฟฟ้าสำหรับแช่อาหาร"},
        {"images": ["images/สิ่งของ/พัดลม_1.png", "images/สิ่งของ/พัดลม_2.png", "images/สิ่งของ/พัดลม_3.png"], "answer": "พัดลม", "syllables": 2, "hint": "เครื่องใช้ไฟฟ้ามีใบพัดหมุน คลายร้อน"},
        {"images": ["images/สิ่งของ/โทรทัศน์_1.png", "images/สิ่งของ/โทรทัศน์_2.png", "images/สิ่งของ/โทรทัศน์_3.png"], "answer": "โทรทัศน์", "syllables": 3, "hint": "จอแสดงภาพและเสียง ดูข่าวดูละคร"},
    ],
    "อาหาร": [
        {"images": ["images/อาหาร/ต้มยำกุ้ง_1.png", "images/อาหาร/ต้มยำกุ้ง_2.png", "images/อาหาร/ต้มยำกุ้ง_3.png"], "answer": "ต้มยำกุ้ง", "syllables": 3, "hint": "อาหารไทยรสเปรี้ยวเผ็ด ใส่ตะไคร้ใบมะกรูด"},
        {"images": ["images/อาหาร/ผัดไทย_1.png", "images/อาหาร/ผัดไทย_2.png", "images/อาหาร/ผัดไทย_3.png"], "answer": "ผัดไทย", "syllables": 2, "hint": "เส้นจันท์ใส่กุ้ง ถั่วงอก เต้าหู้"},
        {"images": ["images/อาหาร/ส้มตำ_1.png", "images/อาหาร/ส้มตำ_2.png", "images/อาหาร/ส้มตำ_3.png"], "answer": "ส้มตำ", "syllables": 2, "hint": "อาหารอีสาน ทำจากมะละกอดิบ"},
        {"images": ["images/อาหาร/แกงเขียวหวาน_1.png", "images/อาหาร/แกงเขียวหวาน_2.png", "images/อาหาร/แกงเขียวหวาน_3.png"], "answer": "แกงเขียวหวาน", "syllables": 3, "hint": "แกงกะทิสีเขียว"},
        {"images": ["images/อาหาร/ไข่เจียว_1.png", "images/อาหาร/ไข่เจียว_2.png", "images/อาหาร/ไข่เจียว_3.png"], "answer": "ไข่เจียว", "syllables": 2, "hint": "ตีให้ฟูแล้วทอดในน้ำมันร้อน กินกับข้าว"},
    ],
    "สถานที่": [
        {"images": ["images/สถานที่/วัดพระแก้ว_1.png", "images/สถานที่/วัดพระแก้ว_2.png", "images/สถานที่/วัดพระแก้ว_3.png"], "answer": "วัดพระแก้ว", "syllables": 3, "hint": "อยู่ในพระบรมมหาราชวัง กรุงเทพฯ"},
        {"images": ["images/สถานที่/สนามบิน_1.png", "images/สถานที่/สนามบิน_2.png", "images/สถานที่/สนามบิน_3.png"], "answer": "สนามบิน", "syllables": 3, "hint": "ที่ขึ้นลงของอากาศยาน"},
        {"images": ["images/สถานที่/โรงพยาบาล_1.png", "images/สถานที่/โรงพยาบาล_2.png", "images/สถานที่/โรงพยาบาล_3.png"], "answer": "โรงพยาบาล", "syllables": 4, "hint": "สถานที่รักษาคนป่วย"},
        {"images": ["images/สถานที่/โรงเรียน_1.png", "images/สถานที่/โรงเรียน_2.png", "images/สถานที่/โรงเรียน_3.png"], "answer": "โรงเรียน", "syllables": 2, "hint": "สถานที่ที่นักเรียนไปเรียนหนังสือ"},
        {"images": ["images/สถานที่/สวนสาธารณะ_1.png", "images/สถานที่/สวนสาธารณะ_2.png", "images/สถานที่/สวนสาธารณะ_3.png"], "answer": "สวนสาธารณะ", "syllables": 5, "hint": "สถานที่พักผ่อนและออกกำลังกาย"},
    ],
    "กีฬา": [
        {"images": ["images/กีฬา/ฟุตบอล_1.png", "images/กีฬา/ฟุตบอล_2.png", "images/กีฬา/ฟุตบอล_3.png"], "answer": "ฟุตบอล", "syllables": 2, "hint": "กีฬาใช้เท้าเตะลูกเข้าประตู ทีมละ 11 คน"},
        {"images": ["images/กีฬา/แบดมินตัน_1.png", "images/กีฬา/แบดมินตัน_2.png", "images/กีฬา/แบดมินตัน_3.png"], "answer": "แบดมินตัน", "syllables": 3, "hint": "กีฬาใช้ไม้ตีลูกขนไก่"},
        {"images": ["images/กีฬา/วอลเลย์บอล_1.png", "images/กีฬา/วอลเลย์บอล_2.png", "images/กีฬา/วอลเลย์บอล_3.png"], "answer": "วอลเลย์บอล", "syllables": 3, "hint": "กีฬาใช้มือตบลูกข้ามตาข่าย ทีมละ 6 คน"},
        {"images": ["images/กีฬา/ว่ายน้ำ_1.png", "images/กีฬา/ว่ายน้ำ_2.png", "images/กีฬา/ว่ายน้ำ_3.png"], "answer": "ว่ายน้ำ", "syllables": 2, "hint": "กีฬาแข่งในสระ มีท่าฟรีสไตล์ ท่ากบ"},
        {"images": ["images/กีฬา/บาสเกตบอล_1.png", "images/กีฬา/บาสเกตบอล_2.png", "images/กีฬา/บาสเกตบอล_3.png"], "answer": "บาสเกตบอล", "syllables": 3, "hint": "กีฬาโยนลูกลงห่วง"},
    ],
    "จังหวัด": [
        {"images": ["images/จังหวัด/เชียงใหม่_1.png", "images/จังหวัด/เชียงใหม่_2.png", "images/จังหวัด/เชียงใหม่_3.png"], "answer": "เชียงใหม่", "syllables": 2, "hint": "จังหวัดใหญ่ทางภาคเหนือ มีดอยสุเทพ"},
        {"images": ["images/จังหวัด/ภูเก็ต_1.png", "images/จังหวัด/ภูเก็ต_2.png", "images/จังหวัด/ภูเก็ต_3.png"], "answer": "ภูเก็ต", "syllables": 2, "hint": "เกาะท่องเที่ยวชื่อดังทางภาคใต้"},
        {"images": ["images/จังหวัด/ขอนแก่น_1.png", "images/จังหวัด/ขอนแก่น_2.png", "images/จังหวัด/ขอนแก่น_3.png"], "answer": "ขอนแก่น", "syllables": 2, "hint": "จังหวัดศูนย์กลางภาคอีสาน"},
        {"images": ["images/จังหวัด/ชลบุรี_1.png", "images/จังหวัด/ชลบุรี_2.png", "images/จังหวัด/ชลบุรี_3.png"], "answer": "ชลบุรี", "syllables": 3, "hint": "จังหวัดที่มีบางแสนและพัทยา"},
        {"images": ["images/จังหวัด/กาญจนบุรี_1.png", "images/จังหวัด/กาญจนบุรี_2.png", "images/จังหวัด/กาญจนบุรี_3.png"], "answer": "กาญจนบุรี", "syllables": 5, "hint": "จังหวัดที่มีสะพานข้ามแม่น้ำแคว"},
    ],
}

# แป้นพิมพ์ภาษาไทยเรียงเหมือน iPhone ทุกปุ่ม (มีตัวเลขและสัญลักษณ์ด้วย ไม่มีช่องว่าง)
KEYBOARD_NORMAL = [
    ["ๅ", "/", "-", "ภ", "ถ", "ุ", "ึ", "ค", "ต", "จ", "ข", "ช"],
    ["ๆ", "ไ", "ำ", "พ", "ะ", "ั", "ี", "ร", "น", "ย", "บ", "ล"],
    ["ฟ", "ห", "ก", "ด", "เ", "้", "่", "า", "ส", "ว", "ง"],
    ["ผ", "ป", "แ", "อ", "ิ", "ื", "ท", "ม", "ใ", "ฝ"],
]
KEYBOARD_SHIFT = [
    ["+", "๑", "๒", "๓", "๔", "ู", "฿", "๕", "๖", "๗", "๘", "๙"],
    ["๐", "\"", "ฎ", "ฑ", "ธ", "ํ", "๊", "ณ", "ฯ", "ญ", "ฐ", ","],
    ["ฤ", "ฆ", "ฏ", "โ", "ฌ", "็", "๋", "ษ", "ศ", "ซ", "."],
    ["(", ")", "ฉ", "ฮ", "ฺ", "์", "?", "ฒ", "ฬ", "ฦ"],
]

REVEAL_SECONDS = 1.5   # เวปลาที่ขึ้นผลถูก/ผิด + เฉลย ก่อนไปข้อถัดไป
FLASH_SECONDS = 1.0    # เวลาที่ขึ้นข้อความ "ผิด ลองใหม่" (ตอนยังมีโอกาสเหลือ)

class WordGame:
    def __init__(self, category, difficulty):
        self.category = category
        self.difficulty = difficulty
        self.rules = DIFFICULTY.get(difficulty, DIFFICULTY["ง่าย"])
        self._new_round()

    def _new_round(self):
        """สุ่มโจทย์ 5 ข้อ และรีเซ็ตค่าทั้งรอบ (ใช้ทั้งตอนเริ่มเกมและตอนเล่นซ้ำ)"""
        pool = QUESTION_BANK.get(self.category, QUESTION_BANK["สำนวนไทย"])
        num_questions = min(5, len(pool))      # ถ้าในคลังมีไม่ถึง 5 จะดึงมาเท่าที่มี
        self.questions = random.sample(pool, num_questions)
        self.total_questions = len(self.questions)

        self.q_index = 0
        self.score = 0
        self.hints_left = self.rules["hints"]
        self.finished = False
        self.timer_running = False   # ยังไม่เริ่มจับเวลา จนกว่านับถอยหลัง 3-2-1 จะจบ
        self._init_question()

    def _init_question(self): #โดนเรียกตอนเริ่มข้อใหม่กับตอนเล่นซ้ำ
        self.user_input = ""
        self.lives_left = self.rules["lives"]
        self.hint_used_this_q = False
        self.current_hint_text = ""
        self.q_start_time = time.time()
        self.reveal = None           # ผลของข้อนี้ตอนจบข้อ {"result": ..., "answer": ...}
        self.reveal_start = 0
        self.frozen_time = 0
        self.flash_text = ""         # ข้อความแจ้งตอนตอบผิดแต่ยังมีโอกาส
        self.flash_until = 0

    def start_timer(self):
        """เรียกตอนนับถอยหลัง 3-2-1 จบ ถึงจะเริ่มนับเวลาข้อแรก"""
        self.timer_running = True
        self.q_start_time = time.time()

    @property
    def current_q(self):
        return self.questions[self.q_index]

    @property
    def locked(self):
        """True = ตอนนี้กดอะไรไม่ได้ (กำลังขึ้นผล หรือยังไม่เริ่มจับเวลา)"""
        return self.reveal is not None or not self.timer_running

    def time_left(self):
        if not self.timer_running:
            return self.rules["time"]
        if self.reveal is not None:
            return self.frozen_time          # หยุดเวลาไว้ตอนขึ้นผล
        elapsed = time.time() - self.q_start_time
        return max(0, int(self.rules["time"] - elapsed))

    def flash_message(self):
        return self.flash_text if time.time() < self.flash_until else ""

    def _end_question(self, result):
        """จบข้อนี้: เก็บผลไว้ให้ UI แสดง ยังไม่เปลี่ยนข้อจนกว่าจะครบ REVEAL_SECONDS"""
        self.frozen_time = self.time_left()
        self.reveal = {"result": result, "answer": self.current_q["answer"]}
        self.reveal_start = time.time()
        self.flash_text = ""

    def update(self):
        """ฝั่ง UI เรียกทุกเฟรม"""
        if self.finished:
            return None
        if self.reveal is not None:
            if time.time() - self.reveal_start >= REVEAL_SECONDS:
                self.next_question()
                return "next"
            return None
        if self.timer_running and self.time_left() <= 0:
            self._end_question("timeout")    # เวลาหมด = จบข้อทันที นับว่าผิด
            return "timeout"
        return None

    def add_letter(self, char):
        # ไม่จำกัดความยาวตามคำตอบ ฝั่ง UI จะเช็กเองว่าข้อความยังไม่ล้นกล่อง
        if not self.locked:
            self.user_input += char

    def backspace(self):
        """ลบตัวอักษรตัวสุดท้าย"""
        if not self.locked:
            self.user_input = self.user_input[:-1]

    def reset_input(self):
        if not self.locked:
            self.user_input = ""

    def use_hint(self):
        if not self.locked and not self.hint_used_this_q and self.hints_left > 0:
            self.hints_left -= 1
            self.hint_used_this_q = True
            self.current_hint_text = self.current_q.get("hint", "ไม่มีคำใบ้")
            return True
        return False

    def submit_answer(self):
        if self.locked:
            return None
        if self.user_input == self.current_q["answer"]:
            self.score += 1
            self._end_question("correct")
            return "correct"
        self.lives_left -= 1
        self.user_input = ""
        if self.lives_left <= 0:
            self._end_question("wrong")
            return "out_of_lives"
        self.flash_text = f"ผิด! ลองใหม่ เหลือโอกาส {self.lives_left} ครั้ง"
        self.flash_until = time.time() + FLASH_SECONDS
        return "wrong"

    def next_question(self):
        self.q_index += 1
        if self.q_index >= self.total_questions:
            self.finished = True
            return False
        self._init_question()
        return True

    def replay(self):
        """เมื่อกดปุ่มเล่นซ้ำ ให้สุ่มโจทย์ 5 ข้อใหม่จากคลังเดิม"""
        self._new_round()
