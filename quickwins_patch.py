"""
quickwins_patch.py

This module monkeypatches engine.Game at import-time to apply quick, low-risk
performance improvements without editing engine.py directly.

Applied quick-wins:
- Use a deque-compatible class for projectiles (supports pop(0) calls as popleft).
- Precompute star positions once and replace per-frame random generation.
- Add mark_save_dirty() and a debounced flush inside update() by wrapping Game.update.
- Build a static sprite cache and ensure build_interactables() populates it.

This file imports engine and patches Game immediately when imported.
"""
from collections import deque
import random
import types

class DequeCompat(deque):
    """A small deque subclass that supports pop(i) where i==0 behaves like popleft.
    For other indices we fall back to list-based removal (rare path).
    """
    def pop(self, idx=None):
        if idx is None:
            return super().pop()
        if idx == 0:
            return super().popleft()
        # fallback: convert to list, pop index, rebuild deque
        lst = list(self)
        val = lst.pop(idx)
        self.clear()
        super().extend(lst)
        return val

def apply_quickwins():
    try:
        import engine
    except Exception:
        # engine not available at patch time
        return

    Game = engine.Game

    # Wrap __init__ to convert projectiles to DequeCompat and precompute stars
    orig_init = Game.__init__
    def patched_init(self, *args, **kwargs):
        orig_init(self, *args, **kwargs)
        # Convert projectiles list -> DequeCompat for efficient popleft usage
        try:
            if not isinstance(getattr(self, 'projectiles', None), DequeCompat):
                self.projectiles = DequeCompat(getattr(self, 'projectiles', []))
        except Exception:
            self.projectiles = DequeCompat()
        # Precompute stars if not present
        if not hasattr(self, '_stars') or not self._stars:
            try:
                self._stars = [(random.randint(0, engine.WIDTH), random.randint(0, engine.HEIGHT // 2), random.randint(1,2)) for _ in range(100)]
            except Exception:
                self._stars = [(random.randint(0, 800), random.randint(0, 300), random.randint(1,2)) for _ in range(100)]
        # Save debounce fields
        if not hasattr(self, '_save_dirty'):
            self._save_dirty = False
            self._save_timer = 0
            try:
                self._save_interval = engine.FPS * 2
            except Exception:
                self._save_interval = 120
        # ensure static_sprites exists
        if not hasattr(self, 'static_sprites'):
            self.static_sprites = []
    Game.__init__ = patched_init

    # Add mark_save_dirty
    def mark_save_dirty(self):
        self._save_dirty = True
        self._save_timer = 0
    Game.mark_save_dirty = mark_save_dirty

    # Wrap update to flush saves periodically before original update logic
    if not hasattr(Game, '_orig_update'):
        orig_update = Game.update
        def patched_update(self, *args, **kwargs):
            try:
                if getattr(self, '_save_dirty', False):
                    self._save_timer += 1
                    if self._save_timer >= getattr(self, '_save_interval', 120):
                        # call real save_game_state if present
                        try:
                            self.save_game_state()
                        except Exception:
                            pass
                        self._save_dirty = False
                        self._save_timer = 0
            except Exception:
                pass
            return orig_update(self, *args, **kwargs)
        Game._orig_update = orig_update
        Game.update = patched_update

    # Patch draw_stars to use precomputed star positions
    def patched_draw_stars(self):
        try:
            if self.time < 600 or self.time > 1800:
                star_alpha = 1.0
                if 'rain' in getattr(self, 'weather_type', '') or 'sand' in getattr(self, 'weather_type', ''):
                    star_alpha = max(0, 1.0 - (getattr(self, 'weather_intensity', 0.0) * 1.5))
                if star_alpha > 0:
                    brightness = int((200 + 55 * ( (1 if not hasattr(self,'time') else math.sin(self.time / 100)) )) * star_alpha)
                    # self._stars items are (x,y,radius)
                    for sx, sy, r in getattr(self, '_stars', []):
                        try:
                            pygame.draw.circle(self.screen, (brightness, brightness, brightness), (sx, sy), r)
                        except Exception:
                            pass
        except Exception:
            # fallback to original behavior if something goes wrong
            try:
                return original_draw_stars(self)
            except Exception:
                pass
    # Save original if present
    import math, pygame
    original_draw_stars = getattr(Game, 'draw_stars', None)
    Game.draw_stars = patched_draw_stars

    # Build static sprite cache method
    def build_static_sprites(self):
        self.static_sprites = []
        try:
            h = len(self.map)
            w = len(self.map[0]) if h else 0
            for y in range(h):
                for x in range(w):
                    val = self.map[y][x]
                    if val == engine.TileType.TREE.value:
                        tex = self.tree_leafy_sprites[(x * 73 + y * 31) % len(self.tree_leafy_sprites)] if hasattr(self, 'tree_leafy_sprites') and self.tree_leafy_sprites else None
                        if tex: self.static_sprites.append({'x': x * engine.TILE_SIZE + 32, 'y': y * engine.TILE_SIZE + 32, 'tex': tex})
                    elif val == engine.TileType.DEAD_TREE.value:
                        if hasattr(self, 'tree_dead_sprite'): self.static_sprites.append({'x': x * engine.TILE_SIZE + 32, 'y': y * engine.TILE_SIZE + 32, 'tex': self.tree_dead_sprite})
                    elif val == engine.TileType.BUSH.value:
                        tex = self.bush_sprites[(x * 53 + y * 89) % len(self.bush_sprites)] if hasattr(self, 'bush_sprites') and self.bush_sprites else None
                        if tex: self.static_sprites.append({'x': x * engine.TILE_SIZE + 32, 'y': y * engine.TILE_SIZE + 32, 'tex': tex})
                    elif val == engine.TileType.ROCK.value:
                        if hasattr(self, 'rock_sprite'): self.static_sprites.append({'x': x * engine.TILE_SIZE + 32, 'y': y * engine.TILE_SIZE + 32, 'tex': self.rock_sprite})
                    elif val == engine.TileType.STANDING_TORCH.value:
                        if hasattr(self, 'torch_sprite'): self.static_sprites.append({'x': x * engine.TILE_SIZE + 32, 'y': y * engine.TILE_SIZE + 32, 'tex': self.torch_sprite})
        except Exception:
            pass
    Game.build_static_sprites = build_static_sprites

    # Wrap build_interactables to ensure static sprite cache is built
    orig_build_interactables = Game.build_interactables
    def patched_build_interactables(self, *a, **k):
        r = orig_build_interactables(self, *a, **k)
        try:
            if hasattr(self, 'build_static_sprites'):
                self.build_static_sprites()
        except Exception:
            pass
        return r
    Game.build_interactables = patched_build_interactables

# Apply immediately
apply_quickwins()
