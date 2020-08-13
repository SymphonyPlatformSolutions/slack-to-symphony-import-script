import re
import argparse
import logging
import os

from pathlib import Path
from slack import WebClient
from slack.errors import SlackApiError
from slack_rooms import SlackRoom
from slack_import import SlackImport
from sym_api_client_python.auth.rsa_auth import SymBotRSAAuth
from sym_api_client_python.clients.sym_bot_client import SymBotClient
from sym_api_client_python.configure.configure import SymConfig
from sym_api_client_python.exceptions.APIClientErrorException import APIClientErrorException


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--auth", choices=["rsa", "cert"], default="rsa",
        help="Authentication method to use")
    parser.add_argument("--config", help="Config json file to be used")
    args = parser.parse_args()
    # Cert Auth flow: pass path to certificate config.json file
    config_path = args.config
    configure = SymConfig(config_path, config_path)
    configure.load_config()
    if args.auth == "rsa":
        auth = SymBotRSAAuth(configure)
    elif args.auth == "cert":
        auth = Auth(configure)
    else:
        raise ValueError("Unexpected value for auth: " + args.auth)
    auth.authenticate()
    # Initialize SymBotClient with auth and configure objects
    bot_client = SymBotClient(auth, configure)
    print('successfully authenticated')
    slack_token = "xoxb-1176760234163-1161874769927-DeI0LsLlIfRKDynhm2Ewf358"
    room_obj = SlackRoom(slack_token).import_rooms(bot_client)
    print('successfully created rooms')
    slack_import = SlackImport(slack_token, room_obj).run_import(bot_client)

if __name__ == "__main__":
    main()
