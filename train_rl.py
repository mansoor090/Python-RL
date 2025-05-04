from peaceful_pie.unity_comms import UnityComms
import argparse
from my_env import MyEnv
from stable_baselines3.ppo.ppo import PPO



def run(args: argparse.Namespace) -> None:

    unity_comms = UnityComms(port=args.port)
    model_name = args.model
    my_env = MyEnv(unity_comms=unity_comms)
    ppo = PPO.load("./tune_models/PPO_run_1")
    # ppo = PPO(
    #     "MultiInputPolicy",
    #     env=my_env,
    #     verbose=1,
    #     tensorboard_log='./tensorboard/',
    #     learning_rate=3e-4,
    #     n_steps=4096,
    #     batch_size=512,
    #     gamma=0.99,
    #     gae_lambda=0.95,
    #     clip_range=0.2,
    #     ent_coef=0.01,
    #     vf_coef=0.5,
    #     max_grad_norm=0.5,
    # )

    ppo.learn(total_timesteps=100000)


    ppo.save(model_name)


    my_env.close()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=9000)
    parser.add_argument('--model', type=str, default='PPO_Test_Model_1')
    args = parser.parse_args()
    run(args)