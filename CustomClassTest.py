from dataclasses import dataclass

from peaceful_pie.unity_comms import UnityComms
import argparse

@dataclass
class MyVector3:
    x: float
    y: float
    z: float


def run(args: argparse.Namespace) -> None:
    unity_comms = UnityComms(port=args.port)
    res = unity_comms.GetPos(ResultClass = MyVector3)
    print('res', res)
    print(type(res))
    print(res.x, res.y, res.z)
    #unity_comms.Say(message=args.message)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=9000)

    #parser.add_argument('--message', type=str, required=True)
    args = parser.parse_args()
    run(args)