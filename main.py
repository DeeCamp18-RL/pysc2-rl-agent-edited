import os, argparse
from absl import flags
flags.FLAGS(['main.py'])
import tensorflow as tf

from common import Config
from common.env import make_envs
from rl.agent import A2CAgent
from rl.model import fully_conv
from rl import Runner, EnvWrapper

if __name__ == '__main__':
    # flags.FLAGS(['main.py'])
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpu", type=int, default=0)
    parser.add_argument("--sz", type=int, default=32)
    parser.add_argument("--envs", type=int, default=32)
    parser.add_argument("--render", type=int, default=1)
    parser.add_argument("--steps", type=int, default=16)
    parser.add_argument("--updates", type=int, default=1000000)
    parser.add_argument('--lr', type=float, default=7e-4)
    parser.add_argument('--vf_coef', type=float, default=0.25)
    parser.add_argument('--ent_coef', type=float, default=1e-3)
    parser.add_argument('--discount', type=float, default=0.99)
    parser.add_argument('--clip_grads', type=float, default=1.)
    parser.add_argument("--run_id", type=int, default=-1)
    parser.add_argument("--map", type=str, default='MoveToBeacon')
    parser.add_argument("--cfg_path", type=str, default='config.json.dist')
    parser.add_argument("--test", type=bool, nargs='?', const=True, default=False)
    parser.add_argument("--restore", type=bool, nargs='?', const=True, default=False)
    parser.add_argument('--save_replay', type=bool, nargs='?', const=True, default=False)
    parser.add_argument('--save_best_only', type=bool, nargs='?', const=True, default=False)
    args = parser.parse_args()

    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)
    tf.reset_default_graph() 
    sess = tf.Session()
    # config = Config(args.sz, args.map, lambda _: 1)
    config = Config(args.sz, args.map, args.run_id)
    os.makedirs('weights/' + config.full_id(), exist_ok=True)
    cfg_path = 'weights/%s/config.json' % config.full_id()
    config.build(cfg_path if args.restore else args.cfg_path)
    if not args.restore and not args.test:
        config.save(cfg_path)

    envs = EnvWrapper(make_envs(args), config)
    agent = A2CAgent(sess, fully_conv, config, args.restore, args.discount, args.lr, args.vf_coef, args.ent_coef, args.clip_grads, args.save_best_only, not args.test)

    runner = Runner(envs, agent, not args.test, args.steps)
    runner.run(args.updates)

    if args.save_replay:
        envs.save_replay()

    envs.close()
