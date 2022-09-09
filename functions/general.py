import random
import time


def greet(greeting_addr:dict, neighbours:list):
    neighbours.append(greeting_addr)
    return {"neighbours": neighbours, "is_success": True}

def leave(greeting_addr:dict, neighbours:list):
    neighbours.remove(greeting_addr)
    return {"neighbours": neighbours, "is_success": True}

def finish(neighbours:list):
    neighbours.clear()
    return {"neighbours": neighbours}

def query(capacity:int, in_use:int, storage:list[dict], last_request:dict):
    is_success = False
    for each in storage:
        if each.get("var_name") == last_request.get("var_name"):
            is_success = True
            break
    time.sleep(random.choice(range(0, 5000, 100))/1000)
    return {"is_success": is_success}