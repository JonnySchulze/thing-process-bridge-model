from src.utils import escape_url
from lxml import etree
import requests
from copy import deepcopy

thing_descriptions = []
default_thing_description = {"@context": "http://www.w3.org/ns/td",
    "securityDefinitions": {"no_sec" : {"scheme":"nosec","in":"header"}},
    "security":"no_sec"}

def get_thing_descriptions_from_tpbm(tpbm):
    iterate_tpbm(tpbm["endpoints"], tpbm["title"])
    return thing_descriptions

def iterate_tpbm(input, id):
    if isinstance(input, dict):
        for key, value in input.items():
            if id:
                iterate_tpbm(value, id+":"+key)
            else:
                iterate_tpbm(value, key)
    elif isinstance(input, list):
        thing_description = deepcopy(default_thing_description)
        thing_description.update({"id": id})
        for endpoint in input:
            thing_description = add_endpoint(endpoint, thing_description)
        thing_descriptions.append(thing_description)

def add_endpoint(endpoint, thing_description):
    name = endpoint["name"]
    if endpoint["profile"] in ["delete", "get", "patch", "post", "put", "none", "symbolic"]:
        if not "actions" in thing_description:
            thing_description.update({"actions": {}})
        idempotent = endpoint["profile"] in ["delete", "get", "put", "symbolic"]
        safe = endpoint["profile"] in ["get", "symbolic"]
        thing_description["actions"].update({name:{"safe":safe,
            "idempotent":idempotent, "forms":[{"href":endpoint["url"],"op":["invokeaction"],"contentType":"application/json"}]}})
        if not endpoint["profile"] in ["none", "symbolic"]:
            thing_description["actions"][name]["forms"][0].update({"htv:methodName": endpoint["profile"].upper()})

        thing_description["actions"][name].update(create_optionals(endpoint))
        if "input" in endpoint:
            if isinstance(endpoint["input"], str) or isinstance(endpoint["input"], bool) and endpoint["input"]:
                thing_description["actions"][name].update({"input": create_properties(endpoint)})
        thing_description["actions"][name].update(create_optionals(endpoint))

    return thing_description

def create_optionals(endpoint):
    optionals = {}
    if "icon" in endpoint:
        if isinstance(endpoint["icon"], str):
            optionals.update({"icon": endpoint["icon"]})
        elif endpoint["icon"]:
            optionals.update({"icon": endpoint["symbol.svg"]})

    if "input" in endpoint and isinstance(endpoint["input"], str):
        if endpoint["input"] != "schema.rng":
            optionals.update({"schema_name": endpoint["input"]})

    if "output" in endpoint and endpoint["profile"] != "symbolic":
        if isinstance(endpoint["output"], str):
            optionals.update({"output": {"type": "string", "contentMediaType": endpoint["output"]}})
        else:
            optionals.update({"output": {"type": "object", "properties": {}}})
            index = 0
            while index < len(endpoint["output"]):
                optionals["output"].update({"par"+str(index): {"type": "string", "contentMediaType": endpoint["output"][index]}})

    if "event" in endpoint and endpoint["event"]:
        optionals.update({"event": True})

    if "misc" in endpoint:
        optionals.update({"misc": endpoint["misc"]})
    return optionals

def create_properties(endpoint):
    if not "input" in endpoint or isinstance(endpoint["input"], bool) and not endpoint["input"]:
        return {"type": "string"}
    else:
        if isinstance(endpoint["input"], bool) and endpoint["input"]:
            schema_url = "schema.rng"
        elif isinstance(endpoint["input"], str):
            schema_url = endpoint["input"]
        url = "https://cpee.org/flow/resources/endpoints/"+escape_url(endpoint["url"], endpoint["profile"])+"/"+schema_url
        
        tree = etree.fromstring(requests.get(url).text)
        properties = {}
        if tree.getchildren()[0].tag == "{http://relaxng.org/ns/structure/1.0}element":
            for element in tree:
                properties.update(create_property(element))
        else:
            properties.update(create_property(tree))

        if len(properties.keys()) > 1:
            properties = {"type": "object", "properties": properties}
        return properties

def create_property(element):
    relaxng_url = "{http://relaxng.org/ns/structure/1.0}"
    name = ""
    property = {}
    if "name" in element.attrib:
        name = element.attrib["name"]
        property.update({name: {}})
        if "{http://rngui.org}label" in element.attrib:
            property[name].update({"title": element.attrib["{http://rngui.org}label"]})
    elif "{http://rngui.org}label" in element.attrib:
        name = element.attrib["{http://rngui.org}label"]
        property.update({name: {}})
    else:
        name = "unnamed_element"
        property.update({name: {}})

    children_types = []
    for children in element.getchildren():
        children_types.append(children.tag)
    if len(children_types) == 1 or relaxng_url+"data" in children_types:
        index = 0
        if element.getchildren()[0].tag == relaxng_url+"anyName":
            index = 1
        type = element.getchildren()[index].tag
        if type == relaxng_url+"data":
            if "type" in element.getchildren()[index].attrib:
                if element.getchildren()[index].attrib["type"] in ["boolean","integer","string"]:
                    property[name].update({"type": element.getchildren()[index].attrib["type"]})
                elif element.getchildren()[index].attrib["type"] == "nonNegativeInteger":
                    property[name].update({"type": "integer", "minimum": 0})

            if "{http://rngui.org}label" in element.getchildren()[index].attrib:
                property[name].update({"description": element.getchildren()[index].attrib["{http://rngui.org}label"]})
        elif type == relaxng_url+"text":
            property[name].update({"type": "string", "misc": "message"})
            if "{http://rngui.org}label" in element.getchildren()[index].attrib:
                property[name].update({"description": element.getchildren()[index].attrib["{http://rngui.org}label"]})
        elif type == relaxng_url+"choice":
            enum = []
            for value in element.getchildren()[index]:
                enum.append(value.text)
            property[name].update({"type": "string", "enum": enum})
        elif type == relaxng_url+"zeroOrMore":
            property[name].update({"type": "array", "items": {}})
            if element.getchildren()[index].getchildren()[0].tag == relaxng_url+"element":
                array_items = create_property(element.getchildren()[index].getchildren()[0])
                property[name]["items"] = array_items

            if "{http://rngui.org}label" in element.getchildren()[index].attrib:
                property[name].update({"description": element.getchildren()[index].attrib["{http://rngui.org}label"]})

    elif len(element.getchildren()) > 1:
        property[name].update({"type": "object", "properties": {}})
        for child_element in element.getchildren():
            latest_element = create_property(child_element)
            child_key, child_value = list(latest_element.items())[0]
            if child_key in property[name]["properties"].keys():
                index = 1
                while child_key+"_"+str(index) in property[name]["properties"].keys():
                    index += 1
                latest_element[child_key+"_"+str(index)] = latest_element.pop(child_key)
            property[name]["properties"].update(latest_element)
      
    return property