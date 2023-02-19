from .. import config


def wrap_position(x, y):
    x = x % config.nx
    y = y % config.ny
    if x < 0:
        x = config.nx + x
    if y < 0:
        y = config.ny + y
    return x, y


class ReadOnly:

    def __init__(self, props):
        for key, item in props.items():
            setattr(self, key, item)
