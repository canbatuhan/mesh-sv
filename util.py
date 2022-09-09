import json
import random

CONSTANTS_PATH = "configurations/constants.json"
STATEMACHINE_PATH = "configurations/statemachine.json"

constants = json.load(open(CONSTANTS_PATH, "r"))
ADDRS_LIST_PATH = constants["address_list_path"]
BUFFER_SIZE = constants["buffer_size"]
COMMANDS = constants["commands"]
ACKS = constants["acknowledgements"]

def generate_request(cmd:str, var_name:str=None, var_size:int=None, client_addr:tuple[str, int]=None) -> dict:
		return {"id": random.randint(0, 99999),
				"cmd": cmd, 
				"var_name": var_name,
				"var_size": var_size,
				"client_addr": client_addr}

def get_cmd_query(cmd_name:str) -> tuple[str, str]:
	for each in COMMANDS:
		if each.get("name") == cmd_name:
			return each.get("command"), each.get("query")

def get_cmd_query_name(cmd:str) -> str:
	for each in COMMANDS:
		if each.get("command") == cmd:
			return each.get("name")
		elif each.get("query") == cmd:
			return "QUERY"

def get_ack_nack(ack_name:str) -> tuple[str, str]:
	for each in ACKS:
		if each.get("name") == ack_name:
			return each.get("ack"), each.get("nack")

def is_nack(ack:str) -> bool:
    return "NACK" in ack