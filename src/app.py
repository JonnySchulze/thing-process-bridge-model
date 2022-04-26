from flask import Flask, request, jsonify
import converter
from syntax_check import check

app = Flask(__name__)
app.config['DEBUG'] = True

tpbms = []
thing_descriptions = []

def _find_next_id(type):
    if type == "td":
        descriptions = thing_descriptions
    else:
        descriptions = tpbms
    if not descriptions:
        return 1        
    else:
        return max(description["id"] for description in descriptions) + 1

@app.get("/tpbms")
def get_tpbms():
    return jsonify(tpbms)

@app.get("/thing_descriptions")
def get_thing_descriptions():
    return jsonify(thing_descriptions)

@app.post("/tpbms")
def add_tpbm():
    if request.is_json:
        tpbm = request.get_json()
        check_result = check(tpbm)
        if not "\nERROR: " in check_result:
            tpbm["id"] = _find_next_id("tpbm")
            tpbms.append(tpbm)
            return tpbm, 201
        else:
            return "Syntax errors were detected in the TPBM. " + check_result, 415
    return "error: Request must be JSON", 415

@app.post("/thing_descriptions")
def add_thing_description():
    if request.is_json:
        thing_description = request.get_json()
        thing_description["id"] = _find_next_id("td")
        thing_descriptions.append(thing_description)
        return thing_description, 201
    return "error: Request must be JSON", 415

@app.route('/thing_descriptions/<id>')
def get_thing_description(id):
    for thing_description in thing_descriptions:
        if str(thing_description["id"])==id:
            return jsonify(thing_description)
    return "Not found", 404

@app.route('/tpbms/<id>')
def get_tpbm(id):
    for tpbm in tpbms:
        if str(tpbm["id"])==id:
            return jsonify(tpbm)
    return "Not found", 404

@app.route('/tpbms/<id>/thing_description/<path>')
def convert_tpbm(id, path):
    for tpbm in tpbms:
        if str(tpbm["id"])==id:
            tds = converter.get_thing_descriptions_from_tpbm(tpbm)
            for td in tds:
                if td["id"] == path:
                    return jsonify(td)
    else:
        return "Not found", 404