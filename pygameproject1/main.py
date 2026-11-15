import pygame
import sys
from game_logic import WordGame, CATEGORIES, KEYBOARD_NORMAL, KEYBOARD_SHIFT
import ui_components as ui
import audio

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("เกมทายคำ")
audio.init()          # โหลดเสียงจากโฟลเดอร์ sounds/
audio.play_music()    # เพลงพื้นหลัง เล่นวนตลอด
clock = pygame.time.Clock()

font_title = pygame.font.Font(ui.FONT_PATH, 32)
font_btn = pygame.font.Font(ui.FONT_PATH, 20)
font_small = pygame.font.Font(ui.FONT_PATH, 16)

# ให้ pygame-ce จัดตำแหน่งสระบน/ล่างและวรรณยุกต์ของภาษาไทยให้ถูก ไม่ให้ทับกัน
# (ต้องเรียกก่อน render ตัวหนังสือครั้งแรก)
for f in (font_title, font_btn, font_small):
    try:
        f.set_script("Thai")
    except (AttributeError, pygame.error):
        pass   # pygame เวอร์ชันที่ไม่รองรับ จะข้ามไป

state = "TITLE_SUB"
selected_cat = None
selected_diff = None
cat_offset = 0
countdown_val = 3
countdown_timer = 0
countdown_played = None   # เลขนับถอยหลังล่าสุดที่เล่นเสียงไปแล้ว
show_exit_modal = False
shift_on = False
game = None

running = True
while running:
    ui.begin_frame()      # ใช้เช็กว่าเมาส์เพิ่งเข้าปุ่มใหม่ไหม (เสียง hover)
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    if state == "TITLE_SUB":
        btns = ui.draw_title_subscreen(screen, font_title, font_btn)
        for event in events:
            if btns["start"].is_clicked(event):
                state = "MENU_SUB"

    elif state == "MENU_SUB":
        btns = ui.draw_menu_subscreen(screen, font_title, font_btn, CATEGORIES, cat_offset, selected_cat, selected_diff)
        for event in events:
            if btns["prev_cat"].is_clicked(event):
                cat_offset = max(0, cat_offset - 1)
            elif btns["next_cat"].is_clicked(event):
                cat_offset = min(len(CATEGORIES) - 3, cat_offset + 1)
            elif "go_game" in btns and btns["go_game"].is_clicked(event):
                game = WordGame(selected_cat, selected_diff)
                state = "COUNTDOWN"
                countdown_val = 3
                countdown_played = None
                countdown_timer = pygame.time.get_ticks()
            else:
                for key, btn in btns.items():
                    if btn.is_clicked(event):
                        if key.startswith("cat_"):
                            selected_cat = key.replace("cat_", "")
                        elif key.startswith("diff_"):
                            selected_diff = key.replace("diff_", "")

    elif state == "COUNTDOWN":
        if countdown_played != countdown_val:
            audio.play("countdown")
            countdown_played = countdown_val
        progress = (pygame.time.get_ticks() - countdown_timer) / 1000
        ui.draw_countdown_screen(screen, font_title, font_btn, countdown_val, progress)
        if pygame.time.get_ticks() - countdown_timer >= 1000:
            countdown_val -= 1
            countdown_timer = pygame.time.get_ticks()
            if countdown_val <= 0:
                state = "GAME"
                shift_on = False
                game.start_timer()   # เริ่มจับเวลาข้อแรกหลังนับ 3-2-1 จบ

    elif state == "GAME":
        # อัปเดตเวลาถอยหลัง และเช็คว่าเล่นจบเกมหรือยัง
        result = game.update()
        if result == "timeout":
            audio.play("wrong")
        if game.finished:
            state = "SUMMARY"
            audio.play("finish")
            continue   # เกมจบแล้ว ไม่ต้องวาดหน้าเกมต่อ (กัน IndexError ตอนอ่าน current_q)

        layout = KEYBOARD_SHIFT if shift_on else KEYBOARD_NORMAL
        game_btns = ui.draw_game_screen(screen, font_title, font_btn, font_small, game, layout, shift_on)
        
        if show_exit_modal:
            modal_btns = ui.draw_exit_modal(screen, font_btn)
            for event in events:
                if modal_btns["yes"].is_clicked(event):
                    show_exit_modal = False
                    state = "TITLE_SUB"
                elif modal_btns["no"].is_clicked(event):
                    show_exit_modal = False
        else:
            for event in events:
                if game_btns["close"].is_clicked(event):
                    show_exit_modal = True
                elif game_btns["reset"].is_clicked(event):
                    game.reset_input()
                elif game_btns["hint"].is_clicked(event):
                    game.use_hint()
                elif game_btns["submit"].is_clicked(event):
                    result = game.submit_answer()
                    if result == "correct":
                        audio.play("correct")
                    elif result in ("wrong", "out_of_lives"):
                        audio.play("wrong")
                elif game_btns["shift"].is_clicked(event):
                    shift_on = not shift_on
                elif game_btns["backspace"].is_clicked(event):
                    game.backspace()
                else:
                    for k_name, btn in game_btns.items():
                        if k_name.startswith("key_") and btn.is_clicked(event):
                            char = k_name.replace("key_", "")
                            # พิมพ์ได้จนกว่าข้อความจะยาวสุดกล่อง
                            new_width = font_btn.size(game.user_input + char)[0]
                            if new_width <= ui.ANS_BOX.width - ui.ANS_PADDING * 2:
                                game.add_letter(char)
                            shift_on = False   # กดตัวอักษรแล้ว Shift ปิดเองเหมือน iOS

    elif state == "SUMMARY":
        sum_btns = ui.draw_summary_screen(screen, font_title, font_btn, game)
        for event in events:
            if sum_btns["replay"].is_clicked(event):
                game.replay()
                state = "COUNTDOWN"
                countdown_val = 3
                countdown_played = None
                countdown_timer = pygame.time.get_ticks()
            elif sum_btns["home"].is_clicked(event):
                state = "TITLE_SUB"

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()