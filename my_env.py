from dataclasses import dataclass
from peaceful_pie.unity_comms import UnityComms
import argparse
import gymnasium as gym
import numpy as np
from numpy.typing import NDArray
from typing import Tuple, Any
from gymnasium import spaces
from stable_baselines3.common.env_checker import check_env
import json




@dataclass
class Observations:
    #dead: bool
    myPosition: list[int]         # [x, y, z]
    targetPos: list[int]   # [dx, dy, dz]
    canMove: list[bool]  # list of bools indicating if the agent can move to that position
    # walkablePos: list[list[int]]  # list of [hx, hy, hz]
    # hurdlesPositions: list[list[int]]  # list of [hx, hy, hz]
    
@dataclass
class RlResult:
    reward: float
    finished: bool
    truncate: bool
    obs: Observations



class MyEnv(gym.Env):
    max_hurdles : int = 14

    def __init__(self, unity_comms: UnityComms):

        walkCount : int = 0
        hurdleCount: int = 0

        # walkCount = unity_comms.GetWalkableCount()
        # hurdleCount = unity_comms.GetHurdleCount()


        self.unity_commes = unity_comms
        self.action_space = spaces.Discrete(4)
        # self.action_space = spaces(6)
        self.observation_space = spaces.Dict({
           # "dead": spaces.Discrete(2),
            "myPosition": spaces.Box(low=-np.inf, high=np.inf, shape=(3,), dtype=np.float32),
            "targetPos": spaces.Box(low=-np.inf, high=np.inf, shape=(3,), dtype=np.float32),
            "canMove": spaces.Box(low=0, high=1, shape=(4,), dtype=np.float32)  # NEW
            # "walkablePos": spaces.Box(low=-np.inf, high=np.inf, shape=(walkCount, 3), dtype=np.float32),
            # "hurdlesPositions": spaces.Box(low=-np.inf, high=np.inf, shape=(hurdleCount, 3), dtype=np.float32)
            
        })

    def step(self, action: NDArray[np.uint8]) -> Tuple[dict[str, NDArray[np.float32] | int], float, bool, bool, dict[str, Any]]:

        action_str = ["north","south","east","west"][action]

        rlResult: RlResult = self.unity_commes.Step(action=action_str, ResultClass=RlResult)
        info = {"finished": rlResult.finished}  # or any other info you want

        obs_dict = {
            "myPosition": np.array(rlResult.obs.myPosition, dtype=np.float32),
            "targetPos": np.array(rlResult.obs.targetPos, dtype=np.float32),
            "canMove": np.array(rlResult.obs.canMove, dtype=np.float32),  # NEW
            # "walkablePos": np.array(rlResult.obs.walkablePos, dtype=np.float32),
            # "hurdlesPositions": np.array(rlResult.obs.hurdlesPositions, dtype=np.float32),
            
        }

        save_obs_to_file(obs_dict, rlResult.reward)
        return obs_dict, rlResult.reward, rlResult.finished, rlResult.truncate, info


    def reset(self, seed=None, **kwargs) -> Tuple[dict[str, NDArray[np.float32] | int], dict[str, Any]]:
        obs_vec3: Observations = self.unity_commes.Reset(ResultClass = Observations)

        obs_dict = {
            "myPosition": np.array(obs_vec3.myPosition, dtype=np.float32),
            "targetPos": np.array(obs_vec3.targetPos, dtype=np.float32),
            "canMove": np.array(obs_vec3.canMove, dtype=np.float32),  # NEW
            # "walkablePos": np.array(rlResult.obs.walkablePos, dtype=np.float32),
            # "hurdlesPositions": np.array(rlResult.obs.hurdlesPositions, dtype=np.float32),
            
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