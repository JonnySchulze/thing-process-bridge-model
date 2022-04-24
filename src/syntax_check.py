from utils import get_name_from_url

def check(tpbm):
    result = "Syntax Check Result:"
    if not "title" in tpbm:
        result += "\nERROR: title field is required"

    if not "endpoints" in tpbm:
        result += "\nERROR: endpoints field is required"
    else:
        result += iterate_tpbm(tpbm["endpoints"], tpbm["title"]) 
    return result

def iterate_tpbm(input, id):
    result = ""
    if isinstance(input, dict):
        for key, value in input.items():
            if id:
                result += iterate_tpbm(value, id+":"+key)
            else:
                result += iterate_tpbm(value, key)
        if result:
            result += "\n\n"
    elif isinstance(input, list):
        for endpoint in input:
            result += check_endpoint(endpoint)
        if result:
            result = "Subdirectory " + id + " results:\n"
    return result

def check_endpoint(tpbm_endpoint):
    response = ""
    name = ""
    if "name" in tpbm_endpoint and isinstance(tpbm_endpoint["name"], str):
        name = tpbm_endpoint["name"]
    elif "name" in tpbm_endpoint and not isinstance(tpbm_endpoint["name"], str):
        response += "\nERROR: The endpoint name has to be of string type"
    elif not "name" in tpbm_endpoint and "url" in tpbm_endpoint and isinstance(tpbm_endpoint["url"], str):
        name = get_name_from_url(tpbm_endpoint["url"])
        response += "\WARNING: No endpoint name was indicated. The endpoint point name will thus be derived from the url and will be " + name
    if name:
        name += ": "

    if not "url" in tpbm_endpoint:
        response += "\nERROR: " + name + "The endpoint url is missing"
    elif not isinstance(tpbm_endpoint["url"], str):
        response += "\nERROR: " + name + "The endpoint url has to be of string type"

    if not "profile" in tpbm_endpoint:
        response += "\nERROR: " + name + "The endpoint profile is missing"
    elif not isinstance(tpbm_endpoint["profile"], str):
        response += "\nERROR: " + name + "The endpoint profile has to be of string type, with a valid value"
    elif not tpbm_endpoint["profile"] in ["none", "delete", "get", "patch", "post", "put", "get-put", "symbolic"]:
        response += "\nERROR: " + name + tpbm_endpoint["profile"] + " is not a valid endpoint profile"

    if "input" in tpbm_endpoint and not isinstance(tpbm_endpoint["input"], (str, bool)):
        response += "\nERROR: " + name + "If indicated, input has to be of string of boolean type"
    if "icon" in tpbm_endpoint and not isinstance(tpbm_endpoint["icon"], (str, bool)):
        response += "\nERROR: " + name + "If indicated, icon has to be of string of boolean type"
    if "event" in tpbm_endpoint and not isinstance(tpbm_endpoint["event"], bool):
        response += "\nERROR: " + name + "If indicated, event has to be of boolean type"
    return response