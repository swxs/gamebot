from dag import DAG, Node
from . import nodes

one_one_dag = DAG(name="main")
with one_one_dag as dag:
    first_battle_dag = DAG(name="first_battle_dag")
    battle_dag = DAG(name="battle_dag")
    victory_dag = DAG(name="victory_dag")
    choose_treasure_dag = DAG(name="choose_treasure_dag")
    replace_treasure_dag = DAG(name="replace_treasure_dag")
    visit_dag = DAG(name="visit_dag")
    find_next_battle_dag = DAG(name="find_next_battle_dag")
    finish_dag = DAG(name="finish_dag")

    with first_battle_dag as first_battle_dag:
        first_battle_dag >> nodes.first_time_choose >> battle_dag

    with battle_dag as battle_dag:
        battle_dag >> nodes.start_battle >> nodes.play_hero >> nodes.use_skill >> nodes.finish_turn >> [victory_dag, nodes.use_skill]

    with victory_dag as victory_dag:
        victory_dag >> nodes.victory >> [choose_treasure_dag, replace_treasure_dag, finish_dag]

    with visit_dag as visit_dag:
        visit_dag >> nodes.visit >> find_next_battle_dag

    with find_next_battle_dag as find_next_battle_dag:
        find_next_battle_dag >> nodes.find_next_battle >> battle_dag

    with choose_treasure_dag as choose_treasure_dag:
        choose_treasure_dag >> nodes.choose_treasure >> [battle_dag, visit_dag, find_next_battle_dag]

    with replace_treasure_dag as replace_treasure_dag:
        replace_treasure_dag >> nodes.replace_treasure >> [battle_dag, visit_dag, find_next_battle_dag]

    with finish_dag as finish_dag:
        finish_dag >> nodes.get_presents >> nodes.get_presents >> nodes.finish_presents >> nodes.finish

    dag >> nodes.start >> nodes.choose_party >> battle_dag
