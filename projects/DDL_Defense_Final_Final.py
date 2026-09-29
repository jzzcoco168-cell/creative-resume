import pygame
import math
import sys
import os
import random

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 1. 初始化
pygame.init()
SCREEN = pygame.display.set_mode((800, 650))
pygame.display.set_caption("算了吧！DDL终极防御战 - 黄金平衡版")

# 2. 颜色定义
WHITE     = (255, 255, 255)
BLACK     = (0,   0,   0)
RED       = (255, 50,  50)
GREEN     = (50,  255, 50)
BLUE      = (50,  150, 255)
YELLOW    = (255, 200, 50)
GRAY      = (100, 100, 100)
DARK_GRAY = (40,  40,  40)
PURPLE    = (150, 50,  255)

# 3. 字体加载（Mac 中文字体修复）
_mac_fonts = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode MS.ttf",
    "/Library/Fonts/Arial Unicode MS.ttf",
]
_font_path = None
for _p in _mac_fonts:
    if os.path.exists(_p):
        _font_path = _p
        break

if _font_path:
    FONT       = pygame.font.Font(_font_path, 18)
    LARGE_FONT = pygame.font.Font(_font_path, 48)
    HUGE_FONT  = pygame.font.Font(_font_path, 72)
else:
    FONT       = pygame.font.Font(None, 24)
    LARGE_FONT = pygame.font.Font(None, 60)
    HUGE_FONT  = pygame.font.Font(None, 80)

# 4. 路径与放置槽位
path = [(0, 300), (200, 300), (200, 100), (500, 100), (500, 450), (800, 450)]
slots = [
    pygame.Rect(100, 200, 50, 50), pygame.Rect(100, 350, 50, 50),
    pygame.Rect(250, 200, 50, 50), pygame.Rect(250, 350, 50, 50),
    pygame.Rect(400, 200, 50, 50), pygame.Rect(400, 350, 50, 50),
    pygame.Rect(550, 200, 50, 50), pygame.Rect(550, 350, 50, 50),
    pygame.Rect(650, 350, 50, 50),
]
def _load_img(path_str, size=None):
    """安全加载图片，失败返回 None"""
    try:
        img = pygame.image.load(path_str).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception:
        return None

def _placeholder(size, color, label):
    """找不到图片时用带标签的色块代替"""
    surf = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(surf, color, (0, 0, size[0], size[1]), border_radius=8)
    txt = FONT.render(label, True, WHITE)
    surf.blit(txt, (size[0]//2 - txt.get_width()//2, size[1]//2 - txt.get_height()//2))
    return surf

def _load_any(filename, size=None):
    """同时搜索根目录和 assets/ 子目录"""
    for prefix in ["", "assets/"]:
        img = _load_img(prefix + filename, size)
        if img:
            return img
    return None

_bg_raw = _load_any("bg.png", (800, 650))
if _bg_raw:
    # 给背景叠加一层半透明深色遮罩，让塔更突出
    _overlay = pygame.Surface((800, 650), pygame.SRCALPHA)
    _overlay.fill((0, 0, 0, 120))  # 数字越大越暗，120 约 47% 遮罩
    _bg_raw.blit(_overlay, (0, 0))
BG_IMAGE    = _bg_raw
HEART_FULL  = _load_any("heart_full.png",  (35, 35))
HEART_EMPTY = _load_any("heart_empty.png", (35, 35))
COIN_IMG = _load_any("coin.png", (30, 30))
# 加载怪物图片
ENEMY_IMGS = {
    "Essay":             _load_any("enemy_Essay.png",             (30, 30)),
    "Quiz":              _load_any("enemy_Quiz.png",              (30, 30)),
    "Report":            _load_any("enemy_Report.png",            (30, 30)),
    "Exam":              _load_any("enemy_Exam.png",              (30, 30)),
    "Final Presentation":_load_any("enemy_FinalPresentation.png", (70, 70)),
}

# 加载组员像素小人
MEMBERS_ALIVE = [
    _load_any("member1_alive.png", (60, 80)),
    _load_any("member2_alive.png", (60, 80)),
    _load_any("member3_alive.png", (60, 80)),
    _load_any("member4_alive.png", (60, 80))
]
MEMBERS_DEAD = [
    _load_any("member1_dead.png"),
    _load_any("member2_dead.png"),
    _load_any("member3_dead.png"),
    _load_any("member4_dead.png")
]
# 死亡状态按宽度统一缩放（横躺，保持比例）
_dead_w = 80
MEMBERS_DEAD = [
    pygame.transform.scale(img, (_dead_w, int(img.get_height() * _dead_w / img.get_width())))
    if img else None
    for img in MEMBERS_DEAD
]

# 5. 音效加载
pygame.mixer.init()
def _load_sfx(filename):
    for prefix in ["", "assets/"]:
        p = prefix + filename
        if os.path.exists(p):
            try:
                return pygame.mixer.Sound(p)
            except:
                pass
    return None

SFX_PLACE     = _load_sfx("放置.mp3")
SFX_KILL      = _load_sfx("击杀.mp3")
SFX_COUNTDOWN = _load_sfx("开始倒计时.mp3")
SFX_LEVELUP   = _load_sfx("升级音效.mp3")
SFX_WIN       = _load_sfx("胜利.mp3")
SFX_LOSE      = _load_sfx("失败1.mp3")
SFX_HURT      = _load_sfx("受伤扣血.mp3")
# 背景音乐（只加载，不立即播放，等倒计时结束后再播）
BGM_PATH = "bgm.mp3"
if os.path.exists(BGM_PATH):
    pygame.mixer.music.load(BGM_PATH)
    pygame.mixer.music.set_volume(0.5)   # 音量 0.0~1.0，可自行调整


# 6. AI 防御塔设定
GUARDS = {
    "GPT":      {"cost": 150, "color": GREEN,          "dmg": 4.0, "range": 220, "cd": 20, "desc": "High DMG All-round"},
    "Gemini":   {"cost": 120, "color": BLUE,           "dmg": 3.0, "range": 180, "cd": 25, "desc": "Mid-range Steady"},
    "DeepSeek": {"cost": 90,  "color": (50, 200, 255), "dmg": 5.0, "range": 250, "cd": 60, "desc": "Long-range Sniper"},
    "DouBao":   {"cost": 60,  "color": (255, 100, 100),"dmg": 1.2, "range": 130, "cd": 12, "desc": "Close-range Rapid"},
    "Grok":     {"cost": 40,  "color": PURPLE,         "dmg": 1.5, "range": 120, "cd": 35, "desc": "Budget Emergency"},
}
TOWER_IMAGES = {}
for _name, _stats in GUARDS.items():
    _raw = _load_any(f"tower_{_name}.png", (44, 44))
    if _raw:
        # 给每个塔图片加一个彩色发光边框，让它在背景上更突出
        _framed = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.rect(_framed, _stats["color"], (0, 0, 50, 50), border_radius=8)
        _framed.blit(_raw, (3, 3))
        TOWER_IMAGES[_name] = _framed
    else:
        TOWER_IMAGES[_name] = _placeholder((50, 50), _stats["color"], _name)

guard_names    = list(GUARDS.items())
selected_guard = None

# 6. 游戏状态
gpa_cents      = 0
money          = 200
lives          = 4
game_state     = "COUNTDOWN"
level          = 1
wave_scale     = 1.0
enemies_spawned = 0
boss_active    = False
gpa_week1      = 0
gpa_week2      = 0

# 漂浮伤害数字
class FloatingText:
    def __init__(self, text, pos, color=RED):
        self.pos    = [float(pos[0]), float(pos[1])]
        self.timer  = 40
        self.surface = FONT.render(text, True, color)

    def update_and_draw(self, screen):
        self.pos[1] -= 0.8
        self.timer  -= 1
        self.surface.set_alpha(int((self.timer / 40.0) * 255))
        screen.blit(self.surface, (int(self.pos[0]), int(self.pos[1])))
        return self.timer <= 0

floating_texts = []

# 防御塔类
class Tower:
    def __init__(self, rect, tower_type):
        self.rect     = rect
        self.type     = tower_type
        stats         = GUARDS[tower_type]
        self.color    = stats["color"]
        self.range    = stats["range"]
        self.damage   = stats["dmg"]
        self.cooldown = stats["cd"]
        self.timer    = 0

    def draw(self, screen):
        screen.blit(TOWER_IMAGES[self.type], (self.rect.x, self.rect.y))

        mx, my = pygame.mouse.get_pos()
        if self.rect.collidepoint(mx, my):
            # 攻击范围圆圈
            rng = self.range
            rs  = pygame.Surface((rng * 2, rng * 2), pygame.SRCALPHA)
            pygame.draw.circle(rs, (255, 255, 255, 40), (rng, rng), rng)
            pygame.draw.circle(rs, (255, 255, 255, 150), (rng, rng), rng, 1)
            screen.blit(rs, (self.rect.centerx - rng, self.rect.centery - rng))
            # 出售提示
            if not selected_guard:
                sell_price = GUARDS[self.type]["cost"] // 2
                sell_surf  = FONT.render(f"Sell +{sell_price/100:.2f}", True, RED)
                screen.blit(sell_surf, (self.rect.x - 10, self.rect.y - 22))

# 敌人类
class Enemy:
    _names = ["Essay", "Quiz", "Report", "Exam"]

    def __init__(self, health_multiplier, is_boss=False):
        self.pos        = list(path[0])
        self.target_idx = 1
        self.is_boss    = is_boss
        if is_boss:
            self.speed  = 0.5
            self.max_hp = 200 * health_multiplier
            self.radius = 35
            self.name   = "Final Presentation"
        else:
            self.speed  = 1.5
            self.max_hp = 12 * health_multiplier
            self.radius = 15
            self.name   = random.choice(self._names)
        self.hp = self.max_hp

    def move(self):
        if self.target_idx < len(path):
            tx, ty = path[self.target_idx]
            dx, dy = tx - self.pos[0], ty - self.pos[1]
            dist   = math.hypot(dx, dy)
            if dist < self.speed:
                self.target_idx += 1
            else:
                self.pos[0] += dx / dist * self.speed
                self.pos[1] += dy / dist * self.speed
        return self.target_idx >= len(path)

    def draw(self, screen):
        cx, cy = int(self.pos[0]), int(self.pos[1])
        img = ENEMY_IMGS.get(self.name)
        if img:
            screen.blit(img, (cx - img.get_width() // 2, cy - img.get_height() // 2))
        else:
            color = PURPLE if self.is_boss else RED
            pygame.draw.circle(screen, color, (cx, cy), self.radius)

        # 名字标签
        ns = FONT.render(self.name, True, WHITE)
        screen.blit(ns, (cx - ns.get_width() // 2, cy + self.radius + 4))

        # 血条（受伤后才显示）
        if self.hp < self.max_hp:
            bw = self.radius * 2
            bx = cx - self.radius
            by = cy - self.radius - 12
            pygame.draw.rect(screen, BLACK, (bx, by, bw, 6))
            fill = max(0, int((bw - 2) * self.hp / self.max_hp))
            pygame.draw.rect(screen, RED,   (bx + 1, by + 1, fill, 4))

# 全局列表
enemies, towers, bullets = [], [], []
spawn_timer = 0
clock       = pygame.time.Clock()

# 重置 / 下一关
def reset_game():
    global gpa_cents, lives, game_state, level, wave_scale, enemies_spawned, boss_active, spawn_timer, selected_guard
    gpa_cents = 0; money = 200; lives = 4; game_state = "COUNTDOWN"; level = 1
    wave_scale = 1.0; enemies_spawned = 0; boss_active = False
    spawn_timer = 0; selected_guard = None
    enemies.clear(); towers.clear(); bullets.clear(); floating_texts.clear()

def start_next_level():
    global game_state, level, enemies_spawned, boss_active, wave_scale, spawn_timer, gpa_cents, money
    level += 1; enemies_spawned = 0; boss_active = False
    global gpa_week1, gpa_week2
    if level == 2:          # 刚从第1周进入第2周
        gpa_week1 = gpa_cents
    gpa_cents = 0           # 每周GPA重新从0开始
    game_state = "COUNTDOWN"; spawn_timer = 0; money = 200
    if SFX_COUNTDOWN: SFX_COUNTDOWN.play()
    towers.clear(); enemies.clear(); bullets.clear(); floating_texts.clear()
    wave_scale = 1.0 + (level - 1) * 0.3

# 主循环
countdown_timer = 0   # 倒计时帧计数器（60帧=1秒）
while True:
    mx, my   = pygame.mouse.get_pos()
    btn_next = pygame.Rect(200, 350, 150, 50)
    btn_quit = pygame.Rect(450, 350, 150, 50)

    # ── 事件处理 ──
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if event.key == pygame.K_r and game_state == "GAME_OVER":
                reset_game()
            if event.key in (pygame.K_p, pygame.K_SPACE):
                if game_state == "PLAYING":
                    game_state = "PAUSED"
                    pygame.mixer.music.pause()   # 暂停时音乐暂停
                elif game_state == "PAUSED":
                    game_state = "PLAYING"
                    pygame.mixer.music.unpause() # 恢复时音乐继续

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "GAME_OVER":
                reset_game()
            elif game_state == "LEVEL_WIN":
                if btn_next.collidepoint(mx, my): start_next_level()
                if btn_quit.collidepoint(mx, my): pygame.quit(); sys.exit()
            elif game_state == "GRADUATION":
                if btn_next.collidepoint(mx, my): reset_game() 
                if btn_quit.collidepoint(mx, my): pygame.quit(); sys.exit()
            elif game_state == "PLAYING":
                clicked_card = False
                for i, (name, stats) in enumerate(guard_names):
                    card_rect = pygame.Rect(90 + i * 130, 560, 90, 80)
                    if card_rect.collidepoint(mx, my):
                        clicked_card = True
                        if money >= stats["cost"]:
                            selected_guard = name
                        break

                if not clicked_card:
                    occupied = [t.rect for t in towers]
                    if selected_guard:
                        for slot in slots:
                            if slot.collidepoint(mx, my) and slot not in occupied:
                                towers.append(Tower(slot, selected_guard))
                                if SFX_PLACE: SFX_PLACE.play()
                                money -= GUARDS[selected_guard]["cost"]
                                selected_guard = None
                                break
                    else:
                        for t in towers[:]:
                            if t.rect.collidepoint(mx, my):
                                money += GUARDS[t.type]["cost"] // 2
                                towers.remove(t)
                                break

                if not clicked_card and my < 550 and not any(s.collidepoint(mx, my) for s in slots):
                    selected_guard = None

    # ── 绘制背景 ──
    if BG_IMAGE:
        SCREEN.blit(BG_IMAGE, (0, 0))
    else:
        SCREEN.fill((20, 30, 50))

    # ── 绘制路径 ──
    pygame.draw.lines(SCREEN, (50, 60, 80), False, path, 42)
    pygame.draw.lines(SCREEN, (80, 95, 115), False, path, 30)

    # ── 绘制槽位 ──
    occupied = [t.rect for t in towers]
    for slot in slots:
        if slot not in occupied:
            if selected_guard:
                if slot.collidepoint(mx, my):
                    prev = TOWER_IMAGES[selected_guard].copy()
                    prev.set_alpha(160)
                    SCREEN.blit(prev, (slot.x, slot.y))
                    pygame.draw.rect(SCREEN, GREEN, slot, 2, border_radius=5)
                    rng = GUARDS[selected_guard]["range"]
                    pygame.draw.circle(SCREEN, GREEN, slot.center, rng, 1)
                else:
                    pygame.draw.rect(SCREEN, YELLOW, slot, 1, border_radius=5)
            else:
                pygame.draw.rect(SCREEN, GRAY, slot, 1, border_radius=5)

    # ── 绘制塔、敌人、子弹 ──
    for t in towers:
        t.draw(SCREEN)
    for e in enemies:
        e.draw(SCREEN)
    for sp, ep, col, btype in bullets:
        if btype == "GPT":
            # 绿色粗激光 + 大爆炸点
            pygame.draw.line(SCREEN, (0, 255, 120), sp, ep, 4)
            pygame.draw.circle(SCREEN, WHITE, (int(ep[0]), int(ep[1])), 7)
        elif btype == "Gemini":
            # 彩虹双线
            pygame.draw.line(SCREEN, (100, 100, 255), sp, ep, 2)
            pygame.draw.line(SCREEN, (255, 100, 255), (sp[0]+3, sp[1]+3), (ep[0]+3, ep[1]+3), 2)
        elif btype == "DeepSeek":
            # 蓝色粗射线（狙击风格）
            pygame.draw.line(SCREEN, (50, 200, 255), sp, ep, 6)
            pygame.draw.circle(SCREEN, (200, 240, 255), (int(ep[0]), int(ep[1])), 10)
        elif btype == "DouBao":
            # 橙色光球（速射风格）
            pygame.draw.circle(SCREEN, (255, 200, 0), (int(ep[0]), int(ep[1])), 7)
            pygame.draw.circle(SCREEN, WHITE, (int(ep[0]), int(ep[1])), 3)
        elif btype == "Grok":
            # 紫色闪电折线
            mid = ((sp[0]+ep[0])//2 + 10, (sp[1]+ep[1])//2 - 10)
            pygame.draw.line(SCREEN, PURPLE, sp, mid, 2)
            pygame.draw.line(SCREEN, PURPLE, mid, ep, 2)

    # ── 游戏逻辑 ──
        # ── 倒计时状态 ──
    if game_state == "COUNTDOWN":
        countdown_timer += 1
        # 第一帧播放音效
        if countdown_timer == 1 and SFX_COUNTDOWN:
            SFX_COUNTDOWN.play()
        # 计算当前显示的数字（每90帧换一个，共360帧=6秒）
        if countdown_timer <= 40:
            cd_num = "3"
        elif countdown_timer <= 80:
            cd_num = "2"
        elif countdown_timer <= 120:
            cd_num = "1"
        elif countdown_timer <= 200:
            cd_num = "GO!"
        else:
            game_state = "PLAYING"
            countdown_timer = 0
            # 倒计时结束，开始播放背景音乐
            if os.path.exists(BGM_PATH) and not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)
        
        if game_state == "COUNTDOWN":
            # 缩放动画：每个数字从大到小（zoom效果）
            if cd_num == "GO!":
                phase = (countdown_timer - 121) % 80
                scale = 2.0 - (phase / 80) * 1.0
            else:
                phase = (countdown_timer - 1) % 40
                scale = 2.5 - (phase / 40) * 1.5
            
            # 绘制背景（游戏画面）
            if BG_IMAGE:
                SCREEN.blit(BG_IMAGE, (0, 0))
            else:
                SCREEN.fill((20, 30, 50))
            
            # 绘制半透明遮罩
            overlay = pygame.Surface((800, 650), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            SCREEN.blit(overlay, (0, 0))
            
            # 绘制缩放数字
            base_size = 120
            dyn_size = max(20, int(base_size * scale))
            if _font_path:
                cd_font = pygame.font.Font(_font_path, dyn_size)
            else:
                cd_font = pygame.font.Font(None, dyn_size)
            
            # 颜色：3=红，2=橙，1=黄，GO=绿
            cd_colors = {"3": (255, 80, 80), "2": (255, 160, 50), "1": (255, 220, 50), "GO!": (80, 255, 120)}
            cd_surf = cd_font.render(cd_num, True, cd_colors.get(cd_num, WHITE))
            cx = 400 - cd_surf.get_width() // 2
            cy = 280 - cd_surf.get_height() // 2
            SCREEN.blit(cd_surf, (cx, cy))
            
            pygame.display.flip()
            pygame.time.Clock().tick(60)
            continue

    if game_state == "PLAYING":
        bullets.clear()

        # 生成敌人
        if not boss_active:
            spawn_timer += 1
            if spawn_timer > 60:
                if enemies_spawned < 30:
                    enemies.append(Enemy(wave_scale))
                    enemies_spawned += 1
                    spawn_timer = 0
                    wave_scale += 0.01
                else:
                    enemies.append(Enemy(wave_scale, is_boss=True))
                    boss_active = True
                    spawn_timer = 0

        # 移动敌人
        for e in enemies[:]:
            if e.move():
                enemies.remove(e)
                lives -= 1
                floating_texts.append(FloatingText("DDL Slipped Through！", e.pos, RED))
                if SFX_HURT: SFX_HURT.play()
                if e.is_boss:
                    boss_active = False
                    lives -= 1
                    floating_texts.append(FloatingText("Failed Final！-2❤", e.pos, RED))
                    if level >= 2:
                        gpa_week2 = gpa_cents
                        gpa_cents = (gpa_week1 + gpa_week2) // 2
                        if SFX_WIN: SFX_WIN.play()
                        pygame.mixer.music.stop()

                        game_state = "GRADUATION"   # Boss漏掉也算毕业
                    else:
                        start_next_level()          # 第1关Boss漏掉，进第2关
                if lives <= 0:
                    if SFX_LOSE: SFX_LOSE.play()
                    pygame.mixer.music.stop()
                    game_state = "GAME_OVER"

        # 塔攻击
        for t in towers:
            if t.timer > 0:
                t.timer -= 1
            in_range = [e for e in enemies
                        if math.hypot(t.rect.centerx - e.pos[0],
                                      t.rect.centery - e.pos[1]) < t.range]
            if in_range and t.timer == 0:
                target = in_range[0]
                target.hp -= t.damage
                t.timer = t.cooldown
                bullets.append((t.rect.center, tuple(target.pos), t.color,t.type))
                floating_texts.append(FloatingText(f"-{t.damage:.1f}",
                                                   (target.pos[0] + 12, target.pos[1] - 20),
                                                   YELLOW))
                if target.hp <= 0 and target in enemies:
                    enemies.remove(target)
                    if SFX_KILL: SFX_KILL.play()
                    if target.is_boss:
                        gpa_cents += 100
                        money += 50
                        if level >= 2:
                            gpa_week2 = gpa_cents
                            gpa_cents = (gpa_week1 + gpa_week2) // 2  # 取平均
                            if SFX_WIN: SFX_WIN.play()                            
                            game_state = "GRADUATION"
                        else:
                            if SFX_LEVELUP: SFX_LEVELUP.play()
                            game_state = "LEVEL_WIN"
                    else:
                        gpa_cents += 10    # 小怪击杀 GPA +0.1
                        money += 10        # 小怪击杀 奖励$0.10

    # ── 漂浮文字 ──
    for ft in floating_texts[:]:
        if ft.update_and_draw(SCREEN):
            floating_texts.remove(ft)

    # ── 底部 UI 栏 ──
    pygame.draw.rect(SCREEN, DARK_GRAY, (0, 550, 800, 100))
    # 绘制组员小人（左下角位置，横向排列）
    start_x = 30
    start_y = 460  # 放在底部UI栏的上方
    for i in range(4):
        # 根据当前 lives 判断状态
        is_alive = (i < lives)
        img_to_draw = MEMBERS_ALIVE[i] if is_alive else MEMBERS_DEAD[i]
        
        if img_to_draw:
            if is_alive:
                SCREEN.blit(img_to_draw, (start_x + i * 65, start_y))
            else:
                # 死亡状态底部对齐站立位置
                dead_y = start_y + 90 - img_to_draw.get_height()
                SCREEN.blit(img_to_draw, (start_x + i * 65, dead_y))

    # 顶部状态框（去掉黑框，改成半透明小标签）
    # 第一行：GPA（y=8）
    gpa_text = FONT.render(f"GPA: {gpa_cents/100:.2f}", True, YELLOW)
    pygame.draw.rect(SCREEN, (0, 0, 0), (8, 8, gpa_text.get_width() + 14, 30), border_radius=4)
    SCREEN.blit(gpa_text, (15, 10))

    # 第二行：钱（y=8+32=40）
    money_text = FONT.render(f"${money/100:.2f}", True, (50, 255, 150))
    coin_w = 24 if COIN_IMG else 0
    pygame.draw.rect(SCREEN, (0, 0, 0), (8, 40, coin_w + money_text.get_width() + 14, 26), border_radius=4)
    if COIN_IMG:
        SCREEN.blit(COIN_IMG, (10, 37))
        SCREEN.blit(money_text, (10 + coin_w + 2, 43))
    else:
        SCREEN.blit(money_text, (15, 43))

    # 第三行：爱心（y=40+32=72）
    if HEART_FULL and HEART_EMPTY:
        for i in range(4):
            himg = HEART_FULL if i < lives else HEART_EMPTY
            SCREEN.blit(himg, (10 + i * 30, 72))
    else:
        SCREEN.blit(FONT.render(f"Lives: {lives}/4", True, RED), (15, 74))

    SCREEN.blit(FONT.render(f"Semester {level}", True, WHITE), (632, 18))
    if not boss_active:
        SCREEN.blit(FONT.render(f"Progress: {enemies_spawned}/30", True, WHITE), (632, 44))
    else:
        SCREEN.blit(FONT.render("!! FINAL PRESENTATION !!", True, RED), (580, 44))

    # 卡牌
    for i, (name, stats) in enumerate(guard_names):
        cx   = 90 + i * 130
        cy   = 560
        rect = pygame.Rect(cx, cy, 90, 80)
        cost = stats["cost"]

        if name == selected_guard:
            pygame.draw.rect(SCREEN, YELLOW, rect, border_radius=10)
            pygame.draw.rect(SCREEN, BLACK, rect.inflate(-6, -6), border_radius=8)
        else:
            pygame.draw.rect(SCREEN, (55, 55, 55), rect, border_radius=10)
            border_col = WHITE if money >= cost else GRAY
            pygame.draw.rect(SCREEN, border_col, rect, 2, border_radius=10)

        # 卡牌图标（居中，图标上移留出价格空间）
        SCREEN.blit(TOWER_IMAGES[name], (cx + 23, cy + 5))
        # 价格（大字居中，颜色区分是否买得起）
        price_col = YELLOW if money >= cost else (160, 160, 160)
        price_surf = pygame.font.Font(_font_path if _font_path else None, 17).render(
            f"${cost/100:.2f}", True, price_col)
        # 价格背景小条，让文字更清晰
        price_bg = pygame.Rect(cx + 2, cy + 60, 86, 18)
        pygame.draw.rect(SCREEN, (0, 0, 0), price_bg, border_radius=4)
        SCREEN.blit(price_surf, (cx + 45 - price_surf.get_width()//2, cy + 61))

        if rect.collidepoint(mx, my):
            ds = FONT.render(stats["desc"], True, WHITE)
            pygame.draw.rect(SCREEN, BLACK, (cx, cy - 28, ds.get_width() + 10, 24), border_radius=4)
            SCREEN.blit(ds, (cx + 5, cy - 24))

    hint1 = FONT.render("[P] Pause", True, (150, 150, 150))
    hint2 = FONT.render("[ESC] Quit", True, (150, 150, 150))
    SCREEN.blit(hint1, (800 - hint1.get_width() - 10, 608))
    SCREEN.blit(hint2, (800 - hint2.get_width() - 10, 628))

    # ── 弹窗层 ──
    if game_state == "PAUSED":
        ov = pygame.Surface((800, 650), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 150))
        SCREEN.blit(ov, (0, 0))
        SCREEN.blit(HUGE_FONT.render("PAUSED", True, YELLOW), (270, 260))

    elif game_state == "LEVEL_WIN":
        ov = pygame.Surface((800, 650), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 180))
        SCREEN.blit(ov, (0, 0))
        clr_surf = LARGE_FONT.render(f"Semester {level} Cleared!", True, GREEN)
        SCREEN.blit(clr_surf, (400 - clr_surf.get_width()//2, 200))
        pygame.draw.rect(SCREEN, GREEN, btn_next, border_radius=10)
        nw_surf = FONT.render("Next Semester", True, BLACK)
        SCREEN.blit(nw_surf, (btn_next.centerx - nw_surf.get_width()//2, btn_next.centery - nw_surf.get_height()//2))
        pygame.draw.rect(SCREEN, RED, btn_quit, border_radius=10)
        gu_surf = FONT.render("Give Up", True, WHITE)
        SCREEN.blit(gu_surf, (btn_quit.centerx - gu_surf.get_width()//2, btn_quit.centery - gu_surf.get_height()//2))

    elif game_state == "GRADUATION":
        ov = pygame.Surface((800, 650), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 200))
        SCREEN.blit(ov, (0, 0))
        grad_surf = LARGE_FONT.render("Congratulations, Graduate!", True, (255, 215, 0))
        SCREEN.blit(grad_surf, (400 - grad_surf.get_width()//2, 160))
        sub_surf = FONT.render("You survived a whole year of DDLs!", True, WHITE)
        SCREEN.blit(sub_surf, (400 - sub_surf.get_width()//2, 240))
        gpa_surf = FONT.render(f"Final GPA: {gpa_cents/100:.2f} / 4.00", True, YELLOW)
        SCREEN.blit(gpa_surf, (400 - gpa_surf.get_width()//2, 275))
        # 重新开始按钮
        pygame.draw.rect(SCREEN, GREEN, btn_next, border_radius=10)
        nw_surf = FONT.render("Play Again", True, BLACK)
        SCREEN.blit(nw_surf, (btn_next.centerx - nw_surf.get_width()//2, btn_next.centery - nw_surf.get_height()//2))
        # 退出按钮
        pygame.draw.rect(SCREEN, RED, btn_quit, border_radius=10)
        gu_surf = FONT.render("Quit", True, WHITE)
        SCREEN.blit(gu_surf, (btn_quit.centerx - gu_surf.get_width()//2, btn_quit.centery - gu_surf.get_height()//2))

    elif game_state == "GAME_OVER":
        ov = pygame.Surface((800, 650), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 180))
        SCREEN.blit(ov, (0, 0))
        go_surf = LARGE_FONT.render("GAME OVER", True, RED)
        SCREEN.blit(go_surf, (400 - go_surf.get_width()//2, 250))
        rs_surf = FONT.render("Click or press [R] to restart", True, WHITE)
        SCREEN.blit(rs_surf, (400 - rs_surf.get_width()//2, 320))

    pygame.display.flip()
    clock.tick(60)
