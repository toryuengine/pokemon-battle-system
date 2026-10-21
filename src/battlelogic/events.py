from dataclasses import dataclass, field
from typing import Optional

# 対戦の経過を表すイベント。Battleが起きた順にBattle.eventsへ積む（対戦中にprintせず、表示・ログ・観測は呼び出し側で作る）
# ここに入るのは真の状態（相手の正確なHP・持ち物のID等）なので、Agentに渡す観測はfactory/agents側で見える情報だけに絞る
#
# kindと、dataに入る値:
#   "switch_in"   場に出た。party_index・pokemon_id・indivisual_id・reason
#                 (reasonは"lead"（対戦開始）/"manual"（手動交代）/"faint"/"u_turn"/"baton_pass"/"forced"（ほえる等）)
#   "turn_start"  ターンの始まり（dataは空）
#   "move"        技を出そうとした。party_index・move_id（選んだ技。わるあがきは-1）
#   "move_result" 技を出した結果。use_moveが返す結果（hit・damage・effectiveness・hit_count等）をそのまま入れる
#   "cant_move"   ねむり・まひ・ひるみ等で行動できなかった。party_index
#   "hp"          HPが変わった。party_index・before・after・max_hp
#   "faint"       瀕死になった。party_index
#   "status"      状態異常（status_condition）が変わった。party_index・before・after
#   "item"        持ち物が変わった（消費・はたきおとす・トリック等）。party_index・before・after（持ち物のID。無ければNone）
#   "ability"     特性が発動し、画面のメッセージで判明した（いかく・プレッシャー・ちくでん等。テクニシャンのように
#                 メッセージが出ない特性は入らない）。party_index・ability_id・
#                 is_original（元の特性か。トレース・へんしんでコピーした特性ならFalse）
#   "item_activate" 持ち物が消費されずに発動し、画面のメッセージで判明した（たべのこし・いのちのたま・きあいのハチマキ等）。
#                 party_index・item_id（消費した・奪われた持ち物は"item"で分かるので、こちらには入れない）
#   "battle_end"  対戦が終わった。winner_side（1/2。引き分け・ターン上限ならNone）・is_draw


@dataclass
class BattleEvent:
    turn: int
    kind: str
    # どちらの側のイベントか（1=trainer1, 2=trainer2）。場全体のイベントならNone
    side: Optional[int] = None
    data: dict = field(default_factory=dict)
