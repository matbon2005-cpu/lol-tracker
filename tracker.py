import flet as ft
import asyncio
import threading

SPELLS = {
    "Flash": {"cd": 300, "img": "Flash_HD.webp"},
    "Ghost": {"cd": 240, "img": "Ghost_HD.webp"},
    "Teleport": {"cd": 360, "img": "Teleport_HD.webp"},
    "Smite": {"cd": 90, "img": "Smite_HD.webp"},
    "Barrier": {"cd": 180, "img": "Barrier_HD.webp"},
    "Exhaust": {"cd": 210, "img": "Exhaust_HD.webp"},
    "Ignite": {"cd": 210, "img": "Ignite_HD.webp"},
    "Heal": {"cd": 240, "img": "Heal_HD.webp"},
    "Cleanse": {"cd": 210, "img": "Cleanse_HD.webp"}
}

IONIAN_IMG = "Ionian_HD.webp"
COSMIC_IMG = "CosmicInsight_HD.webp"
UNLEASHED_TP_CD = 420  # 7 minuti fissi

class PlayerRow(ft.Row):
    def __init__(self, role_name, default_spell2, exclude_spells, get_trash_active_func, reset_trash_func, record_action_func):
        super().__init__(alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        self.role_name = role_name
        self.locked = False
        self.get_trash_active = get_trash_active_func
        self.reset_trash = reset_trash_func
        self.record_action = record_action_func
        
        self.role_label = ft.Text(role_name, width=40, weight=ft.FontWeight.BOLD, size=15)
        
        self.ionian_active = False
        self.cosmic_active = False
        
        self.spell1_running = False
        self.spell1_token = 0
        self.spell1_left = 0
        
        self.spell2_running = False
        self.spell2_token = 0
        self.spell2_left = 0
        
        self.unleashed_tp_running = False
        self.tp_token = 0
        self.tp_left = 0
        
        self.ionian_btn = ft.Container(
            content=ft.Image(src=IONIAN_IMG, width=35, height=35),
            opacity=0.3,
            on_click=self.toggle_ionian
        )
        self.cosmic_btn = ft.Container(
            content=ft.Image(src=COSMIC_IMG, width=35, height=35),
            opacity=0.3,
            on_click=self.toggle_cosmic
        )
        
        if role_name == "TOP":
            self.unleashed_tp_text = ft.Text("", size=11, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
            self.unleashed_tp_img = ft.Image(src=SPELLS["Teleport"]["img"], width=35, height=35)
            self.unleashed_tp_img_container = ft.Container(content=self.unleashed_tp_img, opacity=1.0)
            
            self.unleashed_tp_container = ft.Container(
                content=ft.Stack([
                    self.unleashed_tp_img_container,
                    ft.Container(content=self.unleashed_tp_text, alignment=ft.alignment.center)
                ]),
                width=35,
                height=35,
                border=ft.border.all(2, ft.colors.GREEN),
                border_radius=4,
                on_click=self.handle_unleashed_tp_click
            )
            group_unleashed_tp = self.unleashed_tp_container
        else:
            group_unleashed_tp = ft.Container(width=35, height=35)
        
        self.current_spell1 = "Flash"
        self.spell1_img = ft.Image(src=SPELLS["Flash"]["img"], width=35, height=35)
        self.spell1_container = ft.Container(content=self.spell1_img, opacity=1.0)
        self.spell1_menu = ft.PopupMenuButton(
            content=self.spell1_container,
            items=[
                ft.PopupMenuItem(text="Flash", on_click=lambda e: self.change_spell1("Flash")),
                ft.PopupMenuItem(text="Ghost", on_click=lambda e: self.change_spell1("Ghost"))
            ]
        )
        self.spell1_timer_btn = ft.ElevatedButton(
            "USA", 
            on_click=self.handle_spell1_click, 
            width=80, 
            height=35,
            style=ft.ButtonStyle(
                color=ft.colors.GREEN,
                bgcolor=ft.colors.BLACK45,
                padding=ft.padding.all(0)
            )
        )
        
        self.current_spell2 = default_spell2
        self.spell2_img = ft.Image(src=SPELLS[default_spell2]["img"], width=35, height=35)
        self.spell2_container = ft.Container(content=self.spell2_img, opacity=1.0)
        
        if role_name == "JGL":
            self.spell2_control = self.spell2_container
        else:
            items = []
            for spell_name in SPELLS.keys():
                if spell_name != "Flash" and spell_name not in exclude_spells:
                    items.append(ft.PopupMenuItem(text=spell_name, on_click=self.make_change_spell2_callback(spell_name)))
            
            self.spell2_control = ft.PopupMenuButton(content=self.spell2_container, items=items)
            
        self.spell2_timer_btn = ft.ElevatedButton(
            "USA", 
            on_click=self.handle_spell2_click, 
            width=80, 
            height=35,
            style=ft.ButtonStyle(
                color=ft.colors.GREEN,
                bgcolor=ft.colors.BLACK45,
                padding=ft.padding.all(0)
            )
        )
        
        group_spell1 = ft.Row([self.spell1_menu, self.spell1_timer_btn], spacing=5)
        group_spell2 = ft.Row([self.spell2_control, self.spell2_timer_btn], spacing=5)
        
        self.controls = [
            self.role_label, 
            self.ionian_btn, 
            self.cosmic_btn,
            group_unleashed_tp,
            group_spell1,
            group_spell2
        ]

    def set_lock(self, locked_state):
        self.locked = locked_state
        self.spell1_menu.disabled = locked_state
        if self.role_name != "JGL":
            self.spell2_control.disabled = locked_state
        self.update()

    def get_color_gradient(self, current_time, max_time):
        percent = current_time / max_time
        red = 255
        green = int((1 - percent) * 255)
        return f"#{red:02x}{green:02x}00"

    def make_change_spell2_callback(self, spell_name):
        return lambda e: self.change_spell2(spell_name)

    def change_spell1(self, spell_name):
        if self.locked: return
        self.current_spell1 = spell_name
        self.spell1_img.src = SPELLS[spell_name]["img"]
        self.update()

    def change_spell2(self, spell_name):
        if self.locked: return
        self.current_spell2 = spell_name
        self.spell2_img.src = SPELLS[spell_name]["img"]
        self.update()

    def toggle_ionian(self, e):
        self.ionian_active = not self.ionian_active
        self.ionian_btn.opacity = 1.0 if self.ionian_active else 0.3
        self.update()

    def toggle_cosmic(self, e):
        if self.locked: return
        self.cosmic_active = not self.cosmic_active
        self.cosmic_btn.opacity = 1.0 if self.cosmic_active else 0.3
        self.update()

    def get_actual_cooldown(self, base_cd):
        haste = 0
        if self.ionian_active: haste += 15
        if self.cosmic_active: haste += 18
        return int(base_cd * (100 / (100 + haste)))

    def get_remaining_time(self, spell_slot):
        if spell_slot == "spell1": return self.spell1_left
        elif spell_slot == "spell2": return self.spell2_left
        elif spell_slot == "tp": return self.tp_left
        return 0

    def cancel_spell(self, spell_slot):
        if spell_slot == "spell1":
            self.spell1_token += 1
            self.spell1_running = False
            self.spell1_container.opacity = 1.0
            self.spell1_timer_btn.text = "USA"
            self.spell1_timer_btn.style = ft.ButtonStyle(
                color=ft.colors.GREEN,
                bgcolor=ft.colors.BLACK45,
                padding=ft.padding.all(0)
            )
        elif spell_slot == "spell2":
            self.spell2_token += 1
            self.spell2_running = False
            self.spell2_container.opacity = 1.0
            self.spell2_timer_btn.text = "USA"
            self.spell2_timer_btn.style = ft.ButtonStyle(
                color=ft.colors.GREEN,
                bgcolor=ft.colors.BLACK45,
                padding=ft.padding.all(0)
            )
        elif spell_slot == "tp":
            self.tp_token += 1
            self.unleashed_tp_running = False
            self.unleashed_tp_text.value = ""
            self.unleashed_tp_img_container.opacity = 1.0
            self.unleashed_tp_container.border = ft.border.all(2, ft.colors.GREEN)
        self.update()

    async def resume_spell(self, spell_slot, rem_time):
        if spell_slot == "spell1":
            await self.start_spell1_internal(start_from=rem_time)
        elif spell_slot == "spell2":
            await self.start_spell2_internal(start_from=rem_time)
        elif spell_slot == "tp":
            await self.start_unleashed_tp_internal(start_from=rem_time)

    async def handle_unleashed_tp_click(self, e):
        if self.get_trash_active():
            if self.unleashed_tp_running:
                self.cancel_spell("tp")
                self.reset_trash()
            return

        if self.unleashed_tp_running: return
        self.record_action(self, "tp")
        await self.start_unleashed_tp_internal()

    async def start_unleashed_tp_internal(self, start_from=None):
        if self.unleashed_tp_running: return
        self.unleashed_tp_running = True
        self.tp_token += 1
        current_token = self.tp_token
        
        self.unleashed_tp_img_container.opacity = 0.4
        actual_cd = UNLEASHED_TP_CD
        start_val = start_from if start_from is not None else actual_cd
        
        for i in range(start_val, 0, -1):
            if current_token != self.tp_token: return
            self.tp_left = i
            color_hex = self.get_color_gradient(i, actual_cd)
            self.unleashed_tp_text.value = f"{i}s"
            self.unleashed_tp_container.border = ft.border.all(2, color_hex)
            self.update()
            await asyncio.sleep(1)
            
        if current_token != self.tp_token: return
        self.cancel_spell("tp")

    async def handle_spell1_click(self, e):
        if self.get_trash_active():
            if self.spell1_running:
                self.cancel_spell("spell1")
                self.reset_trash()
            return

        if self.spell1_running: return
        self.record_action(self, "spell1")
        await self.start_spell1_internal()

    async def start_spell1_internal(self, start_from=None):
        if self.spell1_running: return 
        self.spell1_running = True
        self.spell1_token += 1
        current_token = self.spell1_token
        
        self.spell1_container.opacity = 0.4
        base_cd = SPELLS[self.current_spell1]["cd"]
        actual_cd = self.get_actual_cooldown(base_cd)
        start_val = start_from if start_from is not None else actual_cd
        
        for i in range(start_val, 0, -1):
            if current_token != self.spell1_token: return
            self.spell1_left = i
            self.spell1_timer_btn.text = f"{i}s"
            self.spell1_timer_btn.style = ft.ButtonStyle(
                color=self.get_color_gradient(i, actual_cd),
                bgcolor=ft.colors.BLACK45,
                padding=ft.padding.all(0)
            )
            self.update()
            await asyncio.sleep(1)
            
        if current_token != self.spell1_token: return
        self.cancel_spell("spell1")

    async def handle_spell2_click(self, e):
        if self.get_trash_active():
            if self.spell2_running:
                self.cancel_spell("spell2")
                self.reset_trash()
            return

        if self.spell2_running: return
        self.record_action(self, "spell2")
        await self.start_spell2_internal()

    async def start_spell2_internal(self, start_from=None):
        if self.spell2_running: return
        self.spell2_running = True
        self.spell2_token += 1
        current_token = self.spell2_token
        
        self.spell2_container.opacity = 0.4
        base_cd = SPELLS[self.current_spell2]["cd"]
        actual_cd = self.get_actual_cooldown(base_cd)
        start_val = start_from if start_from is not None else actual_cd
        
        for i in range(start_val, 0, -1):
            if current_token != self.spell2_token: return
            self.spell2_left = i
            self.spell2_timer_btn.text = f"{i}s"
            self.spell2_timer_btn.style = ft.ButtonStyle(
                color=self.get_color_gradient(i, actual_cd),
                bgcolor=ft.colors.BLACK45,
                padding=ft.padding.all(0)
            )
            self.update()
            await asyncio.sleep(1)
            
        if current_token != self.spell2_token: return
        self.cancel_spell("spell2")

def main(page: ft.Page):
    try:
        page.title = "LoL Spell Tracker"
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 5
        page.spacing = 5 
        # NOTA: Rimossi window_width e window_height per evitare crash su Android
        
        player_rows = []
        app_locked = False
        trash_active = False
        trash_timer = None
        
        undo_stack = []
        redo_stack = []

        def update_undo_redo_buttons():
            undo_btn.opacity = 1.0 if undo_stack else 0.3
            redo_btn.opacity = 1.0 if redo_stack else 0.3
            page.update()

        def record_action(row, spell_slot):
            undo_stack.append((row, spell_slot))
            redo_stack.clear()
            update_undo_redo_buttons()

        async def handle_undo(e):
            if not undo_stack: return
            row, spell_slot = undo_stack.pop()
            rem_time = row.get_remaining_time(spell_slot)
            row.cancel_spell(spell_slot)
            redo_stack.append((row, spell_slot, rem_time))
            update_undo_redo_buttons()

        async def handle_redo(e):
            if not redo_stack: return
            row, spell_slot, rem_time = redo_stack.pop()
            undo_stack.append((row, spell_slot))
            update_undo_redo_buttons()
            await row.resume_spell(spell_slot, rem_time)

        def get_trash_status():
            return trash_active

        def deactivate_trash():
            nonlocal trash_active, trash_timer
            trash_active = False
            trash_btn.icon_color = ft.colors.WHITE
            main_container.border = ft.border.all(2, ft.colors.TRANSPARENT)
            if trash_timer:
                trash_timer.cancel()
                trash_timer = None
            page.update()

        main_container = ft.Container(
            border=ft.border.all(2, ft.colors.TRANSPARENT),
            border_radius=8,
            padding=5
        )

        def toggle_lock(e):
            nonlocal app_locked
            app_locked = not app_locked
            lock_btn.icon = ft.icons.LOCK if app_locked else ft.icons.LOCK_OPEN
            lock_btn.icon_color = ft.colors.RED if app_locked else ft.colors.GREEN
            for row in player_rows:
                row.set_lock(app_locked)
            page.update()

        def toggle_trash(e):
            nonlocal trash_active, trash_timer
            trash_active = not trash_active
            trash_btn.icon_color = ft.colors.RED if trash_active else ft.colors.WHITE
            main_container.border = ft.border.all(3, ft.colors.RED if trash_active else ft.colors.TRANSPARENT)
            
            if trash_timer:
                trash_timer.cancel()
                trash_timer = None
                
            if trash_active:
                trash_timer = threading.Timer(10.0, deactivate_trash)
                trash_timer.start()
                
            page.update()

        lock_btn = ft.IconButton(
            icon=ft.icons.LOCK_OPEN,
            icon_color=ft.colors.GREEN,
            icon_size=22,
            on_click=toggle_lock,
            tooltip="Blocca/Sblocca configurazione"
        )

        trash_btn = ft.IconButton(
            icon=ft.icons.DELETE,
            icon_color=ft.colors.WHITE,
            icon_size=22,
            on_click=toggle_trash,
            tooltip="Attiva/Disattiva modalità Reset (Annulla errore click)"
        )

        undo_btn = ft.IconButton(
            icon=ft.icons.UNDO,
            icon_color=ft.colors.WHITE,
            icon_size=22,
            on_click=handle_undo,
            tooltip="Annulla ultima azione (Undo)"
        )
        undo_btn.opacity = 0.3

        redo_btn = ft.IconButton(
            icon=ft.icons.REDO,
            icon_color=ft.colors.WHITE,
            icon_size=22,
            on_click=handle_redo,
            tooltip="Ripristina azione annullata (Redo)"
        )
        redo_btn.opacity = 0.3

        header = ft.Row(
            [
                ft.Row([undo_btn, redo_btn], spacing=2),
                trash_btn,
                lock_btn
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        content_column = ft.Column([
            header,
            ft.Divider(height=1, color=ft.colors.WHITE24)
        ], spacing=5)

        roles_setup = [
            {"role": "TOP", "default_spell": "Teleport", "exclude": ["Smite", "Heal"]},
            {"role": "JGL", "default_spell": "Smite", "exclude": []},
            {"role": "MID", "default_spell": "Teleport", "exclude": ["Smite", "Heal"]},
            {"role": "ADC", "default_spell": "Barrier", "exclude": ["Smite"]},
            {"role": "SUP", "default_spell": "Exhaust", "exclude": ["Smite"]}
        ]
        
        for setup in roles_setup:
            row = PlayerRow(setup["role"], setup["default_spell"], setup["exclude"], get_trash_status, deactivate_trash, record_action)
            player_rows.append(row)
            content_column.controls.append(row)

        main_container.content = content_column
        page.add(main_container)
        
    except Exception as ex:
        # Se qualcosa non va, mostra l'errore sullo schermo invece di crashare in silenzio
        page.add(ft.Text(f"ERRORE CRITICO: {ex}", color=ft.colors.RED, size=18))
        page.update()

ft.app(target=main)
