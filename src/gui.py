import select
import flet as ft
import subprocess, sys
import threading, queue
import time
from pathlib import Path


class Console:
    CLI_FILENAME = "src.cli"

    def __init__(self, page: ft.Page, out):
        self.page = page

        self._process = subprocess.Popen(
            [sys.executable, "-u", "-m", self.CLI_FILENAME],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        self._is_running = True
        self._out = out
        self._queue = queue.Queue()

        self.in_thread = threading.Thread(target=self._loop_input)
        self.in_thread.start()

    def input(self, text: str):
        self._queue.put(text + "\n", timeout=0.5)

    def output(self, text: str):
        self._out.controls.append(ft.Text(text, height=20))

    def terminate(self, text):
        self._process.terminate()
        self._out.value = text
        self._is_running = False
        self.page.update()

    def _loop_input(self):
        while self._is_running:
            if (code := self._process.poll()) is not None:
                self._out.value = "Subprocess exited with code {}".format(code)
                self._is_running = False
                self.page.update()
            try:
                line = self._queue.get_nowait()
                self._process.stdin.write(line)
                self._process.stdin.flush()
            except queue.Empty:
                pass
            except Exception as e:
                self.terminate("Subprocess terminated due to error: {}".format(str(e)))

            try:
                rlist, _, _ = select.select([self._process.stdout], [], [], 0.2)
                if self._process.stdout in rlist:
                    line = self._process.stdout.readline()
                    if line:
                        self.output(line)
            except Exception as e:
                self.terminate("Subprocess terminated due to error: {}".format(str(e)))

            self.page.update()

def main(page: ft.Page):
    def send_command(e):
        try:
            console.input(enter_field.value)
            enter_field.value = ""
            enter_field.focus()
            page.update()
        except Exception as e:
            out_field.controls.append(ft.Text(line))
            page.update()

    page.title = "Console CLI"
    page.window_width = 1000
    page.window_height = 640

    out_field = ft.ListView(
        expand=True,
            spacing=0,
            padding=0,
            auto_scroll=True,
            height=400,
    )

    enter_field = ft.TextField(label="Command", expand=True, on_submit=send_command, autofocus=True)
    send_button = ft.ElevatedButton("Send", on_click=send_command)

    # Контейнер терминала
    console_container = ft.Column(
        [
            ft.Text("Console", size=16),
            out_field,
            ft.Row([enter_field, send_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ],
        expand=True,
    )

    page.add(console_container)

    try:
        console = Console(page, out_field)
    except Exception as e:
        out_field.value = f"Error run console: {e}"
        page.update()
        return

ft.app(target=main)
