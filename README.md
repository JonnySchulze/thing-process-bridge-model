# Thing Process Bridge Model
## Introduction
The Thing Process Bridge Model is an intermediary format to process endpoints and schema RelaxNG files used with the CPEE process workflow execution engine and create W3C Web of Things-correspondend Thing Descriptions.
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
### Example Model
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