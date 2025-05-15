import flet as ft
import subprocess
import sys
python_exe = sys.executable  # gets current Python interpreter path


# Global reference to the running process
current_process = None
unity_process = None


def main(page: ft.Page):
    global current_process

    page.title = "RL Controller"
    page.vertical_alignment = ft.MainAxisAlignment.START

    script_dropdown = ft.Dropdown(
        label="Choose Script",
        options=[
            ft.dropdown.Option("train_rl.py"),
            ft.dropdown.Option("test_rl.py"),
            ft.dropdown.Option("retrain.py"),
        ],
        value="train_rl.py",
    )

    unity_path_input = ft.TextField(
        label="Unity Game Path (.exe)",
        value="C:\\Users\\manso\\Autonomous Car\\New2\\Autonomous Car.exe",
        expand=True
    )

    model_input = ft.TextField(label="Model Name", value="Test_Model")
    port_input = ft.TextField(label="Port", value="9000")
    steps_input = ft.TextField(label="Episodes/Timesteps", value="100000")
    output_display = ft.TextField(value="", multiline=True, read_only=True, min_lines=10, max_lines=30)

    import sys
    import threading

    python_exe = sys.executable

    def run_script(e):
        global current_process
        output_display.value = "🚀 Running...\n"
        page.update()

        cmd = [
            python_exe,
            script_dropdown.value,
            "--port", port_input.value,
            "--model", model_input.value,
        ]

        if script_dropdown.value == "test_rl.py":
            cmd += ["--episodes", steps_input.value]

        try:
            current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            # Background thread to read output
            def read_output():
                for line in current_process.stdout:
                    output_display.value += line
                    page.update()
                current_process.wait()
                output_display.value += f"\n✅ Script finished with code {current_process.returncode}"
                page.update()

            threading.Thread(target=read_output, daemon=True).start()

        except Exception as ex:
            output_display.value = f"❌ Error: {str(ex)}"
            page.update()

    def terminate_script(e):
        global current_process
        if current_process and current_process.poll() is None:
            current_process.terminate()
            output_display.value = f"⛔ Terminated script (PID {current_process.pid})"
            current_process = None
        else:
            output_display.value = "⚠️ No active script to terminate."


    def launch_game(e):
        global unity_process
        try:
            exe_path = unity_path_input.value.strip()
            if not exe_path.endswith(".exe"):
                output_display.value += "\n❌ Invalid Unity EXE path"
                page.update()
                return

            if unity_process and unity_process.poll() is None:
                output_display.value += "\n⚠️ Game already running."
            else:
                unity_process = subprocess.Popen([exe_path])
                output_display.value += f"\n🎮 Game launched (PID {unity_process.pid})"
        except Exception as ex:
            output_display.value += f"\n❌ Failed to launch game: {ex}"
        page.update()

    def close_game(e):
        global unity_process
        try:
            if unity_process and unity_process.poll() is None:
                unity_process.terminate()
                unity_process.wait()
                output_display.value += f"\n❌ Game closed (PID {unity_process.pid})"
                unity_process = None
            else:
                output_display.value += "\n⚠️ No running game to close."
        except Exception as ex:
            output_display.value += f"\n❌ Failed to close game: {ex}"
        page.update()

    def clear_log(e):
         output_display.value = "✅ Log Cleared\n"
         page.update()

    run_button = ft.ElevatedButton("Run", on_click=run_script)
    stop_button = ft.OutlinedButton("Terminate", on_click=terminate_script)
    launch_game_btn = ft.ElevatedButton("🎮 Launch Game", on_click=launch_game)
    close_game_btn = ft.OutlinedButton("❌ Close Game", on_click=close_game)
    clear_log_btn = ft.OutlinedButton("Clear Logs", on_click=clear_log)


    page.add(
        unity_path_input,
        ft.Row([launch_game_btn, close_game_btn]),
        script_dropdown,
        model_input,
        port_input,
        steps_input,
        ft.Row([run_button, stop_button, clear_log_btn]),

        output_display
    )




ft.app(target=main)
