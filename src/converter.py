from src.utils import escape_url, typecast
from lxml import etree
import requests
from copy import deepcopy

default_thing_description = {"@context": ["https://www.w3.org/2022/wot/td/v1.1", 
    {"tpbm": "https://github.com/JonnySchulze/thing-process-bridge-model",
    "schema": "https://cpee.org/flow/resources/endpoints"}],
    "securityDefinitions": {"no_sec" : {"scheme":"nosec"}},
    "security":"no_sec"}

def get_thing_descriptions_from_tpbm(tpbm):
    thing_descriptions = iterate_tpbm(list(tpbm.values())[0], list(tpbm.keys())[0])
    if isinstance(thing_descriptions, dict):
        thing_descriptions = [thing_descriptions]
    return thing_descriptions

def iterate_tpbm(input, id):
    if isinstance(input, dict):
        thing_descriptions = []
        for key, value in input.items():
            if id:
                thing_descriptions.append(iterate_tpbm(value, id+":"+key))
            else:
                thing_descriptions.append(iterate_tpbm(value, key))
        return thing_descriptions
    elif isinstance(input, list):
        thing_description = deepcopy(default_thing_description)
        title = id.rsplit(':', 1)[-1] or id
        thing_description.update({"title": title, "id": id})
        for endpoint in input:
            thing_description = add_endpoint(endpoint, thing_description)
        return thing_description

def add_endpoint(endpoint, thing_description):
    name = endpoint["name"]
    if not "async" in endpoint or not endpoint["async"]:
        affordance_used = "action"
    else:
        affordance_used = "event"

    if not affordance_used in thing_description:
            thing_description.update({affordance_used+"s": {}})

    if affordance_used == "action":    
        idempotent = endpoint["profile"] in ["delete", "get", "put", "symbolic"]
        safe = endpoint["profile"] in ["get", "symbolic"]
        thing_description["actions"].update({name:{"safe":safe,"idempotent":idempotent,"forms":[{"op":["invokeaction"]}]}})
    else:
        if endpoint["profile"] != "delete":
            op = "subscribeevent"
        else:
            op = "unsubscribeevent"
        thing_description["events"].update({name:{"forms":[{"op":[op]}]}})

    thing_description[affordance_used+"s"][name]["forms"][0].update({"href":endpoint["url"],"contentType":"application/x-www-form-urlencoded"})
    if not endpoint["profile"] in ["none", "symbolic"]:
            thing_description[affordance_used+"s"][name]["forms"][0].update({"htv:methodName": endpoint["profile"].upper()})

    if "input" in endpoint:
        if isinstance(endpoint["input"], str) or isinstance(endpoint["input"], bool) and endpoint["input"]:
            input, file_found = create_input(endpoint)
            if file_found:
                thing_description[affordance_used+"s"][name]["forms"][0]["contentType"] = "multipart/form-data"
            if affordance_used == "action":
                input_param = "input"
            elif endpoint["profile"] != "delete":
                input_param = "subscription"
            else:
                input_param = "unsubscription"
            thing_description[affordance_used+"s"][name].update({input_param: input})
                
    if "output" in endpoint and endpoint["profile"] != "symbolic":
        if affordance_used == "action":
            thing_description["actions"][name].update({"output": create_output(endpoint["output"])})
        else:
            thing_description["events"][name].update({"data": create_output(endpoint["output"])})

    thing_description[affordance_used+"s"][name].update(create_optionals(endpoint))

    return thing_description

def create_optionals(endpoint):
    optionals = {}
    if "icon" in endpoint:
        if isinstance(endpoint["icon"], str):
            optionals.update({"tpbm:icon": endpoint["icon"]})
        elif endpoint["icon"]:
            optionals.update({"tpbm:icon": "symbol.svg"})

    if "input" in endpoint and isinstance(endpoint["input"], str):
        if endpoint["input"] != "schema.rng":
            optionals.update({"tpbm:schemaName": endpoint["input"]})

    if "miscFiles" in endpoint:
        optionals.update({"tpbm:miscFiles": endpoint["miscFiles"]})
    return optionals

def create_output(output):
    if isinstance(output, str):
        return {"type": "string", "contentMediaType": output}
    else:
        td_output = {"type": "object", "properties": {}}
        index = 0
        while index < len(output):
            td_output["properties"].update({"par"+str(index): {"type": "string", "contentMediaType": output[index]}})
            index += 1
        return td_output

def create_input(endpoint):
    if isinstance(endpoint["input"], bool) and endpoint["input"]:
        schema_url = "schema.rng"
    elif isinstance(endpoint["input"], str):
        schema_url = endpoint["input"]
    url = "https://cpee.org/flow/resources/endpoints/"+escape_url(endpoint["url"], endpoint["profile"])+"/"+schema_url
    
    tree = etree.fromstring(requests.get(url).text)
    data_objects = {}
    file_found = False
    if tree.getchildren()[0].tag == "{http://relaxng.org/ns/structure/1.0}element":
        for element in tree:
            if element.tag != "{http://relaxng.org/ns/structure/1.0}optional":
                data_object, file_found_object = create_data_object(element)
            else:
                data_object, file_found_object = create_data_object(element.getchildren()[0], False, True)
            data_objects.update(data_object)
            file_found = file_found or file_found_object
    else:
        data_object, file_found_object = create_data_object(tree)
        data_objects.update(data_object)
        file_found = file_found or file_found_object

    if len(data_objects.keys()) > 1:
        data_objects = {"type": "object", "properties": data_objects}
    else:
        data_objects = list(data_objects.values())[0]
    return data_objects, file_found

