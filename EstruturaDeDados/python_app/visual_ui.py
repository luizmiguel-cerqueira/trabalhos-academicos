from __future__ import annotations

import random
import sys

import pygame

from .controller import AppController
from .native_api import KIND_LIST, KIND_QUEUE, KIND_STACK


pygame.init()
HISTORY = 99


class VisualUI:
    def __init__(self, app: AppController) -> None:
        self.app = app
        self.i18n = app.i18n
        self.screen = pygame.display.set_mode((1408, 880), pygame.RESIZABLE)
        pygame.display.set_caption("Estruturas de Dados")
        self.clock = pygame.time.Clock()
        self.running = True
        self.selected_kind = KIND_QUEUE
        self.field_value = ""
        self.field_insert = ""
        self.field_remove = ""
        self.active_input: str | None = None
        self.horizontal_scroll = 0
        self.follow_horizontal_end = True
        self.history_scroll = 0
        self.mouse_pos = (0, 0)
        self.pressed: str | None = None
        self.focused: str | None = None
        self.modal_action: str | None = None
        self.modal_kind: int | None = None
        self.animation_until = 0
        self.tabs: dict[int, pygame.Rect] = {}
        self.actions: dict[str, pygame.Rect] = {}
        self.pointer_addresses: dict[tuple[int, tuple[int, ...]], list[str]] = {}
        self.random_source = random.SystemRandom()
        self.colors = {
            "bg": (8, 12, 24), "panel": (16, 24, 38), "surface": (20, 31, 48),
            "card": (30, 63, 108), "primary": (78, 144, 255),
            "primary_light": (142, 196, 255), "text": (240, 245, 255),
            "muted": (168, 188, 220), "border": (86, 130, 210),
        }
        self.font_title = self._font(33, True)
        self.font_heading = self._font(24, True)
        self.font = self._font(17)
        self.font_small = self._font(15)
        self.status = app.status_message

    def _font(self, size: int, bold: bool = False):
        for name in ("arial", "tahoma", "verdana", "sans-serif"):
            try:
                return pygame.font.SysFont(name, size, bold=bold)
            except Exception:
                continue
        return pygame.font.Font(None, size)

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
            elif event.type == pygame.MOUSEWHEEL and self.selected_kind in (KIND_QUEUE, KIND_LIST):
                self.horizontal_scroll -= event.y * 120
                self.follow_horizontal_end = False
            elif event.type == pygame.MOUSEWHEEL and self.selected_kind == HISTORY:
                self.history_scroll -= event.y * 40
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.pressed = self._hit(event.pos)
                if self.modal_action is not None:
                    self._modal_click(event.pos)
                else:
                    self._click(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.pressed = None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self._focus_next(event.mod & pygame.KMOD_SHIFT)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.focused:
                    if self.focused == "field_remove":
                        self._action("remove_value")
                    elif self.focused == "field_insert":
                        self._action("insert")
                    else:
                        self._activate_focused()
                elif event.key == pygame.K_SPACE and self.focused and not self.focused.startswith("field_"):
                    self._activate_focused()
                elif event.key == pygame.K_BACKSPACE and self.active_input:
                    self._active_field_set(self._active_field_value()[:-1])
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.active_input:
                    self._action("remove_value" if self.active_input == "remove" else "insert")
                elif event.key == pygame.K_ESCAPE:
                    if self.modal_action is not None:
                        self._close_modal()
                    else:
                        self.active_input = False
                        pygame.key.stop_text_input()
            elif event.type == pygame.TEXTINPUT and self.active_input:
                current_value = self._active_field_value()
                if (event.text.isdigit() or (event.text == "-" and not current_value)) and len(current_value) < 32:
                    self._active_field_set(current_value + event.text)

    def _hit(self, position: tuple[int, int]) -> str | None:
        for kind, rect in self.tabs.items():
            if rect.collidepoint(position):
                return f"tab_{kind}"
        for action, rect in self.actions.items():
            if rect.collidepoint(position):
                return action
        return "input" if self._input_rect().collidepoint(position) else None

    def _click(self, position: tuple[int, int]) -> None:
        if self._language_rect().collidepoint(position):
            self.i18n.language = "en" if self.i18n.language == "pt" else "pt"
            return
        if position[0] >= self.screen.get_width() - 130 and 47 <= position[1] <= 85:
            if self._has_session_data():
                self._open_modal("exit")
            else:
                self.running = False
            return
        for kind, rect in self.tabs.items():
            if rect.collidepoint(position):
                self.selected_kind = kind
                self.field_value = ""
                self.field_insert = ""
                self.field_remove = ""
                self.active_input = None
                self.focused = f"tab_{kind}"
                pygame.key.stop_text_input()
                return
        if self._input_rect().collidepoint(position):
            self.active_input = "insert"
            self.focused = "field_insert"
            pygame.key.start_text_input()
            return
        if self.selected_kind == KIND_LIST and self._remove_input_rect().collidepoint(position):
            self.active_input = "remove"
            self.focused = "field_remove"
            pygame.key.start_text_input()
            return
        for action, rect in self.actions.items():
            if rect.collidepoint(position):
                if not self._action_enabled(action):
                    return
                if action == "clear":
                    self._open_modal("clear", self.selected_kind)
                    return
                self.focused = action
                if action == "insert":
                    self.active_input = "insert"
                elif action == "remove_value":
                    self.active_input = "remove"
                else:
                    self.active_input = None
                if self.active_input:
                    pygame.key.start_text_input()
                else:
                    pygame.key.stop_text_input()
                self._action(action)
                return

    def _focus_order(self) -> list[str]:
        order = [f"tab_{kind}" for kind in (KIND_QUEUE, KIND_STACK, KIND_LIST, HISTORY)]
        if self.selected_kind != HISTORY:
            order.append("field_insert")
            if self.selected_kind == KIND_LIST:
                order.append("field_remove")
            order.extend(self.actions.keys())
        else:
            order.extend(("history_prev", "history_next"))
        return order

    def _focus_next(self, reverse: bool = False) -> None:
        order = self._focus_order()
        if not order:
            return
        if self.focused not in order:
            index = -1
        else:
            index = order.index(self.focused)
        self.focused = order[(index - 1 if reverse else index + 1) % len(order)]
        if self.focused == "field_insert":
            self.active_input = "insert"
            pygame.key.start_text_input()
        elif self.focused == "field_remove":
            self.active_input = "remove"
            pygame.key.start_text_input()
        else:
            self.active_input = None
            pygame.key.stop_text_input()

    def _activate_focused(self) -> None:
        if self.focused is None:
            return
        if self.focused.startswith("tab_"):
            kind = int(self.focused.removeprefix("tab_"))
            self._click(self.tabs[kind].center)
        elif self.focused == "field_insert":
            self.active_input = "insert"
            pygame.key.start_text_input()
        elif self.focused == "field_remove":
            self.active_input = "remove"
            pygame.key.start_text_input()
        elif self.focused in self.actions:
            if self._action_enabled(self.focused):
                self._action(self.focused)

    def _has_session_data(self) -> bool:
        return bool(self.app.history or any(self.app.get_tab_values(kind) for kind in (KIND_QUEUE, KIND_STACK, KIND_LIST)))

    def _open_modal(self, action: str, kind: int | None = None) -> None:
        self.modal_action = action
        self.modal_kind = kind
        self.active_input = None
        pygame.key.stop_text_input()

    def _close_modal(self) -> None:
        self.modal_action = None
        self.modal_kind = None
        self.pressed = None

    def _modal_rects(self) -> tuple[pygame.Rect, pygame.Rect]:
        center_x = self.screen.get_width() // 2
        center_y = self.screen.get_height() // 2
        return (
            pygame.Rect(center_x - 175, center_y + 45, 140, 42),
            pygame.Rect(center_x + 35, center_y + 45, 140, 42),
        )

    def _modal_click(self, position: tuple[int, int]) -> None:
        cancel_rect, confirm_rect = self._modal_rects()
        if cancel_rect.collidepoint(position):
            self._close_modal()
        elif confirm_rect.collidepoint(position):
            if self.modal_action == "clear" and self.modal_kind is not None:
                result = self.app.handle_clear(self.modal_kind)
                self.status = "Estrutura limpa" if result == "ok" else result
            elif self.modal_action == "exit":
                self.running = False
            self._close_modal()

    def _input_rect(self) -> pygame.Rect:
        return pygame.Rect(60, 690, 180, 42)

    def _language_rect(self) -> pygame.Rect:
        return pygame.Rect(self.screen.get_width() - 260, 47, 100, 38)

    def _remove_input_rect(self) -> pygame.Rect:
        return pygame.Rect(260, 690, 180, 42)

    def _active_field_value(self) -> str:
        if self.active_input == "remove":
            return self.field_remove
        if self.selected_kind == KIND_LIST and self.active_input == "insert":
            return self.field_insert
        return self.field_value

    def _active_field_set(self, value: str) -> None:
        if self.active_input == "remove":
            self.field_remove = value
        elif self.selected_kind == KIND_LIST and self.active_input == "insert":
            self.field_insert = value
        else:
            self.field_value = value

    def _action_enabled(self, action: str) -> bool:
        if action == "history_prev":
            return self.app.history_page > 0
        if action == "history_next":
            total = self.app.history_count()
            last_page = max(0, (total + self.app.page_size - 1) // self.app.page_size - 1)
            return self.app.history_page < last_page
        values = self.app.get_tab_values(self.selected_kind)
        if action == "insert":
            return len(values) < 10
        if action in {"remove_first", "remove_value", "clear"}:
            return bool(values)
        return True

    def _value(self) -> int | None:
        value_text = self._active_field_value()
        if value_text in ("", "-"):
            return None
        try:
            value = int(value_text)
        except ValueError:
            return None
        return value if -2147483648 <= value <= 2147483647 else None

    def _action(self, action: str) -> None:
        if action == "insert":
            value = self._value()
            if value is None:
                self.status = self.i18n.text("valid_integer")
                return
            result = self.app.handle_insert(self.selected_kind, value)
            self.status = self.i18n.text("inserted") if result == "ok" else result
            if result == "ok":
                self._active_field_set("")
                self.animation_until = pygame.time.get_ticks() + 200
                self.follow_horizontal_end = True
                pygame.key.start_text_input()
        elif action == "remove_first":
            result = self.app.handle_remove_first(self.selected_kind)
            self.status = self.i18n.text("removed") if result == "ok" else result
            if result == "ok":
                self.animation_until = pygame.time.get_ticks() + 200
        elif action == "remove_value":
            value = self._value()
            if value is None:
                self.status = self.i18n.text("valid_integer")
                return
            result = self.app.handle_remove_value(self.selected_kind, value)
            self.status = self.i18n.text("value_removed") if result == "ok" else result
            if result == "ok":
                self.field_remove = ""
                self.animation_until = pygame.time.get_ticks() + 200
        elif action == "clear":
            result = self.app.handle_clear(self.selected_kind)
            self.status = self.i18n.text("cleared") if result == "ok" else result
            if result == "ok":
                self.animation_until = pygame.time.get_ticks() + 200
        elif action == "history_prev":
            self.app.prev_history_page()
            self.status = "Página anterior"
        elif action == "history_next":
            self.app.next_history_page()
            self.status = "Próxima página"

    def draw(self) -> None:
        self.screen.fill(self.colors["bg"])
        self._header()
        self._tabs()
        self._structure()
        self._action_panel()
        if self.modal_action is not None:
            self._modal()
        pygame.display.flip()

    def _rect(self, rect: pygame.Rect, color: tuple[int, int, int]) -> None:
        pygame.draw.rect(self.screen, color, rect, border_radius=18)
        pygame.draw.rect(self.screen, self.colors["border"], rect, 1, border_radius=18)

    def _button(self, rect: pygame.Rect, label: str, key: str, color=None, disabled: bool = False) -> None:
        fill = color or self.colors["primary"]
        if disabled:
            fill = self.colors["panel"]
        if self.pressed == key:
            fill = (48, 98, 175)
        elif not disabled and rect.collidepoint(self.mouse_pos) and fill == self.colors["primary"]:
            fill = (112, 178, 255)
        pygame.draw.rect(self.screen, fill, rect, border_radius=10)
        border = self.colors["border"] if disabled else self.colors["primary_light"]
        pygame.draw.rect(self.screen, border, rect, 1, border_radius=10)
        if self.focused == key:
            pygame.draw.rect(self.screen, self.colors["text"], rect.inflate(6, 6), 2, border_radius=12)
        text = self.font_small.render(label, True, self.colors["text"])
        self.screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))

    def _header(self) -> None:
        width = self.screen.get_width()
        self._rect(pygame.Rect(30, 20, width - 60, 99), self.colors["panel"])
        self.screen.blit(self.font_title.render(self.i18n.text("title"), True, self.colors["text"]), (62, 51))
        self._button(self._language_rect(), "PT / EN", "language", self.colors["panel"])
        self._button(pygame.Rect(width - 130, 47, 65, 38), self.i18n.text("exit"), "exit")

    def _tabs(self) -> None:
        self.tabs.clear()
        options = ((KIND_QUEUE, self.i18n.text("queue")), (KIND_STACK, self.i18n.text("stack")), (KIND_LIST, self.i18n.text("list")), (HISTORY, self.i18n.text("history")))
        for index, (kind, label) in enumerate(options):
            rect = pygame.Rect(45 + index * 200, 135, 175, 42)
            self.tabs[kind] = rect
            color = self.colors["primary"] if kind == self.selected_kind else self.colors["panel"]
            self._button(rect, label, f"tab_{kind}", color)

    def _structure(self) -> None:
        panel = pygame.Rect(30, 195, self.screen.get_width() - 60, 440)
        self._rect(panel, self.colors["surface"])
        if pygame.time.get_ticks() < self.animation_until:
            pygame.draw.rect(self.screen, self.colors["primary_light"], panel.inflate(-4, -4), 3, border_radius=16)
        if self.selected_kind == HISTORY:
            self._history_view(panel)
            return
        names = {KIND_QUEUE: (self.i18n.text("queue").upper(), self.i18n.text("fifo")), KIND_STACK: (self.i18n.text("stack").upper(), self.i18n.text("lifo")), KIND_LIST: (self.i18n.text("list").upper(), self.i18n.text("linked"))}
        title, description = names[self.selected_kind]
        self.screen.blit(self.font_title.render(title, True, self.colors["text"]), (60, 220))
        self.screen.blit(self.font.render(description, True, self.colors["muted"]), (60, 265))
        values = self.app.get_tab_values(self.selected_kind)
        if not values:
            self.screen.blit(self.font.render(self.i18n.text("no_nodes"), True, self.colors["muted"]), (60, 360))
        elif len(values) >= 10:
            self.screen.blit(self.font.render(self.i18n.text("full_state"), True, self.colors["primary_light"]), (60, 295))
            if self.selected_kind == KIND_STACK:
                self._stack(values)
            else:
                self._horizontal(values, self.selected_kind == KIND_QUEUE)
        elif self.selected_kind == KIND_STACK:
            self._stack(values)
        else:
            self._horizontal(values, self.selected_kind == KIND_QUEUE)

    def _history_view(self, panel: pygame.Rect) -> None:
        self.screen.blit(self.font_title.render(self.i18n.text("history").upper(), True, self.colors["text"]), (60, 220))
        self.screen.blit(self.font.render(self.i18n.text("history_description"), True, self.colors["muted"]), (60, 265))
        kind_names = {
            KIND_QUEUE: self.i18n.text("history_kind_queue"),
            KIND_STACK: self.i18n.text("history_kind_stack"),
            KIND_LIST: self.i18n.text("history_kind_list"),
        }
        action_names = {
            1: self.i18n.text("history_action_insert"),
            2: self.i18n.text("history_action_remove_first"),
            3: self.i18n.text("history_action_remove_by_value"),
            4: self.i18n.text("history_action_clear"),
        }
        unknown_kind = self.i18n.text("history_kind_unknown")
        value_label = self.i18n.text("history_value")
        quantity_label = self.i18n.text("history_quantity")
        if not self.app.history:
            self.screen.blit(self.font.render(self.i18n.text("history_empty"), True, self.colors["muted"]), (60, 340))
            return
        row_height = 25
        history_top = 315
        history_bottom = panel.bottom - 20
        max_scroll = max(0, len(self.app.history) * row_height - (history_bottom - history_top))
        self.history_scroll = max(0, min(self.history_scroll, max_scroll))
        self.screen.set_clip(pygame.Rect(panel.x + 20, history_top - 5, panel.width - 40, history_bottom - history_top + 10))
        try:
            for index, entry in enumerate(self.app.history):
                action = action_names.get(entry.action, self.i18n.text("history_kind_unknown"))
                kind = kind_names.get(entry.kind, unknown_kind)
                detail = f"#{entry.sequence:03d}   {kind:<6}   {action:<18}   {value_label}={entry.value}   {quantity_label}={entry.quantity}"
                self.screen.blit(self.font_small.render(detail, True, self.colors["text"]), (65, history_top + index * row_height - self.history_scroll))
        finally:
            self.screen.set_clip(None)
        if max_scroll > 0:
            track = pygame.Rect(panel.right - 28, history_top, 5, history_bottom - history_top)
            thumb_height = max(35, int(track.height * (track.height / (track.height + max_scroll))))
            thumb_y = track.y + int((track.height - thumb_height) * (self.history_scroll / max_scroll))
            pygame.draw.rect(self.screen, self.colors["border"], track, border_radius=3)
            pygame.draw.rect(self.screen, self.colors["primary_light"], (track.x, thumb_y, track.width, thumb_height), border_radius=3)

    def _node(self, x: int, y: int, value: int, pointer: str) -> None:
        value_rect = pygame.Rect(x, y, 82, 54)
        pointer_rect = pygame.Rect(x + 82, y, 58, 54)
        pygame.draw.rect(self.screen, self.colors["card"], value_rect, border_radius=7)
        pygame.draw.rect(self.screen, self.colors["primary_light"], value_rect, 2, border_radius=7)
        pygame.draw.rect(self.screen, self.colors["panel"], pointer_rect)
        pygame.draw.rect(self.screen, self.colors["primary_light"], pointer_rect, 2)
        value_text = self.font.render(str(value), True, self.colors["text"])
        pointer_text = self.font_small.render(pointer, True, self.colors["muted"])
        self.screen.blit(value_text, (value_rect.centerx - value_text.get_width() // 2, y + 17))
        self.screen.blit(pointer_text, (pointer_rect.centerx - pointer_text.get_width() // 2, y + 18))

    def _random_addresses(self, values: list[int]) -> list[str]:
        key = (self.selected_kind, tuple(values))
        cached = self.pointer_addresses.get(key)
        if cached is not None:
            return cached
        candidates = list(range(0x1000, 0x10000, 0x40))
        addresses = [f"0x{value:04X}" for value in self.random_source.sample(candidates, len(values))]
        self.pointer_addresses[key] = addresses
        return addresses

    def _horizontal(self, values: list[int], is_queue: bool) -> None:
        viewport = pygame.Rect(55, 350, self.screen.get_width() - 110, 225)
        entry_width = self.font_small.size(self.i18n.text("input"))[0] if is_queue else 0
        entry_extra = 150 + entry_width if is_queue else 0
        content_end = 180 + (len(values) - 1) * 170 + entry_extra
        visible_end = viewport.right - 10
        max_scroll = max(0, content_end - visible_end)
        if self.follow_horizontal_end:
            self.horizontal_scroll = max_scroll
        self.horizontal_scroll = max(0, min(self.horizontal_scroll, max_scroll))
        start_x = 180 - self.horizontal_scroll
        addresses = self._random_addresses(values)
        self.screen.set_clip(viewport)
        try:
            if is_queue:
                self.screen.blit(self.font_small.render(self.i18n.text("output"), True, self.colors["primary_light"]), (start_x, 375))
                last_x = start_x + (len(values) - 1) * 170
                entry_x = last_x + 150
                self.screen.blit(self.font_small.render(self.i18n.text("input"), True, self.colors["primary_light"]), (entry_x, 443))
                pygame.draw.line(self.screen, self.colors["primary_light"], (last_x + 140, 452), (entry_x - 8, 452), 2)
                pygame.draw.polygon(self.screen, self.colors["primary_light"], [(entry_x - 16, 446), (entry_x - 6, 452), (entry_x - 16, 458)])
            else:
                self.screen.blit(self.font_small.render(self.i18n.text("start"), True, self.colors["primary_light"]), (75, 375))
            x = start_x
            for index, value in enumerate(values):
                pointer = "NULL" if index == len(values) - 1 else addresses[index + 1]
                self._node(x, 425, value, pointer)
                if index < len(values) - 1:
                    pygame.draw.line(self.screen, self.colors["primary_light"], (x + 140, 452), (x + 170, 452), 2)
                    pygame.draw.polygon(self.screen, self.colors["primary_light"], [(x + 162, 446), (x + 172, 452), (x + 162, 458)])
                x += 170
            if max_scroll > 0:
                track = pygame.Rect(180, 570, viewport.right - 190, 5)
                thumb_width = max(80, int(track.width * (track.width / (track.width + max_scroll))))
                thumb_x = track.x + int((track.width - thumb_width) * (self.horizontal_scroll / max_scroll))
                pygame.draw.rect(self.screen, self.colors["border"], track, border_radius=3)
                pygame.draw.rect(self.screen, self.colors["primary_light"], (thumb_x, track.y, thumb_width, track.height), border_radius=3)
        finally:
            self.screen.set_clip(None)

    def _stack(self, values: list[int]) -> None:
        node_x = 620
        top_text = self.font_small.render(self.i18n.text("top"), True, self.colors["primary_light"])
        base_text = self.font_small.render(self.i18n.text("base"), True, self.colors["primary_light"])
        self.screen.blit(top_text, (node_x + (108 - top_text.get_width()) // 2, 200))
        base_y = 225 + (len(values) - 1) * 35 + 38
        self.screen.blit(base_text, (node_x + (108 - base_text.get_width()) // 2, base_y))
        for index, value in enumerate(values):
            y = 225 + index * 35
            rect = pygame.Rect(node_x, y, 108, 32)
            pygame.draw.rect(self.screen, self.colors["card"], rect, border_radius=8)
            pygame.draw.rect(self.screen, self.colors["primary_light"], rect, 2, border_radius=8)
            text = self.font_small.render(str(value), True, self.colors["text"])
            self.screen.blit(text, (rect.centerx - text.get_width() // 2, y + 7))
            if index < len(values) - 1:
                pygame.draw.line(self.screen, self.colors["primary_light"], (674, y + 32), (674, y + 35), 2)

    def _action_panel(self) -> None:
        panel = pygame.Rect(800, 650, 570, 145)
        self._rect(panel, self.colors["surface"])
        if self.selected_kind == HISTORY:
            self.actions.clear()
            self.screen.blit(self.font.render(self.i18n.text("history_navigation"), True, self.colors["muted"]), (825, 670))
            for action, label, x in (("history_prev", self.i18n.text("previous"), 825), ("history_next", self.i18n.text("next"), 950)):
                rect = pygame.Rect(x, 710, 110, 34)
                self.actions[action] = rect
                self._button(rect, label, action, disabled=not self._action_enabled(action))
            self.screen.blit(self.font_small.render(f"Página: {self.app.history_page + 1}", True, self.colors["muted"]), (1085, 720))
            return
        names = {KIND_QUEUE: f"{self.i18n.text('actions')}: {self.i18n.text('queue')}", KIND_STACK: f"{self.i18n.text('actions')}: {self.i18n.text('stack')}", KIND_LIST: f"{self.i18n.text('actions')}: {self.i18n.text('list')}"}
        self.screen.blit(self.font.render(names[self.selected_kind], True, self.colors["muted"]), (825, 670))
        self.actions.clear()
        if self.selected_kind == KIND_LIST:
            buttons = [("insert", self.i18n.text("insert_end"), 825, 710, 140), ("remove_first", self.i18n.text("remove_first"), 973, 710, 145), ("remove_value", self.i18n.text("remove_by_value"), 825, 755, 130), ("clear", self.i18n.text("clear_list"), 963, 755, 120)]
        elif self.selected_kind == KIND_STACK:
            buttons = [("insert", self.i18n.text("push"), 825, 710, 105), ("remove_first", self.i18n.text("pop"), 938, 710, 125), ("clear", self.i18n.text("clear_stack"), 1071, 710, 120)]
        else:
            buttons = [("insert", self.i18n.text("enqueue"), 825, 710, 115), ("remove_first", self.i18n.text("dequeue"), 948, 710, 135), ("clear", self.i18n.text("clear_queue"), 1091, 710, 110)]
        for action, label, x, y, width in buttons:
            rect = pygame.Rect(x, y, width, 34)
            self.actions[action] = rect
            self._button(rect, label, action, disabled=not self._action_enabled(action))
        input_rect = self._input_rect()
        input_rects = [(input_rect, self.i18n.text("insert_value"), self.field_insert if self.selected_kind == KIND_LIST else self.field_value, "insert")]
        if self.selected_kind == KIND_LIST:
            input_rects.append((self._remove_input_rect(), self.i18n.text("remove_value"), self.field_remove, "remove"))
        for rect, label, value, field_name in input_rects:
            pygame.draw.rect(self.screen, self.colors["panel"], rect, border_radius=8)
            border = self.colors["primary_light"] if self.active_input == field_name else self.colors["border"]
            pygame.draw.rect(self.screen, border, rect, 2, border_radius=8)
            self.screen.blit(self.font_small.render(label, True, self.colors["muted"]), (rect.x, 670))
            if value:
                self.screen.blit(self.font.render(value, True, self.colors["text"]), (rect.x + 12, rect.y + 11))
        self.screen.blit(self.font_small.render(self.i18n.text("last_action"), True, self.colors["muted"]), (60, 765))
        self.screen.blit(self.font.render(self.status, True, self.colors["text"]), (155, 761))

    def _modal(self) -> None:
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        self.screen.blit(overlay, (0, 0))
        width, height = self.screen.get_size()
        box = pygame.Rect(width // 2 - 260, height // 2 - 100, 520, 210)
        self._rect(box, self.colors["panel"])
        if self.modal_action == "clear":
            count = len(self.app.get_tab_values(self.modal_kind or KIND_QUEUE))
            title = self.i18n.text("confirm_clear_title")
            message = self.i18n.text("clear_message").format(count=count)
        else:
            title = self.i18n.text("exit_title")
            message = self.i18n.text("exit_message")
        self.screen.blit(self.font_heading.render(title, True, self.colors["text"]), (box.x + 28, box.y + 26))
        self.screen.blit(self.font.render(message, True, self.colors["muted"]), (box.x + 28, box.y + 72))
        cancel_rect, confirm_rect = self._modal_rects()
        self._button(cancel_rect, self.i18n.text("cancel"), "modal_cancel", self.colors["panel"])
        self._button(confirm_rect, self.i18n.text("confirm_clear"), "modal_confirm")


def main() -> None:
    VisualUI(AppController()).run()
