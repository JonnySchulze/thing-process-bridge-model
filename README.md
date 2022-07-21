
# Thing Process Bridge Model

## Introduction

The **Thing Process Bridge Model** (TPBM) is an intermediary format to process endpoints and schema RelaxNG files used with the **[Cloud Process Execution Engine](https://cpee.org/)** (CPEE) and create [W3C Web of Things-correspondend **Thing Descriptions**](https://www.w3.org/TR/wot-thing-description11/) (TD).
Endpoints (mainly consisting of a URL and an HTTP request method) are used to access information about tasks that appear in processes running in the CPEE. Since the repositories and schema files used to store task information are only proprietary, the TPBM helps translate this information into equivalent Thing Descriptions.

## Requirements

- Python 10+
	- External libaries:
		- copy
		- flask
		- lxml
		- requests

## How to run

Run the flask app with `flask run`. Communicate with the locally running API using correspondend API calls:

### Post a Thing Process Bridge Model:

`curl -X POST http://127.0.0.1:5000/tpbms -H "Content-Type: application/json" -d 'ENTER THING PROCESS BRIDGE MODEL'`

### Get a Thing Description relating to a posted Thing Process Bridge Model:

`curl -X GET http://127.0.0.1:5000/tpbms/ENTER ID HERE/thing_description`

## Model Syntax
### Data Model
#### InnerModel
<table>
    <thead>
        <tr>
            <th>Key</th>
            <th>Key meaning</th>
            <th>Value</th>
		    <th>Value meaning</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td rowspan=3>name</td>
            <td rowspan=3>The name of the inner node in the TPBM’s tree model</td>
            <td>Map of <i>InnerModel</i></td>
            <td>Further inner nodes are nested in this node</td>
        </tr>
        <tr>
            <td colspan=2 style="text-align:center"><i>or</i></td>
        </tr>
        <tr>
            <td>Array of <i>EndpointModel</i></td>
            <td>A set of endpoints is nested in this node</td>
        </tr>
    </tbody>
</table>

#### EndpointModel
|Attribute|Assignment|Type|Description|
|-|-|-|-|
|name|mandatory|string|The name of the endpoint, has to be unique for all endpoints on the same level|
|url|mandatory|string|Location of the task in the CPEE endpoint repository|
|profile|mandatory|enum (one of delete, get, patch, post, put, symbolic, none)|HTTP method or special behavior profile used for the endpoint|
|input|optional|boolean or string|Indicates the presence of the default CPEE schema file (schema.rng) or a custom named file name to be used|
|icon|optional|boolean or string|Indicates the presence of the default CPEE icon file (symbol.svg) or a custom named file name to be used|
|output|optional|string or Array of strings|Indicates the served output of the endpoint through a media type or a sequence of media types|
|async|optional|boolean|Indicates whether the endpoint output is sent in an asynchronous way|
|miscFiles|optional|string or Array of strings|Indicates miscellaneous files that are present in the endpoint repository entry|
### TPBM Example
```json
{
   "centurio":[
      {
         "name":"write",
         "url":"https://centurio.work/ing/opcua/write/",
         "profile":"put",
         "input":"schema.rng",
         "icon":"symbol.svg",
         "output":"application/json",
         "async":false,
         "miscFiles":"contents.json"
      }
   ]
}
```