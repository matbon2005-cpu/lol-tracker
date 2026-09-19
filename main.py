import flet as ft

def main(page: ft.Page):
    page.title = "Test"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    page.add(
        ft.Text("L'APP FUNZIONA!", color=ft.colors.GREEN, size=30, weight=ft.FontWeight.BOLD),
        ft.Text("Il problema erano le immagini WebP.", color=ft.colors.WHITE, size=16)
    )

ft.app(target=main)
