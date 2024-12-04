def rect(surface, color, rectangle, width=0):
    pos1, pos2, w, h = rectangle
    for x in range(w):
        for y in range(h):
            if width == 0:
                surface.put_pixel((pos1 + x, pos2 + y), color)
            elif x < width or x >= w - width:
                surface.put_pixel((pos1 + x, pos2 + y), color)
            elif y < width or y >= h - width:
                surface.put_pixel((pos1 + x, pos2 + y), color)


def circle(surface, color, position, radius, width=0):
    x, y = position
    for dx in range(-radius, radius+1):
        for dy in range(-radius, radius+1):
            if dx**2 + dy**2 <= radius**2 and width == 0:
                surface.put_pixel((x + dx, y + dy), color)
            elif radius**2 >= dx**2 + dy**2 >= (radius - width)**2:
                surface.put_pixel((x + dx, y + dy), color)


def line(surface, color, position1, position2, width=1):
    x1, y1 = position1
    x2, y2 = position2
    dx, dy = x2 - x1, y2 - y1
    length = (dx**2 + dy**2) ** 0.5
    increment = (width + 1) / length
    for i in range(int(length) + 1):
        x = int(x1 + dx * i / length)
        y = int(y1 + dy * i / length)
        for w1 in range(width):
            for w2 in range(width):
                surface.put_pixel((x + w1 - width//2, y + w2 - width//2), color)


def polygon(surface, color, positions, filling: bool = True):
    if not filling:
        for i in range(len(positions) - 1):
            line(surface, color, positions[i], positions[i + 1])
        line(surface, color, positions[-1], positions[0])
        return
    # Draw the outline
    polygon(surface, color, positions, filling=False)

    # Find the bounding box of the polygon
    min_x = min(x for x, _ in positions)
    max_x = max(x for x, _ in positions)
    min_y = min(y for _, y in positions)
    max_y = max(y for _, y in positions)

    # Fill the polygon using a scanline algorithm
    for y in range(min_y, max_y + 1):
        intersections = []
        for i in range(len(positions)):
            x1, y1 = positions[i]
            x2, y2 = positions[(i + 1) % len(positions)]
            if y1 > y2:
                x1, y1, x2, y2 = x2, y2, x1, y1
            if y1 <= y < y2 and y2 > y1:
                x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                intersections.append(x)

        intersections.sort()
        for i in range(0, len(intersections), 2):
            if i + 1 < len(intersections):
                start = int(intersections[i])
                end = int(intersections[i + 1])
                for x in range(start, end + 1):
                    surface.put_pixel((x, y), color)
