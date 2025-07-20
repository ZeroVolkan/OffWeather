import flet as ft


def main(page: ft.Page):
    t = ft.Text(value="Hello, world!", size=40)
    page.controls.append(t)  # type: ignore[attr-defined]
    t2 = ft.Text(value="Hello, world!", size=40)
    page.controls.append(t2) # type: ignore[attr-defined]
    page.update()

if __name__ == "__main__":
    ft.app(main)
