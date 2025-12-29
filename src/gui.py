import flet as ft
import sys
from io import StringIO

from src.cli import debug_shell


def main(page: ft.Page):
    page.title = "Debug Shell"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    # Output display
    output_field = ft.TextField(
        multiline=True,
        read_only=True,
        min_lines=20,
        max_lines=20,
        expand=True,
        visible=False,
    )

    # Command input
    command_input = ft.TextField(
        label="Command",
        hint_text="Enter command (api list, status, help, etc.)",
        expand=True,
        visible=False,
    )

    # Buttons
    send_btn = ft.ElevatedButton("Send", visible=False)
    clear_btn = ft.ElevatedButton("Clear", visible=False)
    close_cli_btn = ft.ElevatedButton("Close CLI", visible=False, bgcolor="red")
    open_cli_btn = ft.ElevatedButton(
        "Open CLI",
        bgcolor="green",
        height=60,
    )

    def append_output(text):
        output_field.value += text + "\n"
        output_field.update()

    def open_cli(e):
        # Show CLI interface
        output_field.visible = True
        command_input.visible = True
        send_btn.visible = True
        clear_btn.visible = True
        close_cli_btn.visible = True
        open_cli_btn.visible = False

        page.update()

        # Show intro
        output_field.value = debug_shell.intro + "\n\n"
        output_field.update()

        command_input.focus()

    def close_cli(e):
        # Hide CLI interface
        output_field.visible = False
        command_input.visible = False
        send_btn.visible = False
        clear_btn.visible = False
        close_cli_btn.visible = False
        open_cli_btn.visible = True

        page.update()

    def execute_command(e):
        command = command_input.value.strip()
        if not command:
            return

        # Show command
        append_output(f"(debug) {command}")
        command_input.value = ""
        command_input.update()

        # Execute command
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        try:
            # Execute command directly
            debug_shell.onecmd(command)

            # Get output
            stdout_output = sys.stdout.getvalue()
            stderr_output = sys.stderr.getvalue()

            if stdout_output:
                append_output(stdout_output.rstrip())
            if stderr_output:
                append_output(stderr_output.rstrip())

            # If no output at all
            if not stdout_output and not stderr_output:
                append_output("(command executed)")

        except Exception as ex:
            append_output(f"Error: {ex}")
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    def clear_output(e):
        output_field.value = ""
        output_field.update()

    # Set button handlers
    open_cli_btn.on_click = open_cli
    close_cli_btn.on_click = close_cli
    send_btn.on_click = execute_command
    clear_btn.on_click = clear_output
    command_input.on_submit = execute_command

    # Layout
    page.add(
        ft.Column(
            [
                ft.Text("Debug Shell", size=24, weight=ft.FontWeight.BOLD),
                # Open CLI button (shown initially)
                ft.Container(
                    content=open_cli_btn,
                    alignment=ft.alignment.center,
                    padding=50,
                ),
                # Output (hidden initially)
                output_field,
                # Input (hidden initially)
                ft.Row(
                    [
                        command_input,
                        send_btn,
                        clear_btn,
                        close_cli_btn,
                    ]
                ),
            ],
            expand=True,
        )
    )


ft.app(target=main)
