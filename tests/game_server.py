from __future__ import annotations

import json
import logging
import math
import random

from typing import List, Optional
from dataclasses import dataclass
from pathlib import Path
from enum import Enum


class Direction(Enum):
    U = 1
    R = 2
    D = 3
    L = 4

    def __str__(self):
        return self.name

    @staticmethod
    def random():
        return Direction[Direction.random_str()]

    @staticmethod
    def random_str():
        return random.choice(Direction.__dict__['_member_names_'])


@dataclass
class Point:
    x: float
    y: float

    def __le__(self, other: Point) -> bool:
        return self.x <= other.x and self.y <= other.y

    def __ge__(self, other: Point) -> bool:
        return self.x >= other.x and self.y >= other.y

    def __lt__(self, other: Point) -> bool:
        return self.x < other.x and self.y < other.y

    def __add__(self, other: Point) -> Point:
        x = self.x + other.x
        y = self.y + other.y
        return Point(x, y)

    def __str__(self) -> str:
        return f'[{self.x:.1f}, {self.y:.1f}]'

    def __eq__(self, other: Point):
        return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)

    def to_list(self):
        return [self.x, self.y]

    @staticmethod
    def measure_distance(a: Point, b: Point) -> float:

        squared_distance = (b.x - a.x) ** 2 + (b.y - a.y) ** 2
        return math.sqrt(squared_distance)


class Vector2D(Point):

    def __mul__(self, other: float) -> Vector2D:
        x = self.x * other
        y = self.y * other
        return Vector2D(x, y)


class Road:

    def __init__(self, json_src: dict, width=0.4):

        x0, y0 = json_src['x0'], json_src['y0']
        x1 = json_src.get('x1', x0)
        y1 = json_src.get('y1', y0)

        left_bottom_x = min(x0, x1) - width
        left_bottom_y = min(y0, y1) - width
        right_top_x = max(x0, x1) + width
        right_top_y = max(y0, y1) + width

        self.left_bottom_corner = Point(left_bottom_x, left_bottom_y)
        self.right_top_corner = Point(right_top_x, right_top_y)

    def is_on_the_road(self, point: Point) -> bool:
        return self.left_bottom_corner <= point <= self.right_top_corner

    def bound_to_the_road(self, point: Point) -> Point:
        new_x = bound(self.left_bottom_corner.x, self.right_top_corner.x, point.x)
        new_y = bound(self.left_bottom_corner.y, self.right_top_corner.y, point.y)
        return Point(new_x, new_y)


@dataclass
class Player:

    name: str
    token: str
    id: int
    position: Point
    speed: Vector2D = Vector2D(0.0, 0.0)
    direction: Direction = Direction.U

    def set_speed(self, direction: str, speed: float):
        self.speed = get_speed(direction, speed)

        try:
            self.direction = Direction[direction]
        except KeyError:
            pass    # leave the direction unchanged

    def set_position(self, position: Point):
        self.position = position

    def get_state(self) -> Optional[dict]:
        state = {
            'pos': self.position.to_list(),
            'speed': self.speed.to_list(),
            'dir': str(self.direction)
        }
        return state

    def estimate_new_position(self, ticks: int) -> Point:
        new_position: Point = self.position + self.speed * (ticks / 1000)
        return new_position


class RoadLoader:
    class RawRoad:
        def __init__(self, dict_src: Optional[dict] = None):
            if dict_src is None:
                return
            x0 = dict_src['x0']
            y0 = dict_src['y0']
            x1 = dict_src.get('x1', x0)
            y1 = dict_src.get('y1', y0)
            self.x0 = min(x0, x1)
            self.x1 = max(x0, x1)
            self.y0 = min(y0, y1)
            self.y1 = max(y0, y1)
            self.is_vertical = x0 == x1

        def make_dict(self):
            return {
                'x0': self.x0,
                'x1': self.x1,
                'y0': self.y0,
                'y1': self.y1
            }

        x0: int
        y0: int
        x1: int
        y1: int
        is_vertical: bool

    def __init__(self, raw_roads: dict):
        RawRoad = RoadLoader.RawRoad

        self.vertical_roads: List[RawRoad] = []
        self.horizontal_roads: List[RawRoad] = []
        self.new_roads: List[RawRoad] = []

        for raw_road in raw_roads:
            road = RawRoad(raw_road)
            if road.is_vertical:
                self.vertical_roads.append(road)
            else:
                self.horizontal_roads.append(road)
        self.handle_the_roads()

    def handle_the_roads(self):
        RawRoad = RoadLoader.RawRoad
        RoadPairs = Optional[List[List[RawRoad]]]

        def check_roads(roads: List[RawRoad]) -> RoadPairs:
            for_merging = list()
            for i in range(len(roads)):
                road_1 = roads[i]
                for road_2 in roads[i+1:]:
                    # Проверяем совпадение концов коллинеарных дорог
                    if road_1.is_vertical:
                        if road_1.x0 == road_2.x0:
                            if road_1.y0 == road_2.y1 or road_1.y1 == road_2.y0:
                                for_merging.append([road_1, road_2])
                    else:
                        if road_1.y0 == road_2.y0:
                            if road_1.x0 == road_2.x1 or road_1.x1 == road_2.x0:
                                for_merging.append([road_1, road_2])

            return for_merging

        def merge_roads(road_1: RawRoad, road_2: RawRoad) -> RawRoad:
            result = RawRoad()
            result.x0 = min(road_1.x0, road_2.x0)
            result.x1 = max(road_1.x1, road_2.x1)
            result.y0 = min(road_1.y0, road_2.y0)
            result.y1 = max(road_1.y1, road_2.y1)
            result.is_vertical = road_1.is_vertical

            return result

        vertical_pairs = check_roads(self.vertical_roads)
        horizontal_pairs = check_roads(self.horizontal_roads)

        for pair in vertical_pairs:
            self.new_roads.append(merge_roads(*pair))
            self.vertical_roads.remove(pair[0])
            self.vertical_roads.remove(pair[1])
        for pair in horizontal_pairs:
            self.new_roads.append(merge_roads(*pair))
            self.horizontal_roads.remove(pair[0])
            self.horizontal_roads.remove(pair[1])

    def get_dicts(self):

        result = list()
        src = self.vertical_roads + self.horizontal_roads + self.new_roads
        for road in src:
            result.append(road.make_dict())
        return result

    vertical_roads: List[RawRoad] = list()
    horizontal_roads: List[RawRoad] = list()
    new_roads: List[RawRoad] = list()


class GameSession:

    def __init__(self, game_map: dict, default_speed):
        self.map = game_map
        self.roads: List[Road] = list()
        prepared_roads: List[dict] = RoadLoader(game_map['roads']).get_dicts()
        for r in prepared_roads:
            road = Road(r)
            self.roads.append(road)

        self.players: List[Player] = list()

        self.default_speed = game_map.get('dogSpeed', default_speed)

    def add_player(self, name: str, token: str, _id: int, position: Point):
        player = Player(name, token, _id, position)
        self.players.append(player)

    def get_state(self) -> Optional[dict]:
        state = dict()
        for player in self.players:
            player_state = {
                str(player.id): player.get_state()
            }
            state.update(player_state)

        return {'players': state}

    def tick(self, ticks: int):
        for player in self.players:
            estimated_new_position = player.estimate_new_position(ticks)
            new_position: Point = self.bounded_move(player.position, estimated_new_position)
            if new_position is not None:
                player.set_position(new_position)
            if new_position != estimated_new_position:
                player.set_speed('', 0.0)

    def bounded_move(self, start_point: Point, stop_point: Point) -> Optional[Point]:
        start_roads: List[Road] = list()

        for road in self.roads:
            if road.is_on_the_road(start_point):
                start_roads.append(road)

        if len(start_roads) == 0:
            logging.warning("Player is not on the road. Position: %s, Map: %s", str(start_point), self.map['id'])
            return None

        most_far: Point = start_roads[0].bound_to_the_road(stop_point)

        if len(start_roads) == 1:
            return most_far

        max_distance = Point.measure_distance(start_point, most_far)

        for i in range(1, len(start_roads)):
            pretender: Point = start_roads[i].bound_to_the_road(stop_point)
            distance = Point.measure_distance(start_point, pretender)
            if distance > max_distance:
                most_far = pretender
                max_distance = distance

        return most_far


class GameServer:

    def __init__(self, config_file_name: Path):  # pathlib
        try:
            with open(config_file_name) as f:
                self.config: dict = json.load(f)
        except FileNotFoundError:
            logging.error("Config file is not found. Check the file location: %s", config_file_name)
            raise

        except json.decoder.JSONDecodeError as ex:
            logging.error("Unable to load json config. Error: %s", ex.args[0])
            raise

        self.default_speed = self.config.get('defaultDogSpeed')

        self.sessions: List[GameSession] = list()

    def get_maps(self) -> Optional[List[dict]]:
        try:
            map_list = list()
            for m in self.config['maps']:
                map_list.append({'id': m['id'], 'name': m['name']})
            return map_list
        except KeyError:
            logging.warning("Unable to get maps from the server")
            return list()

    def get_map(self, map_id: str) -> Optional[dict]:
        try:
            for m in self.config['maps']:
                if m['id'] == map_id:
                    return m
        except KeyError:
            logging.warning("There is a problem with maps in config. Config: %s", json.dumps(self.config))
            return None

        logging.warning("There is no such map. Requested map id: %s, available maps: %s",
                        map_id, json.dumps(self.get_maps()))
        return None

    def join(self, username: str, map_id: str, token: str, player_id: int, position: Point) -> bool:

        for session in self.sessions:
            session: GameSession
            if session.map['id'] == map_id:
                session.add_player(username, token, player_id, position)
                return True

        _map = self.get_map(map_id)
        if _map is None:
            return False

        session = GameSession(_map, self.default_speed)
        session.add_player(username, token, player_id, position)
        self.sessions.append(session)
        return True

    def get_state(self, token: str) -> Optional[dict]:
        for session in self.sessions:
            session: GameSession
            for player in session.players:
                player: Player
                if player.token == token:
                    return session.get_state()
        return None

    def move(self, token: str, direction: str) -> bool:

        for session in self.sessions:
            session: GameSession
            for player in session.players:
                if player.token == token:
                    player.set_speed(direction, session.default_speed)
                    return True
        return False    # There is no such player

    def tick(self, ticks: int):
        for session in self.sessions:
            session.tick(ticks)


def bound(bound_1: float, bound_2: float, value: float) -> float:

    lower = min(bound_1, bound_2)
    upper = max(bound_1, bound_2)

    result = min(upper, value)
    result = max(lower, result)

    return result


def get_speed(direction: str, speed: float) -> Vector2D:
    try:
        direction = Direction[direction]

        if direction == Direction.U:
            speed = Vector2D(0.0, -speed)
        elif direction == Direction.R:
            speed = Vector2D(speed, 0.0)
        elif direction == Direction.D:
            speed = Vector2D(0.0, speed)
        elif direction == Direction.L:
            speed = Vector2D(-speed, 0.0)

    except KeyError:
        if direction == '':
            speed = Vector2D(0.0, 0.0)
        else:
            raise

    return speed
