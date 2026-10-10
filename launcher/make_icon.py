import struct
import sys
import zlib
from pathlib import Path

SIZE = 256
SAMPLES = 4


def rounded_square(x, y, size, radius):
    inner = size - 2 * radius
    dx = max(abs(x - size / 2) - inner / 2, 0)
    dy = max(abs(y - size / 2) - inner / 2, 0)
    return dx * dx + dy * dy <= radius * radius


def triangle(x, y, size):
    left, top, bottom = size * 0.40, size * 0.30, size * 0.70
    right = size * 0.70
    if x < left or x > right or y < top or y > bottom:
        return False
    span = (x - left) / (right - left)
    center = size / 2
    half = (bottom - top) / 2 * (1 - span)
    return abs(y - center) <= half


def pixel(x, y):
    square = play = 0
    for sy in range(SAMPLES):
        for sx in range(SAMPLES):
            px = x + (sx + 0.5) / SAMPLES
            py = y + (sy + 0.5) / SAMPLES
            if rounded_square(px, py, SIZE, SIZE * 0.22):
                square += 1
                if triangle(px, py, SIZE):
                    play += 1
    total = SAMPLES * SAMPLES
    coverage = square / total
    if coverage == 0:
        return (0, 0, 0, 0)
    t = y / SIZE
    base = (int(122 - 44 * t), int(167 - 74 * t), int(255 - 35 * t))
    mix = play / max(square, 1)
    color = tuple(int(base[i] * (1 - mix) + 255 * mix) for i in range(3))
    return (*color, int(255 * coverage))


def png(width, height, rows):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    raw = b"".join(b"\0" + bytes(value for px in row for value in px) for row in rows)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def ico(image):
    header = struct.pack("<HHH", 0, 1, 1)
    entry = struct.pack("<BBBBHHII", 0, 0, 0, 0, 1, 32, len(image), 22)
    return header + entry + image


def build(output):
    rows = [[pixel(x, y) for x in range(SIZE)] for y in range(SIZE)]
    image = png(SIZE, SIZE, rows)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(ico(image) if output.suffix.lower() == ".ico" else image)
    return output


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "AnyPS5.ico")
