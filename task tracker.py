import ui
from datetime import datetime, timedelta
import json
import os

# 保存フォルダとファイルのパス
SAVE_FOLDER = os.path.expanduser('~/Documents/habit_data')
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)
DATA_FILE = os.path.join(SAVE_FOLDER, 'habits.json')

def load_habits():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_habits(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

habits_data = load_habits()

# UI設定
BG_COLOR = '#E0E5EC'
TEXT_COLOR = '#333333'
SHADOW_COLOR = '#A3B1C6'
DEVICE_WIDTH = 390
DEVICE_HEIGHT = 844
WEEKDAYS = ['日', '月', '火', '水', '木', '金', '土']

main_view = ui.View(frame=(0, 0, DEVICE_WIDTH, DEVICE_HEIGHT))
main_view.background_color = BG_COLOR

# ===== ニューモーフィズム風ビュー作成関数 =====
def create_neumorphic_view(frame, corner_radius=10):
    container = ui.View(frame=frame, background_color=BG_COLOR)
    
    # 明るい影(上・左)
    light_shadow = ui.View(frame=(-3, -3, frame[2], frame[2]))
    light_shadow.background_color = '#dee4ff'
    light_shadow.corner_radius = corner_radius
    light_shadow.alpha = 2
    container.add_subview(light_shadow)
    
    # 暗い影(下・右)
    dark_shadow = ui.View(frame=(3, 3, frame[2], frame[2]))
    dark_shadow.background_color = SHADOW_COLOR
    dark_shadow.corner_radius = corner_radius
    dark_shadow.alpha = 2
    container.add_subview(dark_shadow)
    
    
    # メインビュー
    main = ui.View(frame=(0, 0, frame[2], frame[3]))
    main.background_color = BG_COLOR
    main.corner_radius = corner_radius
    container.add_subview(main)
    
    return container, main

# ===== ヘッダー =====
header = ui.View(frame=(0, 0, DEVICE_WIDTH, 60), background_color=BG_COLOR)

def add_neumo_button(title, x, action=None):
    container, inner = create_neumorphic_view((x, 15, 40, 40))
    btn = ui.Button(title=title)
    btn.frame = (0, 0, 40, 40)
    btn.tint_color = TEXT_COLOR
    btn.background_color = BG_COLOR
    btn.corner_radius = 10
    btn.action = action
    inner.add_subview(btn)
    header.add_subview(container)
    return btn

menu_btn = add_neumo_button('≡', 10)
search_btn = add_neumo_button('🔍', DEVICE_WIDTH - 90)
settings_btn = add_neumo_button('⚙️', DEVICE_WIDTH - 45)

title_label = ui.Label(frame=(60, 15, DEVICE_WIDTH - 120, 30))
title_label.text = '習慣トラッカー'
title_label.alignment = ui.ALIGN_CENTER
title_label.text_color = TEXT_COLOR
title_label.font = ('<system>', 18)
header.add_subview(title_label)
main_view.add_subview(header)

# ===== タスク入力欄 =====
start_y = 80
row_height = 50
date_fields = []

for i in range(7):
    day = datetime.now() + timedelta(days=i)
    date_str = day.strftime('%Y-%m-%d')
    label_text = day.strftime('%m/%d') + f'\n({WEEKDAYS[day.weekday()]})'
    y = start_y + i * row_height

    date_label = ui.Label(frame=(10, y, 60, row_height))
    date_label.text = label_text
    date_label.number_of_lines = 2
    date_label.alignment = ui.ALIGN_CENTER
    date_label.font = ('<system>', 12)
    date_label.text_color = TEXT_COLOR
    main_view.add_subview(date_label)

    # 入力欄
    task_container, task_inner = create_neumorphic_view((80, y + 10, 200, 30), corner_radius=8)
    task_field = ui.TextField(frame=(0, 0, 200, 30))
    task_field.placeholder = '習慣を入力'
    task_field.font = ('<system>', 12)
    task_field.text_color = TEXT_COLOR
    task_field.border_width = 0
    task_field.background_color = BG_COLOR
    task_inner.add_subview(task_field)
    main_view.add_subview(task_container)

    # スイッチ
    # ✅ スイッチ(影なし)
    sw = ui.Switch(frame=(300, y + 10, 50, 30))
    sw.name = f'{date_str}'
    sw.tint_color = '#34C759'
    sw.bg_color = 'clear'  # 背景透明(好みに応じて)
    main_view.add_subview(sw)

    date_fields.append((date_str, task_field, sw))

# ===== 保存済み表示エリア =====
scroll_view = ui.ScrollView(frame=(0, 450, DEVICE_WIDTH, 350))
scroll_view.background_color = BG_COLOR
main_view.add_subview(scroll_view)

def toggle_switch(sender):
    key = sender.name
    habits_data[key] = sender.value
    save_habits(habits_data)
    sender.bg_color = '#A0E8AF' if sender.value else '#EEE'
    update_stats()

def create_task_row(date_str, task_text, y, done=False):
    task_label = ui.Label(frame=(20, y, 200, 30))
    task_label.text = f'{date_str} {task_text}'
    task_label.font = ('<system>', 14)
    task_label.text_color = '#222'
    scroll_view.add_subview(task_label)

    sw = ui.Switch(frame=(240, y, 60, 30))
    sw.value = done
    sw.name = f'{date_str}-{task_text}'
    sw.action = toggle_switch
    sw.bg_color = '#A0E8AF' if done else '#EEE'
    scroll_view.add_subview(sw)

def display_saved_tasks():
    y = 10
    for key, done in habits_data.items():
        if '-' in key:
            date_str, task_text = key.split('-', 1)
            create_task_row(date_str, task_text, y, done)
            y += 50

display_saved_tasks()

# ===== メニュー =====
menu_view = ui.View(frame=(-250, 0, 250, DEVICE_HEIGHT))
menu_view.background_color = BG_COLOR
main_view.add_subview(menu_view)

def toggle_menu(sender):
    def animate():
        menu_view.x = 0 if menu_view.x < 0 else -250
    ui.animate(animate, duration=0.3)

menu_btn.action = toggle_menu

# 統計ラベル
stats_label = ui.Label(frame=(10, 80, 230, 150))
stats_label.text_color = TEXT_COLOR
stats_label.number_of_lines = 0
stats_label.font = ('<system>', 14)
menu_view.add_subview(stats_label)

def update_stats():
    this_week = [datetime.now() + timedelta(days=i) for i in range(7)]
    keys_this_week = [f"{d.strftime('%Y-%m-%d')}" for d in this_week]

    total = 0
    completed = 0
    for key, value in habits_data.items():
        for day_key in keys_this_week:
            if key.startswith(day_key):
                total += 1
                if value:
                    completed += 1

    rate = (completed / total * 100) if total > 0 else 0
    stats_label.text = f'📊今週の統計\n\n・合計: {total}件\n・達成: {completed}件\n・達成率: {rate:.1f}%'

update_stats()

# メニューの「閉じる」ボタンもニューモーフィズム化
close_container, close_inner = create_neumorphic_view((10, 30, 40, 40))
close_btn = ui.Button(title='≡')
close_btn.frame = (0, 0, 40, 40)
close_btn.tint_color = TEXT_COLOR
close_btn.background_color = BG_COLOR
close_btn.corner_radius = 10
close_btn.action = toggle_menu
close_inner.add_subview(close_btn)
menu_view.add_subview(close_container)

# 表示
main_view.present('sheet')
