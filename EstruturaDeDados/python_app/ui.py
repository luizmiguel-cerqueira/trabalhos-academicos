from __future__ import annotations

import sys

import pygame

from .controller import AppController
from .native_api import KIND_LIST, KIND_QUEUE, KIND_STACK


pygame.init()


class DataStructuresUI:
    def __init__(self, app: AppController) -> None:
        self.app = app
        self.i18n = app.i18n
        self.screen = None
        self.clock = pygame.time.Clock()
        self.running = True
        self.tab = KIND_QUEUE
        self.field_value = ""
        self.field_value_list = ""
        self.field_remove_value = ""
        self.status_message = "Pronto"
        self.modal_active = False
        self.active_input = "main"
        self.mouse_pos = (0, 0)
        self.pressed_button = None
        self._setup_window()

        self.dark = (248, 250, 252)
        self.light = (15, 23, 42)
        self.white = (15, 23, 42)
        self.blue = (96, 165, 250)
        self.blue_soft = (30, 41, 59)
        self.gray = (148, 163, 184)
        self.gray_soft = (51, 65, 85)
        self.border = (71, 85, 105)
        self.red = (248, 113, 113)
        self.green = (74, 222, 128)

    def _setup_window(self) -> None:
        pygame.display.set_caption("Estruturas de Dados")
        self.screen = pygame.display.set_mode((1280, 800), pygame.RESIZABLE)
        self.font = self._font(20)
        self.font_bold = self._font(22, bold=True)
        self.font_small = self._font(16)
        self.font_title = self._font(30, bold=True)

    def _font(self, size: int, bold: bool = False):
        candidates = ["arial", "tahoma", "verdana", "sans-serif"]
        for name in candidates:
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
                return

            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.pressed_button = self._button_under_cursor(event.pos)
                self._handle_click(event.pos)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.pressed_button = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.modal_active = False
                    self.active_input = None
                    continue

                if event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                    self._delete_from_active_field()
                    continue

                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._trigger_action_by_current_tab()
                    continue

            if event.type == pygame.TEXTINPUT:
                text = event.text
                if not text:
                    continue
                if self.active_input == "main":
                    if text.isdigit() or (text == "-" and not self.field_value):
                        if len(self.field_value) < 32:
                            self.field_value += text
                elif self.active_input == "list_insert":
                    if text.isdigit() or (text == "-" and not self.field_value_list):
                        if len(self.field_value_list) < 32:
                            self.field_value_list += text
                elif self.active_input == "list_remove":
                    if text.isdigit() or (text == "-" and not self.field_remove_value):
                        if len(self.field_remove_value) < 32:
                            self.field_remove_value += text

    def _handle_click(self, pos):
        if self.tab == KIND_QUEUE:
            if self._rect_contains(120, 620, 160, 40, pos):
                self.active_input = "main"
            if self._rect_contains(340, 620, 150, 40, pos):
                self._trigger_queue_enqueue()
            if self._rect_contains(510, 620, 150, 40, pos):
                self._trigger_queue_dequeue()
            if self._rect_contains(680, 620, 170, 40, pos):
                self._trigger_queue_clear()
        elif self.tab == KIND_STACK:
            if self._rect_contains(120, 620, 160, 40, pos):
                self.active_input = "main"
            if self._rect_contains(340, 620, 150, 40, pos):
                self.status_message = "Empilhar"
            if self._rect_contains(510, 620, 150, 40, pos):
                self.status_message = "Desempilhar"
            if self._rect_contains(680, 620, 170, 40, pos):
                self.status_message = "Limpar pilha"
        else:
            if self._rect_contains(120, 620, 150, 40, pos):
                self.active_input = "list_insert"
            if self._rect_contains(300, 620, 150, 40, pos):
                self.active_input = "list_remove"

    def _rect_contains(self, x, y, w, h, pos):
        rect = pygame.Rect(x, y, w, h)
        return rect.collidepoint(pos)

    def _button_under_cursor(self, pos):
        if self.tab == KIND_QUEUE:
            buttons = [
                ("input", pygame.Rect(120, 602, 160, 40)),
                ("enqueue", pygame.Rect(340, 602, 150, 40)),
                ("dequeue", pygame.Rect(510, 602, 150, 40)),
                ("clear_queue", pygame.Rect(680, 602, 170, 40)),
            ]
        elif self.tab == KIND_STACK:
            buttons = [
                ("input", pygame.Rect(120, 602, 160, 40)),
                ("push", pygame.Rect(340, 602, 150, 40)),
                ("pop", pygame.Rect(510, 602, 150, 40)),
                ("clear_stack", pygame.Rect(680, 602, 170, 40)),
            ]
        else:
            buttons = [
                ("input_a", pygame.Rect(120, 602, 150, 40)),
                ("input_b", pygame.Rect(300, 602, 150, 40)),
                ("insert_end", pygame.Rect(500, 602, 150, 40)),
                ("remove_first", pygame.Rect(670, 602, 170, 40)),
                ("remove_by_value", pygame.Rect(860, 602, 180, 40)),
                ("clear_list", pygame.Rect(1060, 602, 170, 40)),
            ]

        for name, rect in buttons:
            if rect.collidepoint(pos):
                return name
        return None

    def _button_color(self, x, y, w, h, label):
        hovered = self._rect_contains(x, y, w, h, self.mouse_pos)
        active = self.pressed_button == label
        base = self.blue
        if active:
            return (64, 110, 180)
        if hovered:
            return (118, 185, 255)
        return base

    def _trigger_action_by_current_tab(self):
        if self.tab == KIND_QUEUE:
            self._trigger_queue_enqueue()
        elif self.tab == KIND_STACK:
            self.status_message = "Empilhar"
        else:
            self.status_message = "Lista"

    def _trigger_queue_enqueue(self):
        value = self._parse_int(self.field_value)
        if value is None:
            self.status_message = "Valor inválido"
            return
        if not self.app.is_ready():
            self.status_message = self.app.i18n.text("error_dll")
            return
        result = self.app.handle_insert(KIND_QUEUE, value)
        self.status_message = result if result != "ok" else "Enfileirado"
        if result == "ok":
            self.field_value = ""

    def _trigger_queue_dequeue(self):
        if not self.app.is_ready():
            self.status_message = self.app.i18n.text("error_dll")
            return
        result = self.app.handle_remove_first(KIND_QUEUE)
        self.status_message = result if result != "ok" else "Desenfileirado"

    def _trigger_queue_clear(self):
        if not self.app.is_ready():
            self.status_message = self.app.i18n.text("error_dll")
            return
        result = self.app.handle_clear(KIND_QUEUE)
        self.status_message = result if result != "ok" else "Fila limpa"

    def _parse_int(self, text: str):
        if text in ("", "-"):
            return None
        try:
            value = int(text)
        except ValueError:
            return None
        if value < -2147483648 or value > 2147483647:
            return None
        return value

    def _delete_from_active_field(self):
        if self.active_input == "main":
            self.field_value = self.field_value[:-1]
        elif self.active_input == "list_insert":
            self.field_value_list = self.field_value_list[:-1]
        elif self.active_input == "list_remove":
            self.field_remove_value = self.field_remove_value[:-1]

    def draw(self) -> None:
        self.screen.fill(self.light)
        self._draw_header()
        self._draw_tabs()
        self._draw_body()
        self._draw_footer()
        if self.modal_active:
            self._draw_modal()
        pygame.display.flip()

    def _draw_header(self) -> None:
        header = pygame.Rect(24, 20, self.screen.get_width() - 48, 72)
        pygame.draw.rect(self.screen, self.white, header, border_radius=14)
        title = self.font_title.render(self.i18n.text("title"), True, self.dark)
        self.screen.blit(title, (40, 34))

        lang_label = self.font_small.render(self.i18n.text("language"), True, self.gray)
        self.screen.blit(lang_label, (self.screen.get_width() - 195, 38))

        lang_box = pygame.Rect(self.screen.get_width() - 130, 30, 90, 32)
        pygame.draw.rect(self.screen, self.blue_soft, lang_box, border_radius=8)
        lang_text = self.font_small.render("PT / EN", True, self.blue)
        self.screen.blit(lang_text, (self.screen.get_width() - 108, 38))

        exit_button = pygame.Rect(self.screen.get_width() - 120, 68, 90, 32)
        pygame.draw.rect(self.screen, self.blue, exit_button, border_radius=9)
        exit_text = self.font_small.render(self.i18n.text("exit"), True, self.white)
        self.screen.blit(exit_text, (self.screen.get_width() - 92, 76))

    def _draw_tabs(self) -> None:
        y = 112
        tabs = [
            (KIND_QUEUE, self.i18n.text("queue")),
            (KIND_STACK, self.i18n.text("stack")),
            (KIND_LIST, self.i18n.text("list")),
            (99, self.i18n.text("history")),
        ]
        x = 24
        width = 190
        gap = 12
        for kind, label in tabs:
            rect = pygame.Rect(x, y, width, 44)
            color = self.blue if self.tab == kind else self.white
            border_color = self.blue if self.tab == kind else self.border
            pygame.draw.rect(self.screen, color, rect, border_radius=12)
            pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=12)
            text = self.font.render(label, True, self.white if self.tab == kind else self.dark)
            self.screen.blit(text, (rect.x + 18, rect.y + 12))
            x += width + gap

    def _draw_body(self) -> None:
        body = pygame.Rect(24, 170, self.screen.get_width() - 48, 500)
        pygame.draw.rect(self.screen, self.white, body, border_radius=16)

        title = self._tab_title()
        title_txt = self.font_bold.render(title, True, self.dark)
        self.screen.blit(title_txt, (40, 198))

        info_txt = self.font_small.render(self._tab_explanation(), True, self.gray)
        self.screen.blit(info_txt, (40, 230))

        count_txt = self.font.render(f"{len(self.app.get_tab_values(self.tab))}/10", True, self.dark)
        self.screen.blit(count_txt, (self.screen.get_width() - 120, 198))

        panel = pygame.Rect(40, 270, self.screen.get_width() - 104, 260)
        pygame.draw.rect(self.screen, self.light, panel, border_radius=12)
        pygame.draw.rect(self.screen, self.border, panel, 1, border_radius=12)

        if self.tab == 99:
            self._draw_history_panel(panel)
            return

        self._draw_structure(panel)
        self._draw_controls()

    def _tab_title(self):
        titles = {KIND_QUEUE: "Fila", KIND_STACK: "Pilha", KIND_LIST: "Lista", 99: "Histórico"}
        return titles.get(self.tab, "")

    def _tab_explanation(self):
        explanations = {
            KIND_QUEUE: "FIFO: o primeiro valor entra e sai primeiro.",
            KIND_STACK: "LIFO: o último valor empilhado sai primeiro.",
            KIND_LIST: "A remoção por valor apaga apenas a primeira ocorrência.",
            99: "Eventos da sessão em ordem cronológica.",
        }
        return explanations.get(self.tab, "")

    def _draw_structure(self, panel):
        values = self.app.get_tab_values(self.tab)

        if not values:
            empty = self.font.render(self.i18n.text("empty_state"), True, self.gray)
            self.screen.blit(empty, (panel.x + 18, panel.y + 96))
            return

        card_w = 90
        gap = 12
        x = panel.x + 18
        y = panel.y + 18

        for value in values:
            rect = pygame.Rect(x, y, card_w, 90)
            pygame.draw.rect(self.screen, self.white, rect, border_radius=10)
            pygame.draw.rect(self.screen, self.border, rect, 2, border_radius=10)
            val_txt = self.font_bold.render(str(value), True, self.dark)
            self.screen.blit(val_txt, (rect.x + 28, rect.y + 30))
            x += card_w + gap

        if self.tab == KIND_QUEUE:
            start_lab = self.font_small.render("Início / saída", True, self.gray)
            end_lab = self.font_small.render("Fim / entrada", True, self.gray)
            self.screen.blit(start_lab, (panel.x + 18, panel.y + 120))
            self.screen.blit(end_lab, (x - 90, panel.y + 120))
        elif self.tab == KIND_STACK:
            top_lab = self.font_small.render("Topo / entrada e saída", True, self.gray)
            base_lab = self.font_small.render("Base", True, self.gray)
            self.screen.blit(top_lab, (panel.x + 18, panel.y + 120))
            self.screen.blit(base_lab, (panel.x + 18, panel.y + 145))

    def _draw_controls(self):
        input_y = 620
        label = self.font.render(self.i18n.text("value"), True, self.dark)
        self.screen.blit(label, (40, input_y - 6))

        if self.tab == KIND_QUEUE:
            input_rect = pygame.Rect(120, input_y - 18, 160, 40)
            pygame.draw.rect(self.screen, self.white, input_rect, border_radius=10)
            pygame.draw.rect(self.screen, self.border, input_rect, 2, border_radius=10)
            if self.field_value:
                text = self.font.render(self.field_value, True, self.dark)
                self.screen.blit(text, (input_rect.x + 12, input_rect.y + 10))
            buttons = [
                ("enqueue", 340, 150, 40, "Enfileirar"),
                ("dequeue", 510, 150, 40, "Desenfileirar"),
                ("clear_queue", 680, 170, 40, "Limpar fila"),
            ]
        elif self.tab == KIND_STACK:
            input_rect = pygame.Rect(120, input_y - 18, 160, 40)
            pygame.draw.rect(self.screen, self.white, input_rect, border_radius=10)
            pygame.draw.rect(self.screen, self.border, input_rect, 2, border_radius=10)
            if self.field_value:
                text = self.font.render(self.field_value, True, self.dark)
                self.screen.blit(text, (input_rect.x + 12, input_rect.y + 10))
            buttons = [
                ("push", 340, 150, 40, "Empilhar"),
                ("pop", 510, 150, 40, "Desempilhar"),
                ("clear_stack", 680, 170, 40, "Limpar pilha"),
            ]
        else:
            input_a = pygame.Rect(120, input_y - 18, 150, 40)
            input_b = pygame.Rect(300, input_y - 18, 150, 40)
            for rect, value in [(input_a, self.field_value_list), (input_b, self.field_remove_value)]:
                pygame.draw.rect(self.screen, self.white, rect, border_radius=10)
                pygame.draw.rect(self.screen, self.border, rect, 2, border_radius=10)
                if value:
                    txt = self.font.render(value, True, self.dark)
                    self.screen.blit(txt, (rect.x + 12, rect.y + 10))
            buttons = [
                ("insert_end", 500, 150, 40, "Inserir no final"),
                ("remove_first", 670, 170, 40, "Remover primeiro"),
                ("remove_by_value", 860, 180, 40, "Remover por valor"),
                ("clear_list", 1060, 170, 40, "Limpar lista"),
            ]

        for action, x, w, h, label in buttons:
            rect = pygame.Rect(x, input_y - 18, w, h)
            color = self._button_color(x, input_y - 18, w, h, action)
            if self.pressed_button == action:
                rect.move_ip(0, 2)
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            text = self.font.render(label, True, self.white)
            self.screen.blit(text, (rect.x + 14, rect.y + 10))

    def _draw_history_panel(self, panel):
        entries = self.app.history
        if not entries:
            msg = self.font.render(self.i18n.text("history_empty"), True, self.gray)
            self.screen.blit(msg, (panel.x + 18, panel.y + 80))
            return

        for idx, entry in enumerate(entries[:10]):
            line = f"#{entry.sequence} | kind={entry.kind} | action={entry.action} | value={entry.value} | qty={entry.quantity}"
            txt = self.font_small.render(line, True, self.dark)
            self.screen.blit(txt, (panel.x + 18, panel.y + 16 + idx * 24))

    def _draw_footer(self):
        footer = pygame.Rect(24, 690, self.screen.get_width() - 48, 72)
        pygame.draw.rect(self.screen, self.white, footer, border_radius=14)
        status_label = self.font_small.render("Última ação", True, self.gray)
        self.screen.blit(status_label, (40, 710))
        status_value = self.font_bold.render(self.status_message or "Pronto", True, self.dark)
        self.screen.blit(status_value, (140, 706))

    def _draw_modal(self):
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        box = pygame.Rect(self.screen.get_width() // 2 - 200, self.screen.get_height() // 2 - 85, 400, 170)
        pygame.draw.rect(self.screen, self.white, box, border_radius=16)
        msg = self.font.render("Deseja limpar esta estrutura?", True, self.dark)
        self.screen.blit(msg, (box.x + 26, box.y + 28))

        cancel_rect = pygame.Rect(box.x + 28, box.y + 100, 140, 38)
        confirm_rect = pygame.Rect(box.x + 232, box.y + 100, 140, 38)
        pygame.draw.rect(self.screen, self.gray_soft, cancel_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.blue, confirm_rect, border_radius=8)
        cancel_txt = self.font.render("Cancelar", True, self.dark)
        confirm_txt = self.font.render("Limpar", True, self.white)
        self.screen.blit(cancel_txt, (cancel_rect.x + 38, cancel_rect.y + 10))
        self.screen.blit(confirm_txt, (confirm_rect.x + 46, confirm_rect.y + 10))


def main() -> None:
    from .visual_ui import main as visual_main

    visual_main()


if __name__ == "__main__":
    main()
