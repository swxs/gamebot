from main import handler
from dags.dag import Node

def start():
    # 开始
    return handler.find_ellement_and_click('buttons/start.png', sens=0.6)


def choose_party():
    # 选择队伍
    return handler.find_ellement_and_click('buttons/start1.png', sens=0.4)


def first_time_choose():
    # 第一次选择需要确认
    return handler.find_ellement_and_click('buttons/submit.png', sens=0.7)


def start_battle():
    # 开始副本
    return handler.find_ellement_and_click('buttons/play.png', sens=0.6)


def play_hero():
    # 放下英雄
    return handler.find_ellement_and_click('buttons/hero_0_2.png', sens=0.5)


def use_skill():
    # 使用技能
    return handler.find_ellement_and_click('heroes/11.Ragnaros/skill_2.png', sens=0.6)


def finish_turn():
    # 结束回合
    return handler.find_ellement_and_click('buttons/startbattle.png', sens=0.5)


def victory():
    # 胜利
    return handler.find_ellement_and_click('chekers/win.png', sens=0.65)


def choose_treasure():
    # 选择宝藏
    result = handler.find_ellement_and_click('UI_ellements/PickOneTreasure.png', sens=0.6, tmp_x=0, tmp_y=200)
    if result:
        return handler.find_ellement_and_click('buttons/take.png', sens=0.6)
    else:
        return False


def replace_treasure():
    # 替换宝藏
    result = handler.find_ellement_and_click('UI_ellements/KeepOrReplaceTreasurepng.png', sens=0.6, tmp_x=0, tmp_y=200)
    if result:
        return handler.find_ellement_and_click('buttons/replace.png', sens=0.6)
    else:
        return False


def visit():
    # 治疗
    result = handler.find_ellement_and_click('UI_ellements/bat4.png', speed=0.5, sens=0.7)
    if result:
        return handler.find_ellement_and_click('buttons/visit.png', speed=0.5, sens=0.6)
    else:
        return False


def find_next_battle():
    # 绿色对手
    result = handler.find_ellement_and_click('UI_ellements/bat2.png', speed=0.5, sens=0.6, tmp_y=100)
    if result:
        can_click = handler.find_ellement_and_click('buttons/play.png', speed=0.5, sens=0.6, click=False)
        if can_click:
            return True

    # 红色对手
    result = handler.find_ellement_and_click('UI_ellements/bat1.png', speed=0.5, sens=0.6, tmp_y=100)
    if result:
        can_click = handler.find_ellement_and_click('buttons/play.png', speed=0.5, sens=0.6, click=False)
        if can_click:
            return True

    # 蓝色对手
    result = handler.find_ellement_and_click('UI_ellements/bat3.png', speed=0.5, sens=0.6, tmp_y=100)
    if result:
        can_click = handler.find_ellement_and_click('buttons/play.png', speed=0.5, sens=0.6, click=False)
        if can_click:
            return True

    return False


def get_presents():
    # 拿宝箱
    return handler.find_ellement_and_click('UI_ellements/presents_thing.png', sens=0.6)


def finish_presents():
    # 结束领奖
    return handler.find_ellement_and_click('buttons/done.png', sens=0.5)


def finish():
    # 结束
    return handler.find_ellement_and_click('buttons/finishok.png', sens=0.7)


start = Node("start", start)
choose_party = Node("choose_party", choose_party)
first_time_choose = Node("first_time_choose", first_time_choose)
start_battle = Node("start_battle", start_battle)
play_hero = Node("play_hero", play_hero)
use_skill = Node("use_skill", use_skill)
finish_turn = Node("finish_turn", finish_turn)
victory = Node("victory", victory)
visit = Node("visit", visit)
find_next_battle = Node("find_next_battle", find_next_battle)
choose_treasure = Node("choose_treasure", choose_treasure)
replace_treasure = Node("replace_treasure", replace_treasure)
get_presents = Node("get_presents", get_presents)
finish_presents = Node("finish_presents", finish_presents)
finish = Node("finish", finish)