from src.utils import check_for_media_type

def check(tpbm):
    result = "Syntax Check Result:"
    if not isinstance(tpbm, dict):
        result += "\nERROR: The top level of a TPBM must be an object"
    elif len(list(tpbm.keys())) != 1:
        result += "\nERROR: The top level of a TPBM must have a unique root"
    else:
        result += iterate_tpbm(list(tpbm.values())[0], list(tpbm.keys())[0])
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
        names = []
        for endpoint in input:
            if not isinstance(endpoint, dict):
                result += "\nInvalid syntax: Within an array, endpoints must be defined as objects"
            else:
                result += check_endpoint(endpoint, names)
                if "name" in endpoint and isinstance(endpoint["name"], str):
                    names.append(endpoint["name"])
        if result:
            result = "\nSubdirectory " + id + " results:" + result
    else:
        result += "\nERROR: Subdirectory " + id + ": Invalid syntax"
    return result

def check_endpoint(tpbm_endpoint, previous_endpoint_names):
    response = ""
    name = ""
    if not "name" in tpbm_endpoint:
        response += "\nERROR: No endpoint name was indicated"
    elif "name" in tpbm_endpoint and not isinstance(tpbm_endpoint["name"], str):
        response += "\nERROR: The endpoint name has to be of string type"
    else:
        name = tpbm_endpoint["name"] + ": "
        if tpbm_endpoint["name"] in previous_endpoint_names:
            response += "\nERROR: " + name + "This endpoint name has been already used for another endpoint on the same level"

    if not "url" in tpbm_endpoint:
        response += "\nERROR: " + name + "The endpoint url is missing"
    elif not isinstance(tpbm_endpoint["url"], str):
        response += "\nERROR: " + name + "The endpoint url has to be of string type"

    if not "profile" in tpbm_endpoint:
        response += "\nERROR: " + name + "The endpoint profile is missing"
    elif not isinstance(tpbm_endpoint["profile"], str):
        response += "\nERROR: " + name + "The endpoint profile has to be of string type, with a valid value"
    elif not tpbm_endpoint["profile"] in ["none", "delete", "get", "patch", "post", "put", "symbolic"]:
        response += "\nERROR: " + name + tpbm_endpoint["profile"] + " is not a valid endpoint profile"
    elif tpbm_endpoint["profile"] == "symbolic" and "output" in tpbm_endpoint:
        response += "\nWARNING: " + name + " Symbolic endpoints can not have an output. Even if syntactically correct, the output will be ignored"

    if "input" in tpbm_endpoint and not isinstance(tpbm_endpoint["input"], (str, bool)):
        response += "\nERROR: " + name + "If indicated, input has to be of string of boolean type"

    if "output" in tpbm_endpoint:
        if not isinstance(tpbm_endpoint["output"], (str, list)):
            response += "\nERROR: " + name + "If indicated, output has to be of string of array type"
        elif isinstance(tpbm_endpoint["output"], str):
            if not check_for_media_type(tpbm_endpoint["output"]):
                response += "\nERROR: " + name + tpbm_endpoint["output"] + " is not a media type according to RFC 6838"
        else:
            for output in tpbm_endpoint["output"]:
                if not isinstance(output, str):
                    response += "\nERROR: " + name + "The output includes an element that is not of array type"
                elif not check_for_media_type(output):
                    response += "\nERROR: " + name + output + " is not a media type according to RFC 6838"

    if "icon" in tpbm_endpoint and not isinstance(tpbm_endpoint["icon"], (str, bool)):
        response += "\nERROR: " + name + "If indicated, icon has to be of boolean type"

    if "event" in tpbm_endpoint and not isinstance(tpbm_endpoint["event"], bool):
        response += "\nERROR: " + name + "If indicated, event has to be of boolean type"
    return response