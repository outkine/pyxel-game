import pyxel

pyxel.init(64, 64)
pyxel.load('assets/my_resource.pyxres')


def add_coords(c1, c2):
    return (c1[0] + c2[0], c1[1] + c2[1])


class Tilemap:
    def __init__(self, x):
        self.x = x

    def get(self, coords, tm=0):
        return pyxel.tilemap(tm).get(self.x * 8 + coords[0], coords[1])

    def find_tile_all(self, tile, tm=0):
        return [(x, y) for x in range(8) for y in range(8)
                if self.get((x, y), tm) == tile]

    def find_tile(self, tile, tm=0):
        res = self.find_tile_all(tile, tm)
        return res and res[0]

    def draw(self):
        pyxel.bltm(0, 0, 0, self.x * 8, 0, 8, 8, 0)


class Thing:
    def __init__(self, coords, sprite, sprite_row):
        self.coords = coords
        self.sprite = sprite
        self.sprite_row = sprite_row

    def draw(self):
        pyxel.blt(self.coords[0] * 8, self.coords[1] * 8, 0, self.sprite * 8,
                  self.sprite_row * 8, 8, 8, 0)


class TrailEnemy(Thing):
    def __init__(self, trail, sprite, sprite_row):
        super().__init__(trail[0], sprite, sprite_row)
        self.previous_coords = None

    def touching_trail(self):
        return [
            add_coords(self.coords, change)
            for change in [(0, -1), (0, 1), (-1, 0), (1, 0)]
            if add_coords(self.coords, change) in trail
        ]

    def update(self):
        old_coords = self.coords

        tiles = self.touching_trail()
        if len(tiles) == 2:
            if not self.previous_coords:
                self.coords = tiles[0]
            else:
                self.coords = next(
                    filter(lambda tile: tile != self.previous_coords, tiles))
        elif len(tiles) == 1:
            self.coords = tiles[0]
        else:
            raise Exception('incorrect trail')

        self.previous_coords = old_coords


PLAYER_S = 1
ENEMY_S = 2

WALL = 32
DEATH = 33
ENTRANCE = 35
EXIT = 36
TRAIL = 64

t = 0
tm = Tilemap(-1)
p = Thing((0, 0), PLAYER_S, 0)

entrance = None
exit = None
trail = None
enemy = None


def next_level():
    global entrance, exit, trail, enemy

    tm.x += 1

    entrance = tm.find_tile(ENTRANCE)
    exit = tm.find_tile(EXIT)
    if not entrance or not exit:
        raise Exception('the end!')
    p.coords = entrance

    trail = tm.find_tile_all(TRAIL, 1)
    if trail:
        enemy = TrailEnemy(trail, ENEMY_S, 0)


next_level()

while True:
    if p.coords == exit:
        next_level()

    old_coords = p.coords

    (x, y) = p.coords
    if pyxel.btnp(pyxel.KEY_W):
        y -= 1
    elif pyxel.btnp(pyxel.KEY_S):
        y += 1
    elif pyxel.btnp(pyxel.KEY_A):
        x -= 1
    elif pyxel.btnp(pyxel.KEY_D):
        x += 1
    p.coords = (x, y)

    current_tile = tm.get(p.coords)
    if current_tile == WALL:
        p.coords = old_coords
    elif current_tile == DEATH or (enemy and enemy.coords == p.coords):
        p.coords = entrance

    if enemy and not t % 5:
        enemy.update()

    pyxel.cls(0)
    tm.draw()
    p.draw()
    if enemy:
        enemy.draw()
    pyxel.flip()

    t += 1
