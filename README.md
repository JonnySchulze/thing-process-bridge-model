
# Thing Process Bridge Model

## Introduction

The **Thing Process Bridge Model** (TPBM) is an intermediary format to process endpoints and schema RelaxNG files used with the **[Cloud Process Execution Engine](https://cpee.org/)** (CPEE) and create [W3C Web of Things-correspondend **Thing Descriptions**](https://www.w3.org/TR/wot-thing-description11/) (TD).
Endpoints (mainly consisting of a URL and an HTTP request method) are used to access information about tasks that appear in processes running in the CPEE. Since the repositories and schema files used to store task information are only proprietary, the TPBM helps translate this information into equivalent Thing Descriptions.

## Requirements

- Python 10+
	- External libaries:
		- flask
		- lxml
		- requests

## How to run

After having navigated to the src subdirectory, run the flask app with `flask run`. Communicate with the locally running API using correspondend API calls:

### Post a Thing Process Bridge Model:

`curl -X POST http://127.0.0.1:5000/tpbms -H "Content-Type: application/json" -d 'ENTER THING PROCESS BRIDGE MODEL'`

### Get a Thing Description relating to a posted Thing Process Bridge Model:

`curl -X GET http://127.0.0.1:5000/tpbms/ENTER ID HERE/thing_description`

## Model Syntax
### Data Model
#### MainModel
|Attribute|Assignment|Type|Description|
|-|-|-|-|
|title|mandatory|string|The name of the TPBM<mark>, to be transferred to the generated Thing Description</mark>|
|endpoints|optional*|Array of EndpointModel|The endpoints listed in the TPBM.<br/><mark>*If only a single endpoint is to be noted, it can be indicated without the Array</mark>|
#### EndpointModel
|Attribute|Assignment|Type|Description|
|-|-|-|-|
|name|<mark>optional, yet recommended</mark>|string|The name of the endpoint. If not indicated, it is generated from the last part of the url|
|url|mandatory|string|Location of the task in the task repository|
|profile|mandatory|enum (one of delete, get, patch, post, put, get-put, symbolic, none)|HTTP request method or special behavior profile (get-put, symbolic, none; explanation below) used for the endpoint|
|input|optional|boolean or string|Indicates the presence of the default CPEE icon file (symbol.svg) or a customized file name to be used|
|icon|optional|boolean or string|Indicates the presence of the default CPEE icon file (symbol.svg) or a customized file name to be used|
|output|optional|<mark>any</mark>|Indicates the output produced by the endpoint|
|event|optional|boolean|<mark>Indicates the presence on an event caused by the endpoint</mark>|
|misc|optional|<mark>any(?)</mark>|Option for miscellaneous information to be included in the Thing Description|



### TPBM Example
```json
{
	"title":"centurio",
	"endpoints":[
		{
			"name":"write",
			"url":"https://centurio.work/ing/opcua/write/",
			"profile":"put",
			"input":"schema.rng",
			"icon":"symbol.svg",
			"output":"json",
			"event":false,
			"misc":"Something"
		}
	]
}
```