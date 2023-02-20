from matplotlib import colors
import pyglet
import uuid

from .. import config
from .vehicles import Tank, Ship, Jet
from .tools import wrap_position


class Mine:

    def __init__(self, x, y, team, number, owner, uid):
        self.x = x
        self.y = y
        self.team = team
        self.number = number
        self.owner = owner
        self.health = config.health['mine']
        self.attack = config.attack['mine']
        self.kind = 'mine'
        self.uid = uid

    def make_label(self):
        return


class Base:

    def __init__(self, x, y, team, number, batch, owner, uid, high_contrast=False):
        self.x = x
        self.y = y
        self.kind = 'base'
        self.health = config.health['base']
        self.attack = config.attack['base']
        self.team = team
        self.number = number
        self.owner = owner
        self.batch = batch
        self.uid = uid
        self.competing = False
        muid = uuid.uuid4().hex
        self.mines = {
            muid:
            Mine(x=self.x,
                 y=self.y,
                 team=self.team,
                 number=self.number,
                 owner=self,
                 uid=muid)
        }
        self.crystal = 10000
        self.owner.update_player_map(x=self.x, y=self.y)
        self.avatar = pyglet.sprite.Sprite(img=config.images[f'base_{self.number}'],
                                           x=self.x,
                                           y=self.y,
                                           batch=batch)
        if high_contrast:
            rgb = colors.to_rgb(f'C{self.number}')
            self.shape = pyglet.shapes.Rectangle(
                x=self.x - config.competing_mine_radius,
                y=self.y - config.competing_mine_radius,
                width=config.competing_mine_radius * 2,
                height=config.competing_mine_radius * 2,
                color=tuple(int(round(c * 255)) for c in rgb) + (50, ),
                batch=batch)
        else:
            self.shape = None
        self.label = None
        self.clabel = None
        self.make_label()

        ix = int(x)
        iy = int(y)
        dx = config.vehicle_offset
        offset = None
        while (offset is None):
            xx, yy = wrap_position(ix + dx, iy + dx)
            if self.owner.game_map[yy, xx] == 1:
                offset = (dx, dx)
                break
            xx, yy = wrap_position(ix + dx, iy - dx)
            if self.owner.game_map[yy, xx] == 1:
                offset = (dx, -dx)
                break
            xx, yy = wrap_position(ix - dx, iy + dx)
            if self.owner.game_map[yy, xx] == 1:
                offset = (-dx, dx)
                break
            xx, yy = wrap_position(ix - dx, iy - dx)
            if self.owner.game_map[yy, xx] == 1:
                offset = (-dx, -dx)
                break
            dx += 1
        self.tank_offset = offset

        dx = config.vehicle_offset
        offset = None
        while (offset is None):
            xx, yy = wrap_position(ix + dx, iy + dx)
            if self.owner.game_map[yy, xx] == 0:
                offset = (dx, dx)
                break
            xx, yy = wrap_position(ix + dx, iy - dx)
            if self.owner.game_map[yy, xx] == 0:
                offset = (dx, -dx)
                break
            xx, yy = wrap_position(ix - dx, iy + dx)
            if self.owner.game_map[yy, xx] == 0:
                offset = (-dx, dx)
                break
            xx, yy = wrap_position(ix - dx, iy - dx)
            if self.owner.game_map[yy, xx] == 0:
                offset = (-dx, -dx)
                break
            dx += 1
        self.ship_offset = offset

    def make_label(self):
        if self.label is not None:
            self.label.delete()
        if self.clabel is not None:
            self.clabel.delete()
        color = (0, 0, 0, 255)
        self.label = pyglet.text.Label(f'{self.health} [{len(self.mines)}]',
                                       color=color,
                                       font_size=10,
                                       x=self.x,
                                       y=self.y + 18,
                                       anchor_x='center',
                                       anchor_y='center',
                                       batch=self.batch)
        if self.competing:
            self.clabel = pyglet.text.Label('C',
                                            color=color,
                                            font_size=10,
                                            x=self.x,
                                            y=self.y,
                                            anchor_x='center',
                                            anchor_y='center',
                                            batch=self.batch)
        else:
            self.clabel = None

    def delete(self):
        self.avatar.delete()
        self.label.delete()
        if self.clabel is not None:
            self.clabel.delete()
        if self.shape is not None:
            self.shape.delete()

    def as_info(self):
        return {
            'x': self.x,
            'y': self.y,
            'team': self.team,
            'number': self.number,
            'mines': len(self.mines),
            'crystal': self.crystal,
            'uid': self.uid
        }

    def mine_cost(self):
        return config.cost['mine'] * (2**(len(self.mines) - 1))

    def not_enough_crystal(self, kind):
        if kind == 'mine':
            cost = self.mine_cost()
        else:
            cost = config.cost[kind]

        not_ok = self.crystal < cost
        if not_ok:
            print(f'Not enough crystal to build {kind}')
        return not_ok

    def build_mine(self):
        if self.not_enough_crystal('mine'):
            return
        self.crystal -= self.mine_cost()
        uid = uuid.uuid4().hex
        self.mines[uid] = Mine(x=self.x,
                               y=self.y,
                               team=self.team,
                               number=self.number,
                               owner=self,
                               uid=uid)
        self.make_label()
        print('Building mine', self.mines)

    def build_tank(self, heading):
        if self.not_enough_crystal('tank'):
            return
        print('Building tank')
        uid = uuid.uuid4().hex
        self.owner.tanks[uid] = Tank(x=self.x + self.tank_offset[0],
                                     y=self.y + self.tank_offset[1],
                                     team=self.team,
                                     number=self.number,
                                     heading=heading,
                                     batch=self.batch,
                                     owner=self,
                                     uid=uid)
        self.crystal -= config.cost['tank']

    def build_ship(self, heading):
        if self.not_enough_crystal('ship'):
            return
        print('Building ship')
        uid = uuid.uuid4().hex
        self.owner.ships[uid] = Ship(x=self.x + self.ship_offset[0],
                                     y=self.y + self.ship_offset[1],
                                     team=self.team,
                                     number=self.number,
                                     heading=heading,
                                     batch=self.batch,
                                     owner=self,
                                     uid=uid)
        self.crystal -= config.cost['ship']

    def build_jet(self, heading):
        if self.not_enough_crystal('jet'):
            return
        print('Building jet')
        uid = uuid.uuid4().hex
        self.owner.jets[uid] = Jet(x=self.x,
                                   y=self.y,
                                   team=self.team,
                                   number=self.number,
                                   heading=heading,
                                   batch=self.batch,
                                   owner=self,
                                   uid=uid)
        self.crystal -= config.cost['jet']


class BaseProxy:

    def __init__(self, base):
        for key, item in base.as_info().items():
            setattr(self, key, item)
        self.build_mine = base.build_mine
        self.build_tank = base.build_tank
        self.build_ship = base.build_ship
        self.build_jet = base.build_jet
        self.mine_cost = base.mine_cost

    # def __getitem__(self, key):
    #     return self._data[key]

    # def keys(self):
    #     return self._data.keys()

    # def values(self):
    #     return self._data.values()

    # def items(self):
    #     return self._data.items()

    def cost(self, kind):
        if kind == 'mine':
            return self.mine_cost()
        else:
            return config.cost[kind]
