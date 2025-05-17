import json
import argparse
import gymnasium as gym
import numpy as np

from dataclasses import dataclass
from peaceful_pie.unity_comms import UnityComms
from numpy.typing import NDArray
from typing import Tuple, Any
from gymnasium import spaces
from stable_baselines3.common.env_checker import check_env



@dataclass
class Observations:
    #dead: bool
    myPosition: list[int]   # [x, y, z]
    targetPos: list[int]    # [dx, dy, dz]
    hurdleBools: list[bool] # list of bools indicating if the agent has hurdle in 4 directions
    waterBools: list[bool]  # list of bools indicating if the agent has water in 4 directions

    
@dataclass
class RlResult:
    reward: float
    finished: bool
    truncate: bool
    obs: Observations



class MyEnv(gym.Env):
    max_hurdles : int = 14



    def __init__(self, unity_comms: UnityComms):

        self.unity_commes = unity_comms
        # self.action_space = spaces.Discrete(8)
        # action_space = [action_type, direction]
        # action_type: 0 = walk, 1 = jump
        # direction: 0 = north, 1 = south, 2 = west, 3 = east
        self.action_space = spaces.MultiDiscrete([2, 4])

        self.observation_space = spaces.Dict({
            "myPosition": spaces.Box(low=-np.inf, high=np.inf, shape=(3,), dtype=np.float32),
            "targetPos": spaces.Box(low=-np.inf, high=np.inf, shape=(3,), dtype=np.float32),
            "hurdleBools": spaces.Box(low=0, high=1, shape=(4,), dtype=np.float32),
            "waterBools": spaces.Box(low=0, high=1, shape=(4,), dtype=np.float32)
        })

    def step(self, action: NDArray[np.uint8]) -> Tuple[dict[str, NDArray[np.float32] | int], float, bool, bool, dict[str, Any]]:

        action_type, direction = action  # action[0], action[1]

        action_str = ["north", "south", "east", "west"][direction]
        if action_type == 1:
            action_str = "jump_" + action_str

        rlResult: RlResult = self.unity_commes.Step(action=action_str, ResultClass=RlResult)
        info = {"finished": rlResult.finished}  # or any other info you want

        obs_dict = {
            "myPosition": np.array(rlResult.obs.myPosition, dtype=np.float32),
            "targetPos": np.array(rlResult.obs.targetPos, dtype=np.float32),
            "hurdleBools": np.array(rlResult.obs.hurdleBools, dtype=np.float32),
            "waterBools": np.array(rlResult.obs.waterBools, dtype=np.float32)
        }

        save_obs_to_file(obs_dict, rlResult.reward)
        return obs_dict, rlResult.reward, rlResult.finished, rlResult.truncate, info


    def reset(self, seed=None, **kwargs) -> Tuple[dict[str, NDArray[np.float32] | int], dict[str, Any]]:
        obs: Observations = self.unity_commes.Reset(ResultClass = Observations)

        obs_dict = {
            "myPosition": np.array(obs.myPosition, dtype=np.float32),
            "targetPos": np.array(obs.targetPos, dtype=np.float32),
            "hurdleBools": np.array(obs.hurdleBools, dtype=np.float32),
            "waterBools": np.array(obs.waterBools, dtype=np.float32)
        }

        return obs_dict, {}



def run(args: argparse.Namespace) -> None:
    unity_comms = UnityComms(port=args.port)
    my_env = MyEnv(unity_comms=unity_comms)
    check_env(my_env)

def save_obs_to_file(obs, reward):
    data = {
        "observation": {k: v.tolist() for k, v in obs.items()},
        "reward": reward
    }
    with open("latest_obs.json", "w") as f:
        json.dump(data, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=9000)
    args = parser.parse_args()
    run(args)