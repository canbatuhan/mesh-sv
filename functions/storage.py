import time

def load(storage:list[dict], last_request:dict):
    is_success = False
    for each in storage: # Search for variable by name
        if each.get("var_name") == last_request.get("var_name"):
            time.sleep(each.get("var_size")/1000) # Execution time
            is_success = True # Success
            break
    return {"is_success": is_success}


def store(storage:list[dict], last_request:dict, capacity:int, in_use:int):
    is_success = False
    for each in storage: # Search for variable
        if each.get("var_name") == last_request.get("var_name"):
            return {"is_success": True} # If found directly return

    if last_request.get("var_size") + in_use <= capacity: # If size does not overflow capacity
        storage.append(last_request) # Store
        in_use += last_request.get("var_size")
        time.sleep(last_request.get("var_size")/1000) # Execution time
        is_success = True
    
    return {"storage": storage, "in_use": in_use, "is_success": is_success}


def update(storage:list[dict], last_request:dict, capacity:int, in_use:int):
    old_request = dict()
    is_success = False # Not found

    for each in storage: # Search for the request
        if each.get("var_name") == last_request.get("var_name"):
            old_request = each
            is_success = True # Found
            break
    
    if is_success: # If found, check size
        size_diff = last_request.get("var_size") - old_request.get("var_size")
        if in_use + size_diff <= capacity: # If does not overflow the capacity
            storage.remove(old_request) # Delete old
            time.sleep(old_request.get("var_size")/1000) # Execution time

            storage.append(last_request) # Add new
            in_use += size_diff
            time.sleep(last_request.get("var_size")/1000) # Execution time
    
    return {"storage": storage, "in_use": in_use, "is_success": is_success}