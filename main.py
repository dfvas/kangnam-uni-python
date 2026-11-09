
import pygame
import math
import sys

pygame.init()

WIDTH, HEIGHT = 1000, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Toodee & Topdee - Perspective Transition")
clock = pygame.time.Clock()

# --------------------------------------------------
# 기본 설정
# --------------------------------------------------

BG = (245, 226, 218)
DARK = (39, 23, 62)
SOIL = (91, 54, 74)
GRASS = (117, 185, 76)
GRID = (255, 255, 255)

BLUE = (65, 151, 255)
GREEN = (73, 199, 132)

transitioning = False
transition_time = 0
TRANSITION_DURATION = 1.2

view = 0  # 0: 횡스크롤, 1: 탑다운


def lerp(a, b, t):
    return a + (b - a) * t


def smooth(t):
    return t * t * (3 - 2 * t)


def mix_color(a, b, t):
    return tuple(int(lerp(a[i], b[i], t)) for i in range(3))


# --------------------------------------------------
# 화면에 배치할 오브젝트
# 각 오브젝트는 시작 위치와 도착 위치를 가짐
# --------------------------------------------------

# x, y, width, height
platforms = [
    # 횡스크롤 위치       # 탑다운 위치
    ((70, 90, 180, 35),   (80, 80, 220, 65)),
    ((430, 410, 100, 45), (400, 360, 150, 90)),
    ((570, 300, 180, 40), (650, 170, 170, 100)),
    ((750, 200, 120, 45), (700, 380, 190, 100)),
]

crates = [
    ((180, 330, 42, 48), (220, 180, 52, 52)),
    ((360, 420, 42, 48), (330, 410, 52, 52)),
    ((520, 340, 42, 48), (520, 300, 52, 52)),
]

# 캐릭터 위치
player_start = (480, 320)
player_end = (350, 300)


# --------------------------------------------------
# 배경
# --------------------------------------------------

def draw_background(surface, t):
    color = mix_color(BG, (250, 241, 220), t)
    surface.fill(color)

    # 배경의 장식 원
    pygame.draw.circle(
        surface,
        mix_color((240, 190, 210), (245, 226, 195), t),
        (WIDTH // 2, HEIGHT // 2 - 40),
        170
    )


# --------------------------------------------------
# 맵 테두리
# --------------------------------------------------

def draw_map_border(surface, t):
    x = int(lerp(30, 25, t))
    y = int(lerp(45, 35, t))
    w = int(lerp(760, 900, t))
    h = int(lerp(500, 540, t))

    # 바깥 테두리
    pygame.draw.rect(
        surface, SOIL,
        (x, y, w, h),
        border_radius=8
    )

    pygame.draw.rect(
        surface, DARK,
        (x + 12, y + 12, w - 24, h - 24),
        border_radius=5,
        width=8
    )

    # 탑다운으로 갈수록 격자 배경이 강조됨
    if t > 0:
        grid_surface = pygame.Surface(
            (WIDTH, HEIGHT), pygame.SRCALPHA
        )

        alpha = int(130 * t)

        for gx in range(x + 20, x + w - 15, 32):
            pygame.draw.line(
                grid_surface,
                (*GRID, alpha),
                (gx, y + 15),
                (gx, y + h - 15),
                1
            )

        for gy in range(y + 20, y + h - 15, 32):
            pygame.draw.line(
                grid_surface,
                (*GRID, alpha),
                (x + 15, gy),
                (x + w - 15, gy),
                1
            )

        surface.blit(grid_surface, (0, 0))


# --------------------------------------------------
# 발판
# --------------------------------------------------

def draw_platform(surface, platform, t):
    side, top = platform

    x = int(lerp(side[0], top[0], t))
    y = int(lerp(side[1], top[1], t))
    w = int(lerp(side[2], top[2], t))
    h = int(lerp(side[3], top[3], t))

    # 횡스크롤: 옆면이 보이는 플랫폼
    side_height = int(h * (1 - t) * 0.65)

    if side_height > 0:
        pygame.draw.rect(
            surface,
            SOIL,
            (x, y + h - side_height, w, side_height)
        )

    # 위쪽 표면
    top_color = mix_color(GRASS, (75, 130, 90), t)

    pygame.draw.rect(
        surface,
        top_color,
        (x, y, w, max(4, h - side_height))
    )

    # 가장자리
    pygame.draw.line(
        surface,
        (180, 225, 120),
        (x, y),
        (x + w, y),
        4
    )

    # 탑다운에서 타일처럼 보이는 내부 선
    if t > 0.2:
        alpha = int(100 * t)
        tile_surface = pygame.Surface(
            (w, h), pygame.SRCALPHA
        )

        for gx in range(0, w, 24):
            pygame.draw.line(
                tile_surface,
                (220, 255, 220, alpha),
                (gx, 0), (gx, h), 1
            )

        for gy in range(0, h, 24):
            pygame.draw.line(
                tile_surface,
                (220, 255, 220, alpha),
                (0, gy), (w, gy), 1
            )

        surface.blit(tile_surface, (x, y))


# --------------------------------------------------
# 상자
# --------------------------------------------------

def draw_crate(surface, crate, t):
    side, top = crate

    x = int(lerp(side[0], top[0], t))
    y = int(lerp(side[1], top[1], t))
    w = int(lerp(side[2], top[2], t))
    h = int(lerp(side[3], top[3], t))

    shadow_offset = int(8 * (1 - t))

    pygame.draw.rect(
        surface,
        (65, 45, 43),
        (x + shadow_offset, y + shadow_offset, w, h)
    )

    pygame.draw.rect(
        surface,
        (153, 104, 57),
        (x, y, w, h)
    )

    pygame.draw.rect(
        surface,
        (218, 174, 99),
        (x + 4, y + 4, w - 8, h - 8),
        3
    )

    pygame.draw.line(
        surface,
        (100, 65, 38),
        (x + w // 2, y + 5),
        (x + w // 2, y + h - 5),
        3
    )


# --------------------------------------------------
# 캐릭터
# --------------------------------------------------

def draw_player(surface, t):
    x = lerp(player_start[0], player_end[0], t)
    y = lerp(player_start[1], player_end[1], t)

    # 캐릭터 색상 전환
    color_t = max(0, min(1, (t - 0.35) / 0.3))
    body_color = mix_color(BLUE, GREEN, color_t)

    # 전환 도중 살짝 작아지는 효과
    squash = 1 - 0.25 * math.sin(math.pi * t)

    w = int(42 * squash)
    h = 55

    # 그림자
    pygame.draw.ellipse(
        surface,
        (80, 70, 90),
        (int(x - 22), int(y + 20), 45, 15)
    )

    # 몸통
    pygame.draw.rect(
        surface,
        body_color,
        (int(x - w // 2), int(y - h // 2), w, h),
        border_radius=10
    )

    # 머리
    pygame.draw.circle(
        surface,
        body_color,
        (int(x), int(y - 15)),
        23
    )

    # 눈
    pygame.draw.circle(
        surface, (255, 255, 255),
        (int(x - 8), int(y - 17)), 5
    )

    pygame.draw.circle(
        surface, (255, 255, 255),
        (int(x + 8), int(y - 17)), 5
    )

    pygame.draw.circle(
        surface, DARK,
        (int(x - 7), int(y - 17)), 2
    )

    pygame.draw.circle(
        surface, DARK,
        (int(x + 9), int(y - 17)), 2
    )


# --------------------------------------------------
# 전체 장면 렌더링
# --------------------------------------------------

def render_scene(t):
    scene = pygame.Surface((WIDTH, HEIGHT))

    draw_background(scene, t)
    draw_map_border(scene, t)

    for platform in platforms:
        draw_platform(scene, platform, t)

    for crate in crates:
        draw_crate(scene, crate, t)

    draw_player(scene, t)

    return scene


# --------------------------------------------------
# 메인 루프
# --------------------------------------------------

running = True

while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not transitioning:
                transitioning = True
                transition_time = 0

    # 애니메이션 진행
    if transitioning:
        transition_time += dt

        progress = min(
            transition_time / TRANSITION_DURATION,
            1
        )

        t = smooth(progress)

        if progress >= 1:
            transitioning = False
            view = 1 - view

    else:
        t = float(view)

    # 장면 생성
    scene = render_scene(t)

    # 전환 중 화면 확대 효과
    if transitioning:
        zoom = 1 + 0.035 * math.sin(math.pi * t)

        new_w = int(WIDTH * zoom)
        new_h = int(HEIGHT * zoom)

        scene = pygame.transform.smoothscale(
            scene, (new_w, new_h)
        )

        offset_x = (new_w - WIDTH) // 2
        offset_y = (new_h - HEIGHT) // 2

        screen.blit(
            scene,
            (-offset_x, -offset_y)
        )

    else:
        screen.blit(scene, (0, 0))

    # 안내
    font = pygame.font.SysFont("arial", 24)

    label = (
        "Toodee - Side View"
        if t < 0.5
        else "Topdee - Top View"
    )

    text = font.render(label, True, DARK)
    screen.blit(text, (30, 15))

    hint = font.render("SPACE : Change Perspective", True, DARK)
    screen.blit(hint, (WIDTH - 330, 15))

    pygame.display.flip()

pygame.quit()
sys.exit()
