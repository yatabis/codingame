from math import sqrt, pi, cos, sin, atan2
from operator import attrgetter, itemgetter
from typing import List, Union

Number = Union[int, float]

WIDTH: int = 17630
HEIGHT: int = 9000
BASE_RADIUS: int = 6000
MONSTER_RADIUS: int = 5000
SEARCH_RADIUS: int = 2200
WIND_RADIUS: int = 1280


def distance(x1: int, y1: int, x2: int, y2: int) -> float:
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


class Point:
    def __init__(self, x: Number, y: Number):
        self.x = max(0, min(round(x), WIDTH))
        self.y = max(0, min(round(y), HEIGHT))
        self.distance = distance(self.x, self.y, 0, 0)


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

    def has_more_mana(self, monsters: List):
        if monsters and min(map(attrgetter("distance"), monsters)) < BASE_RADIUS // 2:
            return self.mana >= 20
        else:
            return self.mana >= 20


class Monster:
    def __init__(self, entity_id: int, x: int, y: int, shield: int, is_controlled, health: int, vx: int, vy: int,
                 near_base: int, base: Base):
        self.id = entity_id
        self.x = x if base.side == 0 else WIDTH - x
        self.y = y if base.side == 0 else HEIGHT - y
        self.shield = shield
        self.is_controlled = is_controlled == 1
        self.health = health
        self.vx = vx if base.side == 0 else -vx
        self.vy = vy if base.side == 0 else -vy
        self.near_base = near_base == 1
        self.distance = distance(self.x, self.y, 0, 0)
        self.distance2 = distance(self.x, self.y, WIDTH, HEIGHT)
        self.argument = atan2(self.y, self.x)
        self.next_point = Point(self.x + self.vx, self.y + self.vy)
        self.in_base = self.distance < 6000
        self.is_threat = self.distance < 3000
        self.targeting = self.vx < 0 and self.vy < 0
        self.is_controlling = self.is_controlled and not self.targeting
        self.effective = True
        self.effective2 = True
        x, y = self.x, self.y
        while True:
            if distance(x, y, 0, 0) <= MONSTER_RADIUS:
                self.effective2 = False
                break
            if distance(x, y, WIDTH, HEIGHT) <= MONSTER_RADIUS:
                self.effective = False
                break
            if x < 0 or WIDTH < x or y < 0 or HEIGHT < y:
                self.effective = False
                self.effective2 = False
                break
            x += self.vx
            y += self.vy

    def behind_point(self) -> Point:
        arg = atan2(HEIGHT - self.next_point.y, WIDTH - self.next_point.x)
        r = distance(self.next_point.x, self.next_point.y, WIDTH, HEIGHT) + 1040
        return Point(WIDTH - r * cos(arg), HEIGHT - r * sin(arg))


class Enemy:
    def __init__(self, entity_id: int, x: int, y: int, shield, is_controlled, base: Base):
        self.id = entity_id
        self.x = x if base.side == 0 else WIDTH - x
        self.y = y if base.side == 0 else HEIGHT - y
        self.shield = shield
        self.is_controlled = is_controlled == 1
        self.base = base
        self.distance = distance(self.x, self.y, 0, 0)
        self.distance2 = distance(self.x, self.y, WIDTH, HEIGHT)


class Command:
    def __init__(self, base: Base, monsters: List[Monster]):
        self.base = base
        self.monsters = monsters
        self.turn = 0

    def next_action(self, enemies: List[Enemy]) -> str:
        pass

    def move(self, target: Point) -> str:
        if self.base.side == 0:
            return f"MOVE {target.x} {target.y}"
        else:
            return f"MOVE {WIDTH - target.x} {HEIGHT - target.y}"

    def push_back(self, hero, target: Monster) -> str:
        self.base.spell()
        for i, monster in enumerate(self.monsters):
            if monster.shield == 0 and distance(hero.x, hero.y, monster.x, monster.y) <= WIND_RADIUS:
                self.monsters[i].x += target.x
                self.monsters[i].y += target.y
        return f"SPELL WIND {hero.x + target.x} {hero.y + target.y}"

    def wind(self) -> str:
        self.base.spell()
        if self.base.side == 0:
            return f"SPELL WIND {WIDTH} {HEIGHT}"
        else:
            return f"SPELL WIND 0 0"

    def shield(self, target: Monster) -> str:
        self.base.spell()
        target.shield = 11
        return f"SPELL SHIELD {target.id}"

    def control(self, target: Union[Monster, Enemy], x: int, y: int) -> str:
        self.base.spell()
        target.is_controlled = True
        target.is_controlling = True
        if self.base.side == 0:
            return f"SPELL CONTROL {target.id} {x} {y}"
        else:
            return f"SPELL CONTROL {target.id} {WIDTH - x} {HEIGHT - y}"


class DefenderCommand(Command):
    def __init__(self, hero, index: int, base: Base, monsters: List[Monster]):
        super().__init__(base, monsters)
        self.index = index
        self.hero = hero
        self.arg = pi / 8 + pi / 4 * self.index
        self.dest = Point(BASE_RADIUS * cos(self.arg), BASE_RADIUS * sin(self.arg))
        self.direction = 1

    def next_action(self, enemies: List[Enemy]) -> str:
        if (self.hero.x, self.hero.y) == (self.dest.x, self.dest.y):
            self.arg += self.direction * pi / 40
            self.dest = Point(BASE_RADIUS * cos(self.arg), BASE_RADIUS * sin(self.arg))
            if self.arg < pi / 40 + pi / 4 * self.index:
                self.direction = 1
            if self.arg > 9 * pi / 40 + pi / 4 * self.index:
                self.direction = -1
        self.turn += 1
        monsters = [monster for monster in self.monsters if monster.next_point.distance < BASE_RADIUS + SEARCH_RADIUS]
        level = [monster.next_point.distance for monster in monsters]
        for i, monster in enumerate(monsters):
            if [enemy for enemy in enemies if distance(monster.x, monster.y, enemy.x, enemy.y) < WIND_RADIUS]:
                level[i] = min(level[i], monster.distance - 2200)
            level[i] **= 2
            level[i] += distance(self.hero.x, self.hero.y, monster.x, monster.y)
            level[i] -= monster.health * 5
            level[i] -= monster.shield * 20
        if not monsters:
            return self.move(self.dest)
        target = min([(lv, monster) for monster, lv in zip(monsters, level)], key=itemgetter(0))[1]
        g, gx, gy = 0, 0, 0
        for monster, lv in zip(monsters, level):
            g += 1 / lv
            gx += monster.next_point.x / lv
            gy += monster.next_point.y / lv
        center = Point(gx / g, gy / g)
        if not self.base.has_mana() or distance(self.hero.x, self.hero.y, target.x, target.y) > WIND_RADIUS:
            if target.id in [monster.id for monster in monsters if distance(center.x, center.y, monster.x, monster.y) < 800]:
                return self.move(center)
            else:
                return self.move(target.next_point)
        if [enemy for enemy in enemies if distance(enemy.x, enemy.y, target.x, target.y) < WIND_RADIUS]:
            if target.shield == 0 and target.distance < SEARCH_RADIUS + WIND_RADIUS:
                return self.push_back(self.hero, target)
        else:
            if target.shield == 0 and target.distance < WIND_RADIUS and target.health > 4:
                return self.push_back(self.hero, target)
        if target.id not in [monster.id for monster in monsters
                             if distance(center.x, center.y, monster.x, monster.y) < 800]:
            return self.move(target.next_point)
        enemies = [enemy for enemy in enemies if distance(self.hero.x, self.hero.y, enemy.x, enemy.y) < SEARCH_RADIUS]
        if enemies and len([
            monster.id for monster in monsters
            if distance(center.x, center.y, monster.x, monster.y) < 800
        ]) <= len([
            monster.id for monster in monsters
            if distance(center.x, center.y, monster.x, monster.y) < 800
        ]):
            return self.control(min(enemies, key=attrgetter("distance")), WIDTH, HEIGHT)
        return self.move(center)


class AttackerCommand(Command):
    def __init__(self, hero, base: Base, monsters: List[Monster]):
        super().__init__(base, monsters)
        self.hero = hero
        self.arg = 0
        self.dest = Point(WIDTH - MONSTER_RADIUS * cos(self.arg), HEIGHT - MONSTER_RADIUS * sin(self.arg))
        self.direction = 1
        self.forcing = False

    def next_action(self, enemies: List[Enemy]) -> str:
        if (self.hero.x, self.hero.y) == (self.dest.x, self.dest.y):
            r = MONSTER_RADIUS - self.turn * 10
            self.arg += self.direction * pi / 20
            self.dest = Point(WIDTH - r * cos(self.arg), HEIGHT - r * sin(self.arg))
            if self.arg < pi / 20:
                self.direction = 1
            if self.arg > 9 * pi / 20:
                self.direction = -1
        self.turn += 1
        if self.forcing and distance(self.hero.x, self.hero.y, WIDTH, HEIGHT) > SEARCH_RADIUS:
            if not self.base.has_mana():
                return self.move(Point(WIDTH, HEIGHT))
            if [
                monster for monster in self.monsters
                if 0 < monster.x < WIDTH and 0 < monster.y < HEIGHT
                and monster.distance2 < SEARCH_RADIUS
                and distance(self.hero.x, self.hero.y, monster.x, monster.y)
            ]:
                self.wind()
            targets = [
                monster for monster in self.monsters
                if monster.health > monster.distance2 // 400 * 2 - self.base.mana // 10
                and monster.distance2 < SEARCH_RADIUS
                and distance(self.hero.x, self.hero.y, monster.x, monster.y) < SEARCH_RADIUS
            ]
            if targets:
                target = min(targets, key=attrgetter("distance2"))
                if target.shield == 0:
                    self.forcing = False
                    return self.shield(target)
            if [
                monster for monster in self.monsters
                if 0 < monster.x < WIDTH and 0 < monster.y < HEIGHT
                and distance(self.hero.x, self.hero.y, monster.x, monster.y) < WIND_RADIUS
                and monster.shield == 0
            ]:
                return self.wind()
            else:
                return self.move(Point(WIDTH, HEIGHT))
        self.forcing = False
        if self.base.has_more_mana(self.monsters) and [
            monster for monster in self.monsters
            if monster.health > monster.distance2 // 400 * 2 - self.base.mana // 10
            and 0 < monster.x < WIDTH and 0 < monster.y < HEIGHT
            and distance(self.hero.x, self.hero.y, monster.x, monster.y) < WIND_RADIUS
            and not [enemy for enemy in enemies if distance(monster.x, monster.y, enemy.x, enemy.y) < 800]
        ]:
            self.forcing = distance(self.hero.x, self.hero.y, WIDTH, HEIGHT) > SEARCH_RADIUS + WIND_RADIUS
            return self.wind()
        if distance(self.hero.x, self.hero.y, WIDTH, HEIGHT) > BASE_RADIUS + SEARCH_RADIUS:
            return self.move(self.dest)
        targets = [
            monster for monster in self.monsters
            if distance(self.hero.x, self.hero.y, monster.x, monster.y) < SEARCH_RADIUS
            and not [enemy for enemy in enemies if distance(self.hero.x, self.hero.y, enemy.x, enemy.y) < SEARCH_RADIUS]
        ]
        if targets:
            target = min(targets, key=attrgetter("distance2"))
            if self.base.has_more_mana(self.monsters) and 0 < target.x < WIDTH and 0 < target.y < HEIGHT and distance(self.hero.x, self.hero.y, target.x, target.y) < WIND_RADIUS:
                return self.wind()
            else:
                return self.move(target.behind_point())
        return self.move(self.dest)


class Hero:
    _count: int = 0

    def __init__(self, x: int, y: int, base: Base, monsters: List[Monster]):
        self.id = Hero._count
        self.x = x if base.side == 0 else WIDTH - x
        self.y = y if base.side == 0 else HEIGHT - y
        self.base = base
        self.command = AttackerCommand(self, base, monsters) if self.id == 0 else DefenderCommand(self, self.id - 1,
                                                                                                  base, monsters)
        Hero._count += 1

    def update(self, x: int, y: int, monsters: List[Monster]):
        self.x = x if self.base.side == 0 else WIDTH - x
        self.y = y if self.base.side == 0 else HEIGHT - y
        self.command.monsters = monsters


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
            entity_id, entity_type, x, y, shield_life, is_controlled, health, vx, vy, near_base, _ = map(int,
                                                                                                         input().split())
            if entity_type == 0:
                monsters.append(Monster(entity_id, x, y, shield_life, is_controlled, health, vx, vy, near_base, base))
            elif entity_type == 1:
                if entity_id not in heroes:
                    heroes[entity_id] = Hero(x, y, base, monsters)
                else:
                    heroes[entity_id].update(x, y, monsters)
            elif entity_type == 2:
                enemies.append(Enemy(entity_id, x, y, shield_life, is_controlled, base))
        for hero in sorted(heroes.values(), key=attrgetter('id')):
            print(hero.command.next_action(enemies))


if __name__ == '__main__':
    main()
