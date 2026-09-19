import flet as ft
import asyncio
import threading

def main(page: ft.Page):
    page.title = "LoL Spell Tracker Test"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 10
    
    # Test visivo per capire se l'app si avvia correttamente
    page.add(
        ft.Column([
            ft.Text("TEST AVVIATO CON SUCCESSO!", color=ft.colors.GREEN, size=20, weight=ft.FontWeight.BOLD),
            ft.Text("Se vedi questa schermata, l'APK funziona e il problema erano le immagini.", color=ft.colors.WHITE, size=14),
            ft.ElevatedButton("Cliccami", on_click=lambda e: print("Click ok!"))
        ])
    )

ft.app(target=main)
