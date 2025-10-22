# scripts.py
import subprocess
import os
import shlex
import argparse
import sys

def get_env(local_port: int, chat_model: str = None, chat_host: str = None, chat_port: int | None = None):
    env = os.environ.copy()
    env["LOCAL_PORT"] = str(local_port)
    if chat_model:
        env["CHAT_MODEL"] = chat_model
    if chat_host:
        env["CHAT_HOST"] = chat_host
    if chat_port:
        env["CHAT_PORT"] = str(chat_port)
    return env

def run_command(command: str, env: dict):
    args = shlex.split(command)
    try:
        subprocess.run(args, env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        sys.exit(e.returncode)

def start_chat(model: str = "llama3:8b", port: int = 8010):
    env = get_env(local_port=port, chat_model=model)
    run_command("poetry run python nlip_web/text_chat.py", env)

def start_image(model: str = "llava:7b", port: int = 8020):
    env = get_env(local_port=port, chat_model=model)
    run_command("poetry run python nlip_web/image_chat.py", env)

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="NLIP helpers")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("chat", help="Run text chat server")
    c.add_argument("--model", default="llama3:8b")
    c.add_argument("--port", type=int, default=8010)

    i = sub.add_parser("image", help="Run image chat server")
    i.add_argument("--model", default="llava:7b")
    i.add_argument("--port", type=int, default=8020)

    args = p.parse_args()
    if args.cmd == "chat":
        start_chat(args.model, args.port)
    elif args.cmd == "image":
        start_image(args.model, args.port)
