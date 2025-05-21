import flet as ft
import subprocess
import threading
import asyncio
import json
import os
import sys

current_process = None
unity_process = None
python_exe = sys.executable

async def main(page: ft.Page):
    global current_process, unity_process

    page.title = "RL Controller"
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.DARK

    log_buffer = []

    def display_info  (e):
        if script_dropdown.value == "train_rl.py":
            output_display_info.value = "⚠️ Use this script, if you want to train your model from scratch"
        if script_dropdown.value == "test_rl.py":
            output_display_info.value = "⚠️ Use this script, if you want to test your trained model"
        if script_dropdown.value == "retrain.py":
            output_display_info.value = "⚠️ Use this script, if you want to retrain your model further"
        if script_dropdown.value == "autorun.py":
            output_display_info.value = "⚠️ Use This script if you want to train or retrain your model with multiple instances"
        page.update()

    # Inputs
    script_dropdown = ft.Dropdown(
        label="Choose Script",
        options=[
            ft.dropdown.Option("train_rl.py"),
            ft.dropdown.Option("test_rl.py"),
            ft.dropdown.Option("retrain.py"),
            ft.dropdown.Option("autorun.py"),
        ],
        value="train_rl.py",
        on_change=display_info
    )
    model_input = ft.TextField(label="Model Name", value="PPO_Test_Model_1")
    port_input = ft.TextField(label="Port", value="9000")
    steps_input = ft.TextField(label="Episodes/Timesteps", value="100000")
    unity_path_input = ft.TextField(label="Unity Game Path (.exe)", value="./GameFiles/Autonomous Dog Agent.exe", expand=True)
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    
    browse_button = ft.ElevatedButton(
        "📁 Browse",
        on_click=lambda e: file_picker.pick_files(allow_multiple=False),
    )
    
    def on_file_selected(e: ft.FilePickerResultEvent):
        if e.files:
            unity_path_input.value = e.files[0].path
            page.update()
            
    file_picker.on_result = on_file_selected

    # Scan model files (zip only)
    def get_model_files():
        model_dir = "./models"
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        return [
            f for f in os.listdir(model_dir)
            if f.endswith(".zip")
        ]
    page.update()

    def refresh_model_dropdown(e):
        model_files_dropdown.options = [ft.dropdown.Option(f) for f in get_model_files()]
        page.update()

    model_files_dropdown = ft.Dropdown(
        label="Select Existing Model (.zip)",
        width=200,
        options=[ft.dropdown.Option(f) for f in get_model_files()],
        on_change=lambda e: setattr(model_input, 'value', e.control.value.replace(".zip", ""))
    )
    refresh_button = ft.TextButton(
        text="🔁 Refresh",
        tooltip="Refresh Model List",
        on_click=refresh_model_dropdown  # ✅ call the refresh function
    )

    output_display_info = ft.TextField(
        label="Script Information",
        value="",
        multiline=True,
        read_only=True,
        min_lines=1,
        max_lines=5,
        expand=True
    )

    # Log Output
    output_display_logs = ft.TextField(
        label="Logs",
        value="",
        multiline=True,
        read_only=True,
        min_lines=5,
        max_lines=20,
        expand=True
    )

    # Live Observation Display
    obs_labels = {
        "reward": ft.Text(),
        "myPosition": ft.Text(),
        "targetPos": ft.Text(),
        "hurdleBools": ft.Text(),
        "waterBools": ft.Text()
    }

    def format_vec3(label, vec):
        return f"{label} → x={vec[0]}, y={vec[1]}, z={vec[2]}"

    def format_bools(label, arr):
        ticks = ["✅" if x else "❌" for x in arr]
        directions = ["North", "South", "West", "East"]
        return f"{label}: " + ", ".join(f"{d}: {t}" for d, t in zip(directions, ticks))

    async def poll_obs_loop():

        while True:

            await asyncio.sleep(1)
            try:
                if not os.path.exists("latest_obs.json"):
                    return

                with open("latest_obs.json", "r") as f:
                    content = f.read().strip()
                    if not content:
                        return
                    data = json.loads(content)

                obs = data.get("observation", {})
                reward = data.get("reward", 0)

                my_pos = obs.get("myPosition", [0, 0, 0])
                target_pos = obs.get("targetPos", [0, 0, 0])
                hurdle_bools = obs.get("hurdleBools", [0, 0, 0, 0])
                water_bools = obs.get("waterBools", [0, 0, 0, 0])

                obs_labels["reward"].value = f"🎯 Reward: {reward:.2f}" if isinstance(reward, (
                int, float)) else f"🎯 Reward: {reward}"
                obs_labels["myPosition"].value = format_vec3("My Position", my_pos)
                obs_labels["targetPos"].value = format_vec3("Target Position", target_pos)
                obs_labels["hurdleBools"].value = format_bools("Hurdles", hurdle_bools)
                obs_labels["waterBools"].value = format_bools("Water", water_bools)

                page.update()
            except:
                output_display_logs.value += "I was here3 \n"
                page.update()
                return


    def run_script(e):
        global current_process

        if current_process is not None and current_process.poll() is None:
            output_display_logs.value += "❌ Another script is in process already"
            page.update()
            return

        output_display_logs.value += "🚀 Running script...\n"
        page.update()

        cmd = [
            python_exe,
            script_dropdown.value,
            "--model", model_input.value,
        ]
        if script_dropdown.value == "train_rl.py" or script_dropdown.value == "test_rl.py" or script_dropdown.value == "retrain.py" :
            cmd += ["--episodes", steps_input.value,
                    "--port", port_input.value,
                    ]
        if script_dropdown.value == "autorun.py":
            cmd += ["--buildPath", unity_path_input.value,
                    "--episodes", steps_input.value]

        try:
            current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            def read_output():
                global current_process
                for line in current_process.stdout:
                    output_display_logs.value += line
                    output_display_logs.cursor_position = len(output_display_logs.value)
                    page.update()
                current_process.wait()
                output_display_logs.value += f"\n✅ Script finished with code {current_process.returncode}\n"
                current_process = None  # ✅ allow re-running after finish
                page.update()

            threading.Thread(target=read_output, daemon=True).start()

        except Exception as ex:
            output_display_logs.value += f"❌ Error: {str(ex)}\n"
            page.update()

    def terminate_script(e):
        global current_process
        if current_process and current_process.poll() is None:
            current_process.terminate()
            output_display_logs.value += f"\n⛔ Terminated script (PID {current_process.pid})\n"
            current_process = None
        else:
            output_display_logs.value += "\n⚠️ No active script to terminate.\n"
        page.update()



    def clear_logs(e):
        output_display_logs.value = ""
        page.update()

    def launch_game(e):
        global unity_process
        try:
            exe_path = unity_path_input.value.strip()
            if not exe_path.endswith(".exe"):
                output_display_logs.value += "\n❌ Invalid Unity EXE path\n"
                return

            if unity_process and unity_process.poll() is None:
                output_display_logs.value += "\n⚠️ Game already running.\n"
            else:
                unity_process = subprocess.Popen([exe_path])
                output_display_logs.value += f"\n🎮 Game launched (PID {unity_process.pid})\n"
        except Exception as ex:
            output_display_logs.value += f"\n❌ Failed to launch game: {ex}\n"
        page.update()

    def close_game(e):
        global unity_process
        try:
            if unity_process and unity_process.poll() is None:
                unity_process.terminate()
                unity_process.wait()
                output_display_logs.value += f"\n❌ Game closed (PID {unity_process.pid})\n"
                unity_process = None
            else:
                output_display_logs.value += "\n⚠️ No running game to close.\n"
        except Exception as ex:
            output_display_logs.value += f"\n❌ Failed to close game: {ex}\n"
        page.update()

    run_button = ft.ElevatedButton("▶ Run", on_click=run_script)
    stop_button = ft.OutlinedButton("⛔ Terminate", on_click=terminate_script)
    clear_logs_btn = ft.OutlinedButton("🧹 Clear Logs", on_click=clear_logs)
    launch_game_btn = ft.ElevatedButton("🎮 Launch Game", on_click=launch_game)
    close_game_btn = ft.OutlinedButton("❌ Close Game", on_click=close_game)

    # LEFT: All controls & logs
    left_column = ft.Column([
        ft.Text("🧠 RL Control Center", theme_style="headlineMedium"),
        script_dropdown,
        ft.Row([model_files_dropdown, refresh_button]),
        model_input,
        port_input,
        steps_input,
        ft.Row([run_button, stop_button, clear_logs_btn]),
        ft.Row([unity_path_input, browse_button]),
        ft.Row([launch_game_btn, close_game_btn]),
        output_display_info

    ], expand=True)

    # RIGHT: Observations only
    right_column = ft.Column([
        ft.Text("👀 Live Observation", theme_style="headlineMedium"),
        obs_labels["reward"],
        obs_labels["myPosition"],
        obs_labels["targetPos"],
        obs_labels["hurdleBools"],
        obs_labels["waterBools"],
        ft.Text("📋 Logs", theme_style="titleMedium"),
        output_display_logs
    ], expand=True)

    # Final layout with split view
    layout = ft.Row([
        left_column,
        right_column
    ])

    page.add(ft.Container(content=layout, padding=20, expand=True))

    # ✅ Start live observation loop
    asyncio.create_task(poll_obs_loop())

ft.app(target=main)
