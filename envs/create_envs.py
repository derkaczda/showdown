import argparse
import os

def create_accepter(name, websocket, gamemode, run_count, data_dir, team_dir):
    return f"WEBSOCKET_URI={websocket}\n" \
    f"PS_USERNAME={name}\n" \
    f"POKEMON_MODE={gamemode}\n" \
    f"RUN_COUNT={run_count}\n" \
    f"BOT_MODE=ACCEPT_CHALLENGE\n" \
    f"DATA_DIR={data_dir}\n" \
    f"TEAM_DIR={team_dir}"

def create_challenger(name, to_challenge, password, websocket, gamemode, run_count, data_dir, team_dir):
    return f"WEBSOCKET_URI={websocket}\n" \
    f"PS_USERNAME={name}\n" \
    f"PS_PASSWORD={password}\n" \
    f"POKEMON_MODE={gamemode}\n" \
    f"RUN_COUNT={run_count}\n" \
    f"USER_TO_CHALLENGE={to_challenge}\n" \
    f"BOT_MODE=CHALLENGE_USER\n" \
    f"DATA_DIR={data_dir}\n" \
    f"DATA_COLLECTOR=True\n" \
    f"TEAM_DIR={team_dir}"

def save_file(path, content):
    with open(path, "w") as f:
        f.write(content)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--websocket", type=str, default="showdown-server:8081")
    parser.add_argument("--count", type=int, default=10, help="number of agent pairs")
    parser.add_argument("--runcount", type=int, default=10)
    parser.add_argument("--gamemode", type=str, default="gen8customgame")
    parser.add_argument("--datadir", type=str, default="dataset")
    parser.add_argument("--teamdir", type=str)
    parser.add_argument("--dest", type=str, help="the folder where we save the env files")
    args = parser.parse_args()

    username_password_map = [{ "challenger" : "dlinvcchallenge1", "password" : "JbNeAhqXqw35EEAR", "accepter" : "dlinvcaccept1" },
    { "challenger" : "dlinvcchallenge2", "password" : "Fz8LmGdX2gN8By9N", "accepter" : "dlinvcaccept2" },
    { "challenger" : "dlinvcchallenge3", "password" : "NbmjPcthUbzT4LGz", "accepter" : "dlinvcaccept3" },
    { "challenger" : "dlinvcchallenge4", "password" : "C2pWHquRtUwuVBMv", "accepter" : "dlinvcaccept4" },
    { "challenger" : "dlinvcchallenge5", "password" : "NbmjPcthUbzT4LGz", "accepter" : "dlinvcaccept5" },
    { "challenger" : "dlinvcchallenge6", "password" : "NbmjPcthUbzT4LGz", "accepter" : "dlinvcaccept6" },
    { "challenger" : "dlinvcchallenge7", "password" : "NbmjPcthUbzT4LGz", "accepter" : "dlinvcaccept7" },
    { "challenger" : "dlinvcchallenge8", "password" : "NbmjPcthUbzT4LGz", "accepter" : "dlinvcaccept8" },
    { "challenger" : "dlinvcchallenge9", "password" : "NbmjPcthUbzT4LGz", "accepter" : "dlinvcaccept9" },
    { "challenger" : "dlinvcchallenge10", "password" : "NbmjPcthUbzT4LGz", "accepter" : "dlinvcaccept10" },
    { "challenger" : "dlinvcchallenge11", "password" : "NbmjPcthUbzT4LGz", "accepter" : "dlinvcaccept11" },
    { "challenger" : "dlinvcchallenge12", "password" : "NbmjPcthUbzT4LGz", "accepter" : "dlinvcaccept12" },
    { "challenger" : "dlinvcchallenge13", "password" : "NbmjPcthUbzT4LGz", "accepter" : "dlinvcaccept13" },
    { "challenger" : "dlinvcchallenge14", "password" : "NbmjPcthUbzT4LGz", "accepter" : "dlinvcaccept14" }
    ]

    if args.count > len(username_password_map):
        print(f"Currently we only support {len(username_password_map)} agent pairs")

    if not os.path.exists(args.dest):
        os.makedirs(args.dest)

    for i in range(args.count):
        challenger, password, accepter = username_password_map[i].values()
        challenger_str = create_challenger(challenger, accepter, password, args.websocket, args.gamemode, args.runcount,
            args.datadir, args.teamdir)
        accepter_str = create_accepter(accepter, args.websocket, args.gamemode, args.runcount, args.datadir, args.teamdir)

        accept_file = os.path.join(args.dest, f"accept{i+1}")
        challenge_file = os.path.join(args.dest, f"challenge{i+1}")

        save_file(accept_file, accepter_str)
        save_file(challenge_file, challenger_str)