def create_data_object(element, head_name = False, optional = False):
    relaxng_url = "{http://relaxng.org/ns/structure/1.0}"
    data_object = {}
    file_found = False
    if "name" in element.attrib:
        name = element.attrib["name"]
    elif head_name:
        name = head_name
    else:
        name = "unnamedElement"
    data_object.update({name: {}})
    if "{http://rngui.org}label" in element.attrib:
        data_object[name].update({"title": element.attrib["{http://rngui.org}label"]})
    elif "{http://rngui.org}header" in element.attrib:
        data_object[name].update({"title": element.attrib["{http://rngui.org}header"]})
    if "{http://rngui.org}default" in element.attrib:
        data_object[name].update({"default": typecast(element.attrib["{http://rngui.org}default"])})
    if "{http://rngui.org}hint" in element.attrib:
        data_object[name].update({"schema:hint": element.attrib["{http://rngui.org}hint"]})
    if element.tag == relaxng_url+"attribute":
        data_object[name].update({"schema:attribute": True})
    if optional:
         data_object[name].update({"schema:optional": True}) 
    
    if head_name or name == "unnamedElement" and element.tag == relaxng_url+"data":
        data_object[name].update(parse_data(element.attrib))
        return data_object, file_found

    children_types = []
    for children in element.getchildren():
        children_types.append(children.tag)
    if len(children_types) == 1 or len(children_types) == 2 and relaxng_url+"anyName" in children_types:
        index = 0
        if relaxng_url+"anyName" in children_types:
            data_object[name].update({"schema:anyName": True})
            if element.getchildren()[0].tag == relaxng_url+"anyName":
                index = 1

        element_type = element.getchildren()[index].tag
        if element_type == relaxng_url+"data":
            data_object[name].update(parse_data(element.getchildren()[index].attrib))
        elif element_type == relaxng_url+"text":
            data_object[name].update({"type": "string", "schema:text": True})
            if "{http://rngui.org}label" in element.getchildren()[index].attrib:
                data_object[name].update({"description": element.getchildren()[index].attrib["{http://rngui.org}label"]})
            if "{http://rngui.org}wrap" in element.getchildren()[index].attrib and element.getchildren()[index].attrib["{http://rngui.org}wrap"]:
                data_object[name].update({"schema:wrap": True})
        elif element_type == relaxng_url+"choice":
            enum = []
            for value in element.getchildren()[index]:
                enum.append(typecast(value.text))
            data_object[name].update({"enum": enum})
            data_object[name].update({"type": get_enum_type(data_object, name)})
        elif element_type == relaxng_url+"attribute":
            child_element, child_file_found = create_data_object(element.getchildren()[index].attrib)
            data_object[name].update(child_element)
            data_object[name].update({"schema:attribute": True})
            file_found = file_found or child_file_found
        elif element_type == relaxng_url+"zeroOrMore":
            data_object[name].update({"type": "array", "items": {}})
            if element.getchildren()[index].getchildren()[0].tag == relaxng_url+"element":
                array_items, file_found_child = create_data_object(element.getchildren()[index].getchildren()[0])
                file_found = file_found or child_file_found
                data_object[name]["items"] = list(array_items.values())[0]

            if "{http://rngui.org}label" in element.getchildren()[index].attrib:
                data_object[name].update({"description": element.getchildren()[index].attrib["{http://rngui.org}label"]})

    elif len(element.getchildren()) > 1:
        data_object[name].update({"type": "object", "properties": {}})
        for child_element in element.getchildren():
            if child_element.tag == relaxng_url+"data" and name != "unnamedElement":
                latest_element, child_file_found = create_data_object(child_element, name, False)
            else:
                latest_element, child_file_found = create_data_object(child_element)
            file_found = file_found or child_file_found
            child_key, child_value = list(latest_element.items())[0]
            if child_key in data_object[name]["properties"].keys():
                index = 1
                while child_key+"_"+str(index) in data_object[name]["properties"].keys():
                    index += 1
                latest_element[child_key+"_"+str(index)] = latest_element.pop(child_key)
            data_object[name]["properties"].update(latest_element)
      
    return data_object, file_found

def parse_data(data_element):
    data_object = {}
    if "type" in data_element:
        if data_element["type"] in ["boolean","integer","string"]:
            data_object.update({"type": data_element["type"]})
        elif data_element["type"] == "float":
            data_object.update({"type": "number"})
        elif data_element["type"] == "nonNegativeInteger":
            data_object.update({"type": "integer", "minimum": 0})

    if "{http://rngui.org}label" in data_element:
        data_object.update({"description": data_element["{http://rngui.org}label"]})
    return data_object

def get_enum_type(data_object, name):
    data_types = []
    if "default" in data_object[name]:
        data_types.append(str(type(data_object[name]["default"])))
    for enum_entry in data_object[name]["enum"]:
        data_types.append(str(type(enum_entry)))
    most_frequent_type = max(set(data_types), key = data_types.count)
    if most_frequent_type == "<class 'str'>":
        return "string"
    elif most_frequent_type == "<class 'int'>":
        return "integer"
    elif most_frequent_type == "<class 'float'>":
        return "number"
    else:
        return "bool"