# Schema Context Extension Ontology
The parameters listed below may be used in the generated Thing Descriptions (TDs) as part of the `schema` context extension. Specifically, `schema` parameters may occur in the data objects nested in the parameter describing the input of an endpoint (`input`, `subscription`, `unsubscription`). The `schema` context extension is used to represent elements and attributes in the schema files specified for the endpoints in the Thing Process Bridge Model, for which the Thing Description does not provide its own suitable parameters.
|Parameter|Description|
|-|-|
|`schema:anyName`|Set to `true` if an `anyName` element is nested in an `element` element.|
|`schema:attribute`|Set to `true` if a TD data object represents an `attribute` element. Required to distinguish `attribute` and `element` elements.|
|`schema:hint`|Takes the value of the `rngui:hint` attribute if specified.|
|`schema:optional`|Set to `true` if an input argument is optional to assign. Recognizable in schema files by argument-root `element` element being nested in `optional` element.|
|`schema:text`|Set to `true` if an input argument is a text. Required to distinguish text and string data object arguments.|
|`schema:wrap`|Set to `true` if the `rngui:wrap` attribute is set in a `text` element.|