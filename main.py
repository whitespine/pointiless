# from tkinter import *
from PIL import Image

ERROR_FACTOR = 1.0


def int_vec_n(n):
    assert n >= 1

    class _Vec(object):
        def __init__(self, *args):
            # assert len(args) == n
            # assert all(isinstance(x, T) for x in args)
            self.items = args

        def __add__(self, other):
            # assert isinstance(other, _Vec)
            # assert len(other.items) == n
            return type(self)(*(a + b for a, b in zip(self.items, other.items)))

        def __sub__(self, other):
            # assert isinstance(other, _Vec)
            # assert len(other.items) == n
            return type(self)(*(a - b for a, b in zip(self.items, other.items)))

        def __getitem__(self, item):
            return self.items[item]

        def __mul__(self, other):
            try:
                return type(self)(*((x * other) for x in self.items))
            except (TypeError, ValueError):
                raise ValueError("{} not a valid scalar multiple".format(other))

        @property
        def mag(self):
            return sum(x ** 2 for x in self.items) ** 0.5

        """
        def __getattribute__(self, item):
            s = _sigil_index(item)
            if s is None:
                return super(_Vec, self).__getattribute__(item)
            else:
                return self[s]

        def __setattr__(self, key, value):
            s = _sigil_index(key)
            if s is None:
                super(_Vec, self).__setattr__(key, value)
            else:
                self[s] = value
        """

        def __str__(self):
            return str(self.items)

        def __repr__(self):
            return str(self)

        def __iter__(self):
            return iter(self.items)

        @property
        def tup(self):
            return tuple(self.items)

    return _Vec


class Vec2(int_vec_n(2)):
    def valid(self, img) -> bool:
        w, h = img.size
        return 0 <= self.items[0] < w and 0 <= self.items[1] < h


class Color(int_vec_n(3)):
    def rgb_bounded(self):
        vals = []
        for e in self.items:
            if e < 0.0:
                e = 0.0
            elif e > 255.0:
                e = 255.0
            vals.append(e)
        return Color(*vals)


class FastImage:
    @property
    def size(self):
        return self.w, self.h

    def __init__(self, from_img):
        self.w, self.h = from_img.size

        def pconv(x, y):
            return Color(*(float(v) for v in from_img.getpixel((x, y))))

        self.data = [[pconv(c, r) for r in range(self.h)] for c in range(self.w)]

    def __getitem__(self, item):
        return self.data[item[0]][item[1]]

    def __setitem__(self, key, value):
        self.data[key[0]][key[1]] = value

    def un_dump(self, to_img):
        for x in range(self.w):
            for y in range(self.h):
                p = Vec2(x, y)
                c = tuple(int(v) for v in self[p].rgb_bounded())
                to_img.putpixel((x, y), c)


class Kernel:
    class DistributionPoint:
        def __init__(self, o, f):
            self.offset = o
            self.factor = f

    def __init__(self, distribution):
        self.distribution = distribution

    def apply(self, img, at, avail_colors):
        # Get the base color value
        root_color = img[at]
        # print("Root is {}".format(root_color))

        # Find the closest color
        closest_color = find_closest_color(root_color, avail_colors)

        # Put that color at the target
        img[at] = closest_color

        # Find the error
        error = closest_color - root_color
        # print("Error is {}".format(error))

        # Distribute the error, by the distribution items
        for item in self.distribution:
            # Compute how much we will be altering by
            compensation = error * -item.factor * ERROR_FACTOR
            # print("Compensation is {}".format(compensation))

            # Compute where we are affecting
            target = item.offset + at

            # Find if the point is valid, and if so write to it
            if target.valid(img):
                old_color = img[target]
                new_color = (old_color + compensation).rgb_bounded()
                img[target] = new_color


def find_closest_color(c, options):
    best_color = None
    best_dist = None

    for option in options:
        dist = (option - c).mag
        if best_dist is None or best_dist > dist:
            best_dist = dist
            best_color = option

    return best_color


"""
Stucki
             X   8   4 
     2   4   8   4   2
     1   2   4   2   1

           (1/42)
"""
STUCKI = Kernel([Kernel.DistributionPoint(p, x) for p, x in [
    (Vec2(1, 0), 8 / 42.0),
    (Vec2(2, 0), 4 / 42.0),

    (Vec2(-2, 1), 2 / 42.0),
    (Vec2(-1, 1), 4 / 42.0),
    (Vec2(0, 1), 8 / 42.0),
    (Vec2(1, 1), 4 / 42.0),
    (Vec2(2, 1), 2 / 42.0),

    (Vec2(-2, 2), 1 / 42.0),
    (Vec2(-1, 2), 2 / 42.0),
    (Vec2(0, 2), 4 / 42.0),
    (Vec2(1, 2), 2 / 42.0),
    (Vec2(2, 2), 1 / 42.0)
]])


def main():
    # Load the image
    # img = Image.open("auntie.jpg")
    # img = Image.open("oscar.png")
    # img = Image.open("snail.png")
    # img = Image.open("seurat.jpg")
    # img = Image.open("eye.jpg")
    # img = Image.open("indiana.jpg")
    img = Image.open("indiana3.jpg")
    img = img.convert('RGB')
    fast_img = FastImage(img)

    comp = 0.0

    WHITE = Color(255.0, 255.0, 255.0)
    BLACK = Color(0.0, 0.0, 0.0)
    RED = Color(255.0, comp, comp)
    BLUE = Color(comp, comp, 255.0)
    GREEN = Color(comp, 255.0, comp)
    CYAN = Color(comp, 255.0, 255.0)
    MAGENTA = Color(255.0, comp, 255.0)
    YELLOW = Color(255.0, 255.0, comp)
    BROWN = Color(165.0, 42.0, 42.0)

    colors = [
        WHITE,
        BLACK,
        RED,
        BLUE,
        GREEN,
        # CYAN,
        # MAGENTA,
        YELLOW,
        BROWN
    ]

    """
    color_keys = [
        ("r", RED),
        ("g", GREEN),
        ("b", BLUE),
        ("w", WHITE),
        ("c", BLACK),
    ]
    """
    color_combos = None

    # Iterate over pixels
    w, h = fast_img.size
    # for x in range(w):
    for y in range(h):
        # print("{}%".format(int(100.0 * x / w)))
        print("{}%".format(int(100.0 * y / h)))
        # for y in range(h):
        for x in range(w):
            # pass
            STUCKI.apply(fast_img, Vec2(x, y), colors)

    # Save
    img2 = Image.new('RGB', img.size)
    fast_img.un_dump(img2)
    img2.save("output.png")


main()
