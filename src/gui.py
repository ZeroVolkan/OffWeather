import flet as ft


def main(page: ft.Page):
    for _ in range(2):
        t = ft.Text(value="Hello, world!", size=40)
        page.controls.append(t)  # type: ignore[attr-defined]
    page.update()


if __name__ == "__main__":
    ft.app(main)
