from dags.dag import DAG, Node
import random
import time


def start(handler, hwnd):
    time.sleep(0.3)
    print("start")
    return True


def choose_party(handler, hwnd):
    time.sleep(0.3)
    print("choose_party")
    return True


def first_time_choose(handler, hwnd):
    time.sleep(0.3)
    print("first_time_choose")
    return random.random() > 0.5


def start_battle(handler, hwnd):
    time.sleep(0.3)
    print("start_battle")
    return random.random() > 0.8


def play_hero(handler, hwnd):
    time.sleep(0.3)
    print("play_hero")
    return random.random() > 0.2


def use_skill(handler, hwnd):
    time.sleep(0.3)
    print("use_skill")
    return random.random() > 0.8


def finish_turn(handler, hwnd):
    time.sleep(0.3)
    print("finish_turn")
    return True


def victory(handler, hwnd):
    time.sleep(0.3)
    print("victory")
    return random.random() > 0.5


def visit(handler, hwnd):
    time.sleep(0.3)
    print("visit")
    return True


def find_next_battle(handler, hwnd):
    time.sleep(0.3)
    print("find_next_battle")
    return random.random() > 0.1


def can_battle(handler, hwnd):
    time.sleep(0.3)
    print("can_battle")
    return random.random() > 0.1


def choose_treasure(handler, hwnd):
    time.sleep(0.3)
    print("choose_treasure")
    return random.random() > 0.5


def replace_treasure(handler, hwnd):
    time.sleep(0.3)
    print("replace_treasure")
    return random.random() > 0.5


def get_presents(handler, hwnd):
    time.sleep(0.3)
    print("get_presents")
    return random.random() > 0.3


def finish_presents(handler, hwnd):
    time.sleep(0.3)
    print("finish_presents")
    return True


def finish(handler, hwnd):
    time.sleep(0.3)
    print("finish")
    return True


def end(handler, hwnd):
    print("end")
    return True


dag = DAG(name="main")
with dag as dag:
    first_battle_dag = DAG(name="first_battle_dag")
    battle_dag = DAG(name="battle_dag")

    start = Node("start", start)
    choose_party = Node("choose_party", choose_party)
    visit = Node("visit", visit)
    find_next_battle = Node("find_next_battle", find_next_battle)
    can_battle = Node("can_battle", can_battle)
    end = Node("end", end)

    with first_battle_dag as first_battle_dag:
        first_time_choose = Node("first_time_choose", first_time_choose)

        first_battle_dag >> first_time_choose >> battle_dag

    with battle_dag as battle_dag:
        start_battle = Node("start_battle", start_battle)
        play_hero = Node("play_hero", play_hero)
        use_skill = Node("use_skill", use_skill)
        finish_turn = Node("finish_turn", finish_turn)

        victory_dag = DAG(name="victory_dag")

        with victory_dag as victory_dag:
            victory = Node("victory", victory)

            choose_treasure_dag = DAG(name="choose_treasure_dag")
            replace_treasure_dag = DAG(name="replace_treasure_dag")
            finish_dag = DAG(name="finish_dag")

            with choose_treasure_dag as choose_treasure_dag:
                choose_treasure = Node("choose_treasure", choose_treasure)

                choose_treasure_dag >> choose_treasure

            with replace_treasure_dag as replace_treasure_dag:
                replace_treasure = Node("replace_treasure", replace_treasure)

                replace_treasure_dag >> replace_treasure

            with finish_dag as finish_dag:
                get_presents = Node("get_presents", get_presents)
                finish_presents = Node("finish_presents", finish_presents)
                finish = Node("finish", finish)

                finish_dag >> get_presents >> get_presents >> finish_presents >> finish

            victory_dag >> victory >> [choose_treasure_dag, replace_treasure_dag, finish_dag]

        (battle_dag >> start_battle >> play_hero >> use_skill >> finish_turn >> [victory_dag, use_skill])

    battle_dag_1 = battle_dag.copy(name="battle_dag_1")
    battle_dag_2 = battle_dag.copy(name="battle_dag_2")
    battle_dag_3 = battle_dag.copy(name="battle_dag_3")

    (
        dag
        >> start
        >> choose_party
        >> battle_dag_1
        >> visit
        >> find_next_battle
        >> battle_dag_2
        >> can_battle
        >> battle_dag_3
        >> end
    )


if __name__ == "__main__":
    while True:
        for _ in dag:
            print(_)
