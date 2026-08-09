import pygame
import math
from pathlib import Path
import settings

def load_image(filename, colorkey=None):
    image_path = Path(__file__).resolve().parents[1] / settings.IMAGE_FOLDER / filename
    if not image_path.exists():
        return None
    image = pygame.image.load(str(image_path))
    if image.get_alpha() is not None:
        return image.convert_alpha()
    if pygame.display.get_surface() is not None:
        image = image.convert()
    if image.get_alpha() is None:
        if colorkey is None:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)
    return image

def distance(a, b):
	"""Return distance between two (x,y) pairs or Vector2s."""
	ax, ay = a
	bx, by = b
	return math.hypot(bx - ax, by - ay)

def check_collision_rect(a: pygame.Rect, b: pygame.Rect) -> bool:
	return a.colliderect(b)

def draw_text(surface, text, size, pos, color=(255,255,255), font_name=None, center=True, bold=False, shadow=False):
    font = pygame.font.SysFont(font_name, size, bold=bold)
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    if shadow:
        shadow_surf = font.render(text, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect()
        if center:
            shadow_rect.center = (pos[0] + 2, pos[1] + 2)
        else:
            shadow_rect.topleft = (pos[0] + 2, pos[1] + 2)
        surface.blit(shadow_surf, shadow_rect)
    surface.blit(surf, rect)


def draw_bar(surface, rect, fill_fraction, bg_color=(40, 40, 40), fill_color=(255, 215, 0)):
    pygame.draw.rect(surface, bg_color, rect, border_radius=10)
    inner = rect.inflate(-6, -6)
    inner.width = max(0, min(int(inner.width * max(0.0, min(fill_fraction, 1.0))), inner.width))
    pygame.draw.rect(surface, fill_color, inner, border_radius=8)


def blur_surface(surface, scale=0.14, passes=2):
    if scale <= 0 or scale >= 1:
        return surface.copy()
    size = surface.get_size()
    small = pygame.transform.smoothscale(surface, (max(1, int(size[0] * scale)), max(1, int(size[1] * scale))))
    for _ in range(passes):
        small = pygame.transform.smoothscale(small, size)
        small = pygame.transform.smoothscale(small, (max(1, int(size[0] * scale)), max(1, int(size[1] * scale))))
    return pygame.transform.smoothscale(small, size)


def draw_button(surface, rect, text, font_name=None, text_color=(255, 255, 255), bg_color=(35, 35, 35), border_color=(255, 255, 255), border_width=2):
    pygame.draw.rect(surface, bg_color, rect, border_radius=14)
    pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=14)
    draw_text(surface, text, 24, rect.center, text_color, font_name, center=True, bold=True, shadow=True)


def draw_rhombus(surface, center, size, color, border_color=None, border_width=0):
	cx, cy = center
	half = size / 2
	points = [
		(cx, cy - half),
		(cx + half, cy),
		(cx, cy + half),
		(cx - half, cy),
	]
	pygame.draw.polygon(surface, color, points)
	if border_color is not None and border_width > 0:
		pygame.draw.polygon(surface, border_color, points, width=border_width)


def draw_pixel_heart(surface, top_left, pixel_size=4, fill_level=2, color=(220, 60, 60), empty_color=(20, 20, 20)):
    """Draw a small pixel-art heart at top_left. fill_level is 0=empty, 1=half, 2=full."""
    # more detailed heart pattern with light and shadow pixels
    pattern = [
        (1, 0, 'light'), (4, 0, 'light'),
        (0, 1, 'dark'), (1, 1, 'main'), (2, 1, 'main'), (3, 1, 'main'), (4, 1, 'main'), (5, 1, 'dark'),
        (0, 2, 'dark'), (1, 2, 'main'), (2, 2, 'highlight'), (3, 2, 'highlight'), (4, 2, 'main'), (5, 2, 'dark'),
        (1, 3, 'dark'), (2, 3, 'main'), (3, 3, 'main'), (4, 3, 'dark'),
        (2, 4, 'dark'), (3, 4, 'dark'),
    ]
    bright = (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
    dark = (max(color[0] - 40, 0), max(color[1] - 40, 0), max(color[2] - 40, 0))
    highlight = (min(color[0] + 60, 255), min(color[1] + 60, 255), min(color[2] + 60, 255))
    for (px, py, tone) in pattern:
        if fill_level == 0:
            draw_color = empty_color
        elif fill_level == 2:
            if tone == 'main':
                draw_color = color
            elif tone == 'light':
                draw_color = bright
            elif tone == 'highlight':
                draw_color = highlight
            else:
                draw_color = dark
        else:
            if px <= 2:
                if tone == 'main':
                    draw_color = color
                elif tone == 'light':
                    draw_color = bright
                elif tone == 'highlight':
                    draw_color = highlight
                else:
                    draw_color = dark
            else:
                draw_color = empty_color
        r = pygame.Rect(top_left[0] + px * pixel_size, top_left[1] + py * pixel_size, pixel_size, pixel_size)
        pygame.draw.rect(surface, draw_color, r)


def draw_hearts(surface, x, y, count, max_hearts=5, pixel_size=4, spacing=6, filled_color=(220, 60, 60), empty_color=(20, 20, 20)):
    """Draw up to max_hearts hearts in a row at (x,y), where count is half-heart units."""
    remaining = max(0, int(count))
    for i in range(max_hearts):
        hx = x + i * (pixel_size * 6 + spacing)
        if remaining >= 2:
            fill_level = 2
        elif remaining == 1:
            fill_level = 1
        else:
            fill_level = 0
        draw_pixel_heart(surface, (hx, y), pixel_size=pixel_size, fill_level=fill_level, color=filled_color, empty_color=empty_color)
        remaining -= 2