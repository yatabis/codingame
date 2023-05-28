from math import sqrt, pi, cos, sin, atan2
from operator import attrgetter
from typing import List, Union

Number = Union[int, float]

WIDTH: int = 17630
HEIGHT: int = 9000
BASE_RADIUS = 6000
SEARCH_RADIUS = 2200
WIND_RADIUS = 1280


def distance(x1: int, y1: int, x2: int, y2: int) -> float:
    return sqrt((x1 - x2)**2 + (y1 - y2)**2)


class Point:
    def __init__(self, x: Number, y: Number):
        self.x = max(0, min(round(x), WIDTH))
        self.y = max(0, min(round(y), HEIGHT))
        self.distance = distance(self.x, self.y, 0, 0)

    def __str__(self):
        return f"({self.x}, {self.y})"


POSITION = [
    Point(WIDTH - BASE_RADIUS * cos(pi / 4), HEIGHT - BASE_RADIUS * sin(pi / 4)),
    Point(WIDTH - HEIGHT * cos(pi * 3 / 8), HEIGHT - HEIGHT * sin(pi * 3 / 8)),
    Point(WIDTH - HEIGHT * cos(pi / 8), HEIGHT - HEIGHT * sin(pi / 8)),
]


class Base:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.side = [0, 1][self.y > 4500]
        self.health = 0
        self.mana = 0

    def update(self, health: int, mana: int):
        self.health = health
        self.mana = mana

    def spell(self):
        self.mana -= 10

    def has_mana(self):
        return self.mana >= 10


class Monster:
    def __init__(
            self,
            entity_id: int,
            x: int,
            y: int,
            shield: int,
            is_controlled,
            health: int,
            vx: int,
            vy: int,
            base: Base
    ):
        self.id = entity_id
        self.x = x if base.side == 0 else WIDTH - x
        self.y = y if base.side == 0 else HEIGHT - y
        self.shield = shield
        self.is_controlled = is_controlled == 1
        self.health = health
        self.vx = vx if base.side == 0 else -vx
        self.vy = vy if base.side == 0 else -vy
        self.distance = distance(self.x, self.y, WIDTH, HEIGHT)
        self.next_point = Point(self.x + self.vx, self.y + self.vy)


class Enemy:
    def __init__(self, entity_id: int, x: int, y: int, shield, is_controlled, base: Base):
        self.id = entity_id
        self.x = x if base.side == 0 else WIDTH - x
        self.y = y if base.side == 0 else HEIGHT - y
        self.shield = shield
        self.is_controlled = is_controlled == 1


class Command:
    def __init__(self, hero, base: Base):
        self.hero = hero
        self.base = base

    def next_action(self, monsters: List[Monster]) -> str:
        pass

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
        if self.base.side == 0:
            return f"SPELL CONTROL {target.id} {WIDTH} {HEIGHT}"
        else:
            return f"SPELL CONTROL {target.id} 0 0"


class AttackerCommand(Command):
    def __init__(self, hero, base: Base):
        super().__init__(hero, base)
        self.x = hero.x
        self.y = hero.y
        self.dest = POSITION[hero.id]

    def next_action(self, monsters: List[Monster]) -> str:
        wind = [monster for monster in monsters if distance(self.x, self.y, monster.x, monster.y) < WIND_RADIUS]
        if self.base.has_mana() and wind:
            return self.wind()
        target = [monster for monster in monsters if distance(self.x, self.y, monster.x, monster.y) <= SEARCH_RADIUS]
        if not target:
            return self.move(self.dest)
        center = Point(
            (sum(t.x + t.vx for t in target) + self.dest.x) / (len(target) + 1),
            (sum(t.y + t.vy for t in target) + self.dest.y) / (len(target) + 1)
        )
        return self.move(center)


class Hero:
    _count: int = 0

    def __init__(self, x: int, y: int, base: Base):
        self.id = Hero._count
        self.x = x if base.side == 0 else WIDTH - x
        self.y = y if base.side == 0 else HEIGHT - y
        self.base = base
        Hero._count += 1

    def update(self, x: int, y: int):
        self.x = x if self.base.side == 0 else WIDTH - x
        self.y = y if self.base.side == 0 else HEIGHT - y

    def get_action(self, monsters: List[Monster]) -> str:
        return AttackerCommand(self, self.base).next_action(monsters)


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
                monsters.append(Monster(entity_id, x, y, shield_life, is_controlled, health, vx, vy, base))
            elif entity_type == 1:
                if entity_id not in heroes:
                    heroes[entity_id] = Hero(x, y, base)
                else:
                    heroes[entity_id].update(x, y)
            elif entity_type == 2:
                enemies.append(Enemy(entity_id, x, y, shield_life, is_controlled, base))
        for hero in sorted(heroes.values(), key=attrgetter('id')):
            print(hero.get_action(monsters))


if __name__ == '__main__':
    main()
