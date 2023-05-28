from math import atan2, pi, sqrt
from operator import attrgetter
from typing import List, Optional, Union

Number = Union[int, float]

WIDTH: int = 17630
HEIGHT: int = 9000
POSITION = [
    [6710, 2200],
    [5555, 5555],
    [2200, 6710],
]


class Point:
    def __init__(self, x: Number, y: Number):
        self.x = max(0, min(round(x), WIDTH))
        self.y = max(0, min(round(y), HEIGHT))

    def __str__(self):
        return f"({self.x}, {self.y})"


class Base:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.side = [0, 1][self.y > 4500]
        self.health = 0
        self.mana = 0
        self.has_mana = self.mana >= 10
        self.has_more_mana = self.mana >= 50

    def update(self, health: int, mana: int):
        self.health = health
        self.mana = mana
        self.has_mana = self.mana >= 10
        self.has_more_mana = self.mana >= 50

    def spell(self):
        self.mana -= 10
        self.has_mana = self.mana >= 10
        self.has_more_mana = self.mana >= 50


class Monster:
    def __init__(self, entity_id: int, x: int, y: int, shield: int, is_controlled, health: int, vx: int, vy: int, near_base: int, base: Base):
        self.id = entity_id
        self.x = x if base.side == 0 else WIDTH - x
        self.y = y if base.side == 0 else HEIGHT - y
        self.shield = shield
        self.is_controlled = is_controlled == 1
        self.health = health
        self.vx = vx if base.side == 0 else -vx
        self.vy = vy if base.side == 0 else -vy
        self.near_base = near_base == 1
        self.distance = sqrt(self.x ** 2 + self.y ** 2)
        self.argument = atan2(self.y, self.x)
        self.next_point = Point(self.x + self.vx, self.y + self.vy)
        self.in_base = self.distance < 6000
        self.is_threat = self.distance < 3000
        self.targeting = self.vx < 0 and self.vy < 0
        self.is_controlling = self.is_controlled and not self.targeting


class Enemy:
    def __init__(self, entity_id: int, x: int, y: int, shield, is_controlled, base: Base):
        self.id = entity_id
        self.x = x if base.side == 0 else WIDTH - x
        self.y = y if base.side == 0 else HEIGHT - y
        self.shield = shield
        self.is_controlled = is_controlled == 1
        self.base = base
        self.distance = sqrt(self.x ** 2 + self.y ** 2)


class Hero:
    _count: int = 0

    def __init__(self, x: int, y: int, base: Base):
        self.id = Hero._count
        self.x = x if base.side == 0 else WIDTH - x
        self.y = y if base.side == 0 else HEIGHT - y
        self.base = base
        self.px = POSITION[self.id][0]
        self.py = POSITION[self.id][1]
        Hero._count += 1

    def update(self, x: int, y: int):
        self.x = x if self.base.side == 0 else WIDTH - x
        self.y = y if self.base.side == 0 else HEIGHT - y

    def distance(self, x: Optional[Number], y: Optional[Number]) -> float:
        if x is None:
            x = 0 if self.base.side == 0 else WIDTH
        if y is None:
            y = 0 if self.base.side == 0 else HEIGHT
        dx = x - self.x
        dy = y - self.y
        return sqrt(dx ** 2 + dy ** 2)

    def within_range(self, target: Monster) -> bool:
        return self.distance(target.x, target.y) < 1000

    def get_action(self, monsters: List[Monster], enemies: List[Enemy]) -> str:
        # 担当エリア
        left = self.id * pi / 8
        right = left + pi / 4
        # 対応すべきモンスター
        # ・自分の守備範囲内にいる（自陣内 or 担当エリア内）
        # ・自陣を狙っている
        # ・自チームがコントロール中でない
        targets = [monster for monster in monsters
                   if (monster.in_base or left <= monster.argument <= right)
                   and monster.targeting
                   and not monster.is_controlling
                   ]
        # 対応すべき相手チームのヒーロー
        # ・コントロールされていない
        # ・シールドされていない
        enemies = [enemy for enemy in enemies if not enemy.is_controlled and enemy.shield == 0]
        enemy = min(enemies, key=attrgetter("distance")) if enemies else None

        if not targets:
            # 対応すべきモンスターがいない場合
            if enemy and self.base.has_more_mana:
                # 対応すべき相手チームヒーローがいて、マナに余裕がある場合は相手チームヒーローを相手陣地に戻す
                return self.control(enemy)
            # そうでない場合は定位置に戻る
            return self.move(Point(self.px, self.py))

        # 対応すべきモンスターのうちもっとも自陣に近いものをターゲットとする
        target = min(targets, key=attrgetter("distance"))
        # ターゲットが自陣内にいてシールドされている場合は最優先で攻撃する
        if target.in_base and target.shield > 0:
            return self.move(target.next_point)
        # ターゲットが自陣近くまで迫っていて、WIND 圏内にいる場合は WIND する
        if self.base.has_mana and target.is_threat and self.within_range(target):
            return self.wind()
        # マナに余裕がなければ通常攻撃
        if not self.base.has_more_mana:
            return self.move(target.next_point)
        # 近くに相手チームヒーローがいれば相手陣地に戻す
        if enemy:
            return self.control(enemy)
        # ターゲットがシールドされていれば通常攻撃
        if target.shield > 0:
            return self.move(target.next_point)
        # ターゲットが自陣内にいなくて、WIND 圏内に他のモンスターがいない場合は相手陣地に送る
        if not target.in_base and len([t for t in targets if self.within_range(t)]) < 2:
            return self.control(target)
        # ターゲットが WIND 圏内にいれば WIND
        if self.within_range(target):
            return self.wind()
        return self.move(target.next_point)

    def move(self, target: Point) -> str:
        if self.base.side == 0:
            return f"MOVE {target.x} {target.y}"
        else:
            return f"MOVE {WIDTH - target.x} {HEIGHT - target.y}"

    def wind(self) -> str:
        self.base.spell()
        if self.base.side == 0:
            return f"SPELL WIND {WIDTH} {HEIGHT}"
        else:
            return f"SPELL WIND 0 0"

    def control(self, target: Union[Monster, Enemy]) -> str:
        self.base.spell()
        target.is_controlling = True
        if self.base.side == 0:
            return f"SPELL CONTROL {target.id} {WIDTH} {HEIGHT}"
        else:
            return f"SPELL CONTROL {target.id} 0 0"


def main():
    base_x, base_y = map(int, input().split())
    base = Base(base_x, base_y)
    _ = int(input())
    heroes = {}
    while True:
        my_health, my_mana = map(int, input().split())
        base.update(my_health, my_mana)
        _ = map(int, input().split())
        entity_count = int(input())
        monsters = []
        enemies = []
        for _ in range(entity_count):
            entity_id, entity_type, x, y, shield_life, is_controlled, health, vx, vy, near_base, _ = map(int, input().split())
            if entity_type == 0:
                monsters.append(Monster(entity_id, x, y, shield_life, is_controlled, health, vx, vy, near_base, base))
            elif entity_type == 1:
                if entity_id not in heroes:
                    heroes[entity_id] = Hero(x, y, base)
                else:
                    heroes[entity_id].update(x, y)
            elif entity_type == 2:
                enemies.append(Enemy(entity_id, x, y, shield_life, is_controlled, base))
        for hero in sorted(heroes.values(), key=attrgetter('id')):
            print(hero.get_action(monsters, enemies))


if __name__ == '__main__':
    main()
