from ..dag import DAG, Node


def start(handler, hwnd):
    # 开始
    return handler.find_ellement_and_click(
        hwnd,
        'buttons/start.png',
        sens=0.6,
    )


def choose_party(handler, hwnd):
    # 选择队伍
    return handler.find_ellement_and_click(
        hwnd,
        'buttons/start1.png',
        sens=0.4,
    )


def first_time_choose(handler, hwnd):
    # 第一次选择需要确认
    return handler.find_ellement_and_click(
        hwnd,
        'buttons/submit.png',
        sens=0.7,
    )


def start_battle(handler, hwnd):
    # 开始副本
    return handler.find_ellement_and_click(
        hwnd,
        'buttons/play.png',
        sens=0.5,
    )


def play_hero(handler, hwnd):
    # 放下英雄
    return handler.find_ellement_and_click(
        hwnd,
        'buttons/hero_0_2.png',
        sens=0.5,
    )


def use_skill(handler, hwnd):
    # 使用技能
    return handler.find_ellement_and_click(
        hwnd,
        'heroes/11.Ragnaros/skill_2.png',
        sens=0.6,
    )


def finish_turn(handler, hwnd):
    # 结束回合
    return handler.find_ellement_and_click(
        hwnd,
        'buttons/startbattle.png',
        sens=0.5,
    )


def victory(handler, hwnd):
    # 胜利
    return handler.find_ellement_and_click(
        hwnd,
        'chekers/win.png',
        sens=0.65,
    )


def choose_treasure(handler, hwnd):
    # 选择宝藏
    result = handler.find_ellement_and_click(
        hwnd,
        'UI_ellements/PickOneTreasure.png',
        sens=0.6,
        tmp_x=0,
        tmp_y=200,
    )
    if result:
        return handler.find_ellement_and_click(
            hwnd,
            'buttons/take.png',
            sens=0.6,
        )
    else:
        return False


def replace_treasure(handler, hwnd):
    # 替换宝藏
    result = handler.find_ellement_and_click(
        hwnd,
        'UI_ellements/KeepOrReplaceTreasurepng.png',
        sens=0.6,
        tmp_x=0,
        tmp_y=200,
    )
    if result:
        return handler.find_ellement_and_click(
            hwnd,
            'buttons/replace.png',
            sens=0.6,
        )
    else:
        return False


def visit(handler, hwnd):
    # 治疗
    result = handler.find_ellement_and_click(
        hwnd,
        'UI_ellements/bat4.png',
        speed=0.5,
        sens=0.7,
    )
    if result:
        return handler.find_ellement_and_click(
            hwnd,
            'buttons/visit.png',
            speed=0.5,
            sens=0.6,
        )
    else:
        return False


def find_next_battle(handler, hwnd):
    # 绿色对手
    result = handler.find_ellement_and_click(
        hwnd,
        'UI_ellements/bat2.png',
        speed=0.5,
        sens=0.6,
        tmp_y=100,
    )
    if result:
        can_click = handler.find_ellement_and_click(
            hwnd,
            'buttons/play.png',
            speed=0.5,
            sens=0.6,
            click=False,
        )
        if can_click:
            return True

    # 红色对手
    result = handler.find_ellement_and_click(
        hwnd,
        'UI_ellements/bat1.png',
        speed=0.5,
        sens=0.6,
        tmp_y=100,
    )
    if result:
        can_click = handler.find_ellement_and_click(
            hwnd,
            'buttons/play.png',
            speed=0.5,
            sens=0.6,
            click=False,
        )
        if can_click:
            return True

    # 蓝色对手
    result = handler.find_ellement_and_click(
        hwnd,
        'UI_ellements/bat3.png',
        speed=0.5,
        sens=0.6,
        tmp_y=100,
    )
    if result:
        can_click = handler.find_ellement_and_click(
            hwnd,
            'buttons/play.png',
            speed=0.5,
            sens=0.6,
            click=False,
        )
        if can_click:
            return True

    return False


def get_presents(handler, hwnd):
    # 拿宝箱
    return handler.find_ellement_and_click(
        hwnd,
        'UI_ellements/presents_thing.png',
        sens=0.6,
    )


def finish_presents(handler, hwnd):
    # 结束领奖
    return handler.find_ellement_and_click(
        hwnd,
        'buttons/done.png',
        sens=0.5,
    )


def finish(handler, hwnd):
    # 结束
    return handler.find_ellement_and_click(
        hwnd,
        'buttons/finishok.png',
        sens=0.7,
    )


one_one_dag = DAG(name="main")
with one_one_dag as dag:
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

    first_battle_dag = DAG(name="first_battle_dag")
    battle_dag = DAG(name="battle_dag")
    victory_dag = DAG(name="victory_dag")
    choose_treasure_dag = DAG(name="choose_treasure_dag")
    replace_treasure_dag = DAG(name="replace_treasure_dag")
    visit_dag = DAG(name="visit_dag")
    find_next_battle_dag = DAG(name="find_next_battle_dag")
    finish_dag = DAG(name="finish_dag")

    with first_battle_dag as first_battle_dag:
        first_battle_dag >> first_time_choose >> battle_dag

    with battle_dag as battle_dag:
        battle_dag >> start_battle >> play_hero >> use_skill >> finish_turn >> [
            victory_dag,
            use_skill,
        ]

    with victory_dag as victory_dag:
        victory_dag >> victory >> [choose_treasure_dag, replace_treasure_dag, finish_dag]

    with visit_dag as visit_dag:
        visit_dag >> visit >> find_next_battle_dag

    with find_next_battle_dag as find_next_battle_dag:
        find_next_battle_dag >> find_next_battle >> battle_dag

    with choose_treasure_dag as choose_treasure_dag:
        choose_treasure_dag >> choose_treasure >> [battle_dag, visit_dag, find_next_battle_dag]

    with replace_treasure_dag as replace_treasure_dag:
        replace_treasure_dag >> replace_treasure >> [battle_dag, visit_dag, find_next_battle_dag]

    with finish_dag as finish_dag:
        finish_dag >> get_presents >> get_presents >> finish_presents >> finish

    dag >> start >> choose_party >> battle_dag
