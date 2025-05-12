import itertools
import os
import time
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.monitor import Monitor
from my_env import MyEnv
from peaceful_pie.unity_comms import UnityComms

def make_env(port):
    def _init():
        unity_comms = UnityComms(port=port)
        env = MyEnv(unity_comms=unity_comms)
        env = Monitor(env)
        return env
    return _init

def run_single_train(config, ports, unity_exe_path, run_id):
    print(f"🚀 Running config {config} (Run ID: {run_id})")

    # Launch Unity instances
    unity_processes = []
    for port in ports:
        proc = subprocess.Popen([
            unity_exe_path,
            "--port", str(port)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        unity_processes.append(proc)

    time.sleep(5)  # Let Unity stabilize

    env_fns = [make_env(port) for port in ports]
    env = SubprocVecEnv(env_fns)

    model = PPO(
        "MultiInputPolicy",
        env=env,
        verbose=1,
        tensorboard_log=f"./tune_logs2/{run_id}",
        learning_rate=config['learning_rate'],
        n_steps=config['n_steps'],
        batch_size=config['batch_size'],
        gamma=config['gamma'],
        clip_range=config['clip_range'],
        ent_coef=config['ent_coef'],
    )

    model.learn(total_timesteps=100000)

    model.save(f"tune_models2/PPO_run_{run_id}")

    env.close()
    for proc in unity_processes:
        proc.terminate()
        proc.wait()

def main():
    # === Config ===
    build_path = "C:\\Users\\manso\\Autonomous Car\\New2\\Autonomous Car.exe"
    ports = [17000, 17010, 17020]  # Must match how many Unity builds you can launch

    # Define hyperparameter grid
    param_grid = {
        'learning_rate': [3e-4, 1e-4],
        'n_steps': [2048, 4096],
        'batch_size': [256, 512],
        'gamma': [0.99],
        'clip_range': [0.2, 0.1],
        'ent_coef': [0.01, 0.001],
    }

    keys, values = zip(*param_grid.items())
    all_configs = [dict(zip(keys, v)) for v in itertools.product(*values)]

    # Create folders if not exist
    os.makedirs("tune_logs2", exist_ok=True)
    os.makedirs("tune_models2", exist_ok=True)

    print(f"Total runs: {len(all_configs)}")
    for idx, config in enumerate(all_configs):
        run_single_train(config, ports, build_path, run_id=idx)

if __name__ == "__main__":
    import subprocess
    main()
