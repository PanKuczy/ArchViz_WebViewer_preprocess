/*
	Export a JSON map of geometry object names to their G-buffer IDs.

	The selected layer includes all of its nested child layers. Duplicate object
	names are written once, using the first matching object encountered.
*/
global PBD_GBufferMapRollout

fn PBD_GBufferJsonEscape value =
(
	local result = value as string
	result = substituteString result "\\" "\\\\"
	result = substituteString result "\"" "\\\""
	result = substituteString result "\n" "\\n"
	result = substituteString result "\r" "\\r"
	result = substituteString result "\t" "\\t"
	result
)

fn PBD_GBufferIdText value =
(
	formattedPrint (value as integer) format:"05d"
)

fn PBD_GBufferIsGeometry node =
(
	isValidNode node and (superClassOf node == GeometryClass)
)

fn PBD_GBufferLayerIsDescendant layer rootLayer =
(
	local currentLayer = layer
	local isIncluded = false
	while currentLayer != undefined and not isIncluded do
	(
		isIncluded = currentLayer == rootLayer
		if not isIncluded then currentLayer = currentLayer.getParent()
	)
	isIncluded
)

fn PBD_GBufferLayerNames =
(
	local layerNames = #()
	for layerIndex = 0 to (layerManager.count - 1) do
	(
		local layer = layerManager.getLayer layerIndex
		if layer != undefined then append layerNames layer.name
	)
	layerNames
)

fn PBD_GBufferNodesInLayer rootLayer =
(
	local matchingNodes = #()
	for node in objects where PBD_GBufferIsGeometry node do
	(
		local nodeLayer = node.layer
		if nodeLayer != undefined and PBD_GBufferLayerIsDescendant nodeLayer rootLayer then
			append matchingNodes node
	)
	matchingNodes
)

fn PBD_ExportGBufferMap rootLayer minimumId maximumId =
(
	if maxFilePath == "" then
	(
		messageBox "Save the current scene before exporting the G-buffer map." title:"G-buffer map export"
		return false
	)

	local outputPath = pathConfig.appendPath maxFilePath "cg-id-map.json"
	local outputStream = undefined
	try outputStream = createFile outputPath catch()
	if outputStream == undefined then
	(
		messageBox ("Could not create output file. Check that the scene folder is writable and that the file is not locked:\n" + outputPath) title:"G-buffer map export"
		return false
	)

	local exportedNames = #()
	local exportedIds = #()
	local matchingNodes = #()
	for node in (PBD_GBufferNodesInLayer rootLayer) do
	(
		local gBufferId = node.gbufferChannel as integer
		if gBufferId >= minimumId and gBufferId <= maximumId then
		(
			append matchingNodes node
			if (findItem exportedNames node.name) == 0 then
			(
				append exportedNames node.name
				append exportedIds gBufferId
			)
		)
	)

	local json = "{"
	for entryIndex = 1 to exportedNames.count do
	(
		json += "\"" + PBD_GBufferJsonEscape exportedNames[entryIndex] + "\":\""
		json += PBD_GBufferIdText exportedIds[entryIndex] + "\""
		if entryIndex < exportedNames.count then json += ","
	)
	json += "}"
	format "%" json to:outputStream
	close outputStream

	select matchingNodes
	format "Exported % unique object names to %\n" exportedNames.count outputPath
	messageBox ("Exported " + (exportedNames.count as string) + " object names to:\n" + outputPath) title:"G-buffer map export"
	true
)

rollout PBD_GBufferMapRollout "G-buffer ID map"
(
	dropDownList layerList "Layer:" items:(PBD_GBufferLayerNames()) width:260
	spinner minimumIdSpinner "Minimum ID:" range:[0, 65535, 0] type:#integer fieldwidth:70
	spinner maximumIdSpinner "Maximum ID:" range:[0, 65535, 65535] type:#integer fieldwidth:70
	button refreshButton "Refresh layers" width:120
	button exportButton "Select and export" width:120

	fn RefreshLayerList =
	(
		layerList.items = PBD_GBufferLayerNames()
		if layerList.items.count > 0 then layerList.selection = 1
	)

	on refreshButton pressed do RefreshLayerList()

	on exportButton pressed do
	(
		if layerList.selection == 0 then
		(
			messageBox "Select a layer first." title:"G-buffer map export"
		)
		else if minimumIdSpinner.value > maximumIdSpinner.value then
		(
			messageBox "The minimum ID must not be greater than the maximum ID." title:"G-buffer map export"
		)
		else
		(
			local rootLayer = layerManager.getLayerFromName layerList.selected
			if rootLayer == undefined then
				messageBox "The selected layer no longer exists. Refresh the layer list." title:"G-buffer map export"
			else
				PBD_ExportGBufferMap rootLayer minimumIdSpinner.value maximumIdSpinner.value
		)
	)
)

try (destroyDialog PBD_GBufferMapRollout) catch()
createDialog PBD_GBufferMapRollout width:290
