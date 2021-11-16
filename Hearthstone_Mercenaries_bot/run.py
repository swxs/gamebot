import os
import time
import cv2
import random
import mss
import pyautogui
import numpy as np

from dag import DAG, Node


BASE_PATH = os.path.abspath(__file__)
BASE_PATH, CURRENT_DIR = os.path.split(BASE_PATH)


def get_file_path(fname):
    return os.path.join(BASE_PATH, "files", "1920x1080", fname)


def screen():
    sct = mss.mss()
    filename = sct.shot(mon=1, output=get_file_path('screen.png'))


def find_ellement(file, speed=0.5, sens=0.4, tmp_x=0, tmp_y=0, click=True):
    try:
        time.sleep(0.5)
        screen()
        img = cv2.imread(get_file_path('screen.png'))
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(get_file_path(file), cv2.IMREAD_GRAYSCALE)
        w, h = template.shape[::-1]
        print(w, h)
        result = cv2.matchTemplate(gray_img, template, cv2.TM_CCOEFF_NORMED)

        loc = np.where(result >= sens)
        if len(loc[0]) != 0:
            pt = random.choice(list(zip(*loc[::-1])))
            x = int((pt[0] * 2 + w + tmp_x) / 2)
            y = int((pt[1] * 2 + h + tmp_y) / 2)
            print("Found " + file, x, y)
            pyautogui.moveTo(x, y, speed, pyautogui.easeInOutQuad)
            time.sleep(0.2)
            if click:
                pyautogui.click()
            return True
        else:
            print(f"Not found: {file}")
            return False
    except Exception as e:
        print(e)
        return False


def start():
    # 开始
    return find_ellement('buttons/start.png', sens=0.6)


def choose_party():
    # 选择队伍
    return find_ellement('buttons/start1.png', sens=0.4)


def first_time_choose():
    # 第一次选择需要确认
    return find_ellement('buttons/submit.png', sens=0.7)


def start_battle():
    # 开始副本
    return find_ellement('buttons/play.png', sens=0.6)


def play_hero():
    # 放下英雄
    return find_ellement('buttons/hero_0_2.png', sens=0.5)


def use_skill():
    # 使用技能
    return find_ellement('heroes/11.Ragnaros/skill_2.png', sens=0.6)


def finish_turn():
    # 结束回合
    return find_ellement('buttons/startbattle.png', sens=0.5)


def victory():
    # 胜利
    return find_ellement('chekers/win.png', sens=0.65)


def choose_treasure():
    # 选择宝藏
    result = find_ellement('UI_ellements/PickOneTreasure.png', sens=0.6, tmp_x=0, tmp_y=200)
    if result:
        return find_ellement('buttons/take.png', sens=0.6)
    else:
        return False


def replace_treasure():
    # 替换宝藏
    result = find_ellement('UI_ellements/KeepOrReplaceTreasurepng.png', sens=0.6, tmp_x=0, tmp_y=200)
    if result:
        return find_ellement('buttons/replace.png', sens=0.6)
    else:
        return False


def visit():
    # 治疗
    result = find_ellement('UI_ellements/bat4.png', speed=0.5, sens=0.7)
    if result:
        return find_ellement('buttons/visit.png', speed=0.5, sens=0.6)
    else:
        return False


def find_next_battle():
    # 绿色对手
    result = find_ellement('UI_ellements/bat2.png', speed=0.5, sens=0.6, tmp_y=100)
    if result:
        can_click = find_ellement('buttons/play.png', speed=0.5, sens=0.6, click=False)
        if can_click:
            return True

    # 红色对手
    result = find_ellement('UI_ellements/bat1.png', speed=0.5, sens=0.6, tmp_y=100)
    if result:
        can_click = find_ellement('buttons/play.png', speed=0.5, sens=0.6, click=False)
        if can_click:
            return True

    # 蓝色对手
    result = find_ellement('UI_ellements/bat3.png', speed=0.5, sens=0.6, tmp_y=100)
    if result:
        can_click = find_ellement('buttons/play.png', speed=0.5, sens=0.6, click=False)
        if can_click:
            return True

    # Boss
    result = find_ellement('UI_ellements/bat5.png', speed=0.5, sens=0.6, tmp_y=100)
    if result:
        can_click = find_ellement('buttons/play.png', speed=0.5, sens=0.6, click=False)
        if can_click:
            return True

    return False


def get_presents():
    # 拿宝箱
    return find_ellement('UI_ellements/presents_thing.png', sens=0.6)


def finish_presents():
    # 结束领奖
    return find_ellement('buttons/done.png', sens=0.5)


def finish():
    # 结束
    return find_ellement('buttons/finishok.png', sens=0.7)


dag = DAG(name="main")
with dag as dag:
    start = Node("start", start)
    choose_party = Node("choose_party", choose_party)

    first_battle_dag = DAG(name="first_battle_dag")
    battle_dag = DAG(name="battle_dag")
    victory_dag = DAG(name="victory_dag")
    choose_treasure_dag = DAG(name="choose_treasure_dag")
    replace_treasure_dag = DAG(name="replace_treasure_dag")
    visit_dag = DAG(name="visit_dag")
    find_next_battle_dag = DAG(name="find_next_battle_dag")
    finish_dag = DAG(name="finish_dag")

    with first_battle_dag as first_battle_dag:
        first_time_choose = Node("first_time_choose", first_time_choose)

        first_battle_dag >> first_time_choose >> battle_dag

    with battle_dag as battle_dag:
        start_battle = Node("start_battle", start_battle)
        play_hero = Node("play_hero", play_hero)
        use_skill = Node("use_skill", use_skill)
        finish_turn = Node("finish_turn", finish_turn)

        battle_dag >> start_battle >> play_hero >> use_skill >> finish_turn >> [victory_dag, use_skill]

    with victory_dag as victory_dag:
        victory = Node("victory", victory)

        victory_dag >> victory >> [choose_treasure_dag, replace_treasure_dag, finish_dag]

    with visit_dag as visit_dag:
        visit = Node("visit", visit)

        visit_dag >> visit >> find_next_battle_dag

    with find_next_battle_dag as find_next_battle_dag:
        find_next_battle = Node("find_next_battle", find_next_battle)

        find_next_battle_dag >> find_next_battle >> battle_dag

    with choose_treasure_dag as choose_treasure_dag:
        choose_treasure = Node("choose_treasure", choose_treasure)

        choose_treasure_dag >> choose_treasure >> [battle_dag, visit_dag, find_next_battle_dag]

    with replace_treasure_dag as replace_treasure_dag:
        replace_treasure = Node("replace_treasure", replace_treasure)

        replace_treasure_dag >> replace_treasure >> [battle_dag, visit_dag, find_next_battle_dag]

    with finish_dag as finish_dag:
        get_presents = Node("get_presents", get_presents)
        finish_presents = Node("finish_presents", finish_presents)
        finish = Node("finish", finish)

        finish_dag >> get_presents >> get_presents >> finish_presents >> finish

    dag >> start >> choose_party >> battle_dag

if __name__ == "__main__":
    while True:
        for _ in dag:
            print(_)
