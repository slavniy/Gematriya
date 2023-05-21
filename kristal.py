from PIL import Image, ImageDraw, ImageFont
from math import cos, sin, pi
from itertools import permutations


class NameKristal:
    def __init__(self):
        self.font = ImageFont.truetype("static/NotoSerif-Regular.ttf", 18, encoding='UTF-8')
        self.alf = list('АБВГДеЕЖSZИiЇћКЛМНОПРСТУƔФXѾЦЧШЩЪЫьҌЮЯЭѠѦѪѨѬѮѰӨѴӔ')
        self.width = self.height = 800
        self.fon_color = (255, 255, 255)
        self.padding = 50
        self.text_padding = 20
        self.xc, self.yc = self.width // 2, self.height // 2
        self.r_point = (self.width // 2) - self.padding
        self.r_text = self.r_point + self.text_padding
        self.fi = -pi / 2

    def get_point_coords(self, point_number, points_count, radius):
        return (self.xc + radius * cos(self.fi + (2 * pi * point_number) / (points_count)),
                self.yc + radius * sin(self.fi + (2 * pi * point_number) / (points_count)))

    def draw_lines_to_points(self, points, line_color, drawer):
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                drawer.line((points[i], points[j]), fill=line_color, width=1)
            x, y = points[i]
            drawer.ellipse((x - 2, y - 2, x + 2, y + 2), "#000")

    def draw_name_in_letter_context(self, name):
        name = name.replace('Ё', 'E').replace('ё', 'е').replace('Й', 'Ї')
        im = Image.new('RGB', (self.width, self.height), self.fon_color)
        draw = ImageDraw.Draw(im)
        n = len(self.alf)
        points = []
        name_points = []
        # запоминаем точки многоугольника на окружности
        for i in range(n):
            x_p, y_p = self.get_point_coords(i, n, self.r_point)
            x_t, y_t = self.get_point_coords(i, n, self.r_text)
            points.append((x_p, y_p))
            if self.alf[i] in name:
                name_points.append((x_p, y_p))
            text_color = '#f00' if self.alf[i] in name else "#000"
            draw.text(
                (x_t - 5, y_t - 8),
                self.alf[i],
                fill=(text_color),
                font=self.font
            )
        self.draw_lines_to_points(points, '#eee8aa', draw)
        self.draw_lines_to_points(name_points, '#f00', draw)
        im.save('temp/name1.jpg')

    def draw_name_kristal(self, name):
        im = Image.new('RGB', (self.width, self.height), self.fon_color)
        draw = ImageDraw.Draw(im)
        n = len(name)
        points = []
        for i in range(n):
            p_x, p_y = self.get_point_coords(i, n, self.r_point)
            t_x, t_y = self.get_point_coords(i, n, self.r_text)
            points.append((p_x, p_y))
            draw.text(
                (t_x - 5, t_y - 8),
                name[i],
                fill=('#000'),
                font=self.font
            )
        self.draw_lines_to_points(points, '#000', draw)
        draw.ellipse((0 + self.padding, 0 + self.padding, self.width - self.padding, self.height - self.padding),
                     outline=1)
        im.save('temp/name2.jpg')

    def get_name_gates(self, name):
        name_gates = []
        for i in range(len(name) - 1):
            gates = []
            for j in range(i + 1, len(name)):
                gate = name[i] + name[j]
                gates.append(gate)
            name_gates.append('\t'.join(gates))
        return name_gates

    def get_name_portals(self, name):
        portals = {}
        name = set(name)
        for n in range(3, len(name) + 1):
            words = []
            for comb in set(permutations(name, n)):
                words.append(''.join(comb))
            portals[n] = words
        return portals
