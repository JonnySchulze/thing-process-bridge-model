from utils import get_name_from_url, escape_url
from lxml import etree
import requests
import converter

thing_description = {"@context": "http://www.w3.org/ns/td",
    "securityDefinitions": {"no_sec" : {"scheme":"nosec","in":"header"}},
    "security":"no_sec"}

def get_thing_description_from_tpbm(tpbm):
    thing_description.update({"title":tpbm["title"],
    "id":"test:test-"+str(tpbm["id"])})
    for endpoint in tpbm["endpoints"]:
        add_endpoint(endpoint)
    return thing_description

def add_endpoint(endpoint):
    try:
        if "name" in endpoint:
            name = endpoint["name"]
        else:
            name = get_name_from_url(endpoint["url"])
        if endpoint["profile"] in ["delete", "patch", "post"]:
            if not "actions" in thing_description:
                thing_description.update({"actions": {}})
            if endpoint["profile"] == "delete":
                idempotent = True
            else:
                idempotent = False
            thing_description["actions"].update({name:{"safe":False,
                "idempotent":idempotent, "forms":[{"href":endpoint["url"],"op":["invokeaction"],"contentType":"application/json",
            "htv:methodName": endpoint["profile"].upper()}]}})

            thing_description["actions"][name].update(create_optionals(endpoint))
            if "input" in endpoint and (isinstance(endpoint["input"], str) or isinstance(endpoint["input"], bool) and endpoint["input"]):
                thing_description["actions"][name].update({"input": create_properties(endpoint)})
            thing_description["actions"][name].update(create_optionals(endpoint))            

        elif endpoint["profile"] in ["get", "put", "get-put"]:
            if not "properties" in thing_description:
                thing_description.update({"properties": {}})
            thing_description["properties"].update({name:{ "forms": []}})
            if endpoint["profile"] == "get":
                readonly, writeonly = True, False
                property = ["readproperty"]
            elif endpoint["profile"] == "put":
                readonly, writeonly = False, True
                property = ["writeproperty"]
            else:
                readonly, writeonly = False, False
                property = ["readproperty", "writeproperty"]
            thing_description["properties"][name].update({"readOnly": readonly, "writeOnly": writeonly})
            thing_description["properties"][name]["forms"].append({"href": endpoint["url"],
                "op": property, "contentType": "application/json"})

            thing_description["properties"][name].update(create_properties(endpoint))
            thing_description["properties"][name].update(create_optionals(endpoint))
            

        elif endpoint["profile"] == "symbolic":
            if not "symbolic" in thing_description:
                thing_description.update({"symbolic": {}})
            thing_description["symbolic"].update({name: {}})
            thing_description["symbolic"][endpoint["url"]].update(create_optionals(endpoint))

    except ValueError:
        print("Key error")

def create_optionals(endpoint):
    optionals = {}
    if "icon" in endpoint:
        if isinstance(endpoint["icon"], str):
            optionals.update({"icon": endpoint["icon"]})
        elif endpoint["icon"]:
            optionals.update({"icon": endpoint["symbol.svg"]})

    if "output" in endpoint:
        optionals.update({"output": endpoint["output"]})

    if "event" in endpoint and endpoint["event"]:
        optionals.update({"event": True})

    if "misc" in endpoint:
        optionals.update({"misc": endpoint["misc"]})
    print(optionals)
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
        for element in tree:
            properties.update(converter.create_property(element))

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
            property[name].update({"type": "array", "items": {}, "minItems": 1})
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