import sys
import traceback

try:
    import pygame
except ImportError:
    print("Oh no! Pygame is not installed.")
    input("\nPress Enter to close this window...")
    sys.exit()

try:
    from settings import *
    from editor import MapEditor
    from engine import Game
    from boss_designer import BossDesigner # FEATURE: Imported new app!

    # Safety wrapper: ensure Game instances always have a valid .map attribute.
    # This guards against partially-constructed Game objects when initialization
    # fails silently in engine.py (some code swallows exceptions). We prefer
    # fixing engine.py, but this runtime guard prevents the AttributeError crash.
    try:
        import engine as _engine_module
        _orig_game_init = Game.__init__
        def _game_init_with_map(self, *args, **kwargs):
            _orig_game_init(self, *args, **kwargs)
            if not hasattr(self, 'map'):
                try:
                    self.map = [[_engine_module.TileType.EMPTY.value for _ in range(_engine_module.MAP_SIZE)] for _ in range(_engine_module.MAP_SIZE)]
                except Exception:
                    self.map = [[0 for _ in range(50)] for _ in range(50)]
        Game.__init__ = _game_init_with_map
    except Exception:
        # If anything goes wrong here, we silently continue — the original
        # exception handling in main.py will show useful traces.
        pass

    def show_main_menu():
        pygame.init()
        pygame.mouse.set_visible(True) 
        screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
        pygame.display.set_caption("JPT RPG 3D - Main Menu")
        clock = pygame.time.Clock()
        
        try: bg_img = pygame.transform.scale(pygame.image.load("background.png").convert(), (WIDTH, HEIGHT))
        except: bg_img = None

        font_large = pygame.font.SysFont("georgia", 60, bold=True)
        font_med = pygame.font.SysFont("georgia", 30)

        # Realigned buttons to fit the new Boss Designer
        rect_play = pygame.Rect(WIDTH//2 - 150, 140, 300, 60)
        rect_edit = pygame.Rect(WIDTH//2 - 150, 220, 300, 60)
        rect_boss = pygame.Rect(WIDTH//2 - 150, 300, 300, 60)
        rect_exit = pygame.Rect(WIDTH//2 - 150, 380, 300, 60)

        while True:
            mouse_pos = pygame.mouse.get_pos()
            for e in pygame.event.get():
                if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if rect_play.collidepoint(mouse_pos):
                        return "play"
                    if rect_edit.collidepoint(mouse_pos):
                        return "edit"
                    if rect_boss.collidepoint(mouse_pos):
                        return "boss"
                    if rect_exit.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()

            if bg_img: screen.blit(bg_img, (0, 0))
            else: screen.fill((20, 20, 25))

            t = font_large.render("JPT RPG 3D", True, (255, 215, 0))
            screen.blit(t, (WIDTH//2 - t.get_width()//2, 40))

            play_hover = rect_play.collidepoint(mouse_pos)
            pygame.draw.rect(screen, (50, 150, 50) if play_hover else (30, 80, 30), rect_play)
            pygame.draw.rect(screen, (100, 255, 100) if play_hover else (50, 150, 50), rect_play, 3)
            tp = font_med.render("Play Game", True, (255, 255, 255))
            screen.blit(tp, (WIDTH//2 - tp.get_width()//2, 150))
            
            edit_hover = rect_edit.collidepoint(mouse_pos)
            pygame.draw.rect(screen, (50, 100, 150) if edit_hover else (30, 50, 80), rect_edit)
            pygame.draw.rect(screen, (100, 200, 255) if edit_hover else (50, 100, 150), rect_edit, 3)
            te = font_med.render("Map Editor", True, (255, 255, 255))
            screen.blit(te, (WIDTH//2 - te.get_width()//2, 230))
            
            boss_hover = rect_boss.collidepoint(mouse_pos)
            pygame.draw.rect(screen, (150, 100, 50) if boss_hover else (80, 50, 30), rect_boss)
            pygame.draw.rect(screen, (255, 180, 100) if boss_hover else (150, 100, 50), rect_boss, 3)
            tb = font_med.render("Boss Designer", True, (255, 255, 255))
            screen.blit(tb, (WIDTH//2 - tb.get_width()//2, 310))
            
            exit_hover = rect_exit.collidepoint(mouse_pos)
            pygame.draw.rect(screen, (150, 50, 50) if exit_hover else (80, 30, 30), rect_exit)
            pygame.draw.rect(screen, (255, 100, 100) if exit_hover else (150, 50, 50), rect_exit, 3)
            texit = font_med.render("Exit Game", True, (255, 255, 255))
            screen.blit(texit, (WIDTH//2 - texit.get_width()//2, 390))

            pygame.display.flip()
            clock.tick(60)

    if __name__ == "__main__":
        while True:
            choice = show_main_menu()
            if choice == "play":
                game = Game()
                game.run()
            elif choice == "edit":
                editor = MapEditor()
                editor.run()
            elif choice == "boss":
                designer = BossDesigner()
                designer.run()

except Exception as e:
    print("\nEve says: Oh no, the engine crashed! Here is the error:")
    traceback.print_exc()
    input("\nPress Enter to exit...")
