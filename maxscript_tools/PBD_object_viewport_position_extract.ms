/*
	Export positions of Point helpers, projected through the active camera.

	Edit these values before running the script.
*/
global PBD_ExportPointPositions
global PBD_ExportMatchingCameraStates

fn PBD_JsonEscape value =
(
	local result = value as string
	result = substituteString result "\\" "\\\\"
	result = substituteString result "\"" "\\\""
	result = substituteString result "\n" "\\n"
	result = substituteString result "\r" "\\r"
	result = substituteString result "\t" "\\t"
	result
)

fn PBD_JsonNumber value =
(
	/* MaxScript may use a comma as the decimal separator on some systems. */
	local result = value as string
	substituteString result "," "."
)

fn PBD_FrameKey value =
(
	local frameText = (value as integer) as string
	local isNegative = frameText[1] == "-"
	if isNegative then frameText = substring frameText 2 (frameText.count - 1)
	while frameText.count < 4 do frameText = "0" + frameText
	if isNegative then "-" + frameText else frameText
)

fn PBD_SafeFileName value =
(
	local result = value as string
	local backslashCharacter = bit.intAsChar 92
	local quoteCharacter = bit.intAsChar 34
	for badCharacter in #(backslashCharacter, "/", ":", "*", "?", quoteCharacter, "<", ">", "|") do
		result = substituteString result badCharacter "_"
	result
)

fn PBD_GetActiveCamera =
(
	local cameraNode = viewport.getCamera()
	if isValidNode cameraNode and PBD_IsCameraNode cameraNode then cameraNode else undefined
)

fn PBD_IsCameraNode node =
(
	if not isValidNode node then false
	else (isKindOf node Camera) or ((classOf node as string) == "VRayPhysicalCamera")
)

fn PBD_ProjectPoint worldPosition cameraNode imageAspect =
(
	/* 3ds Max cameras look down their local negative Z axis and Y is up. */
	local cameraPosition = worldPosition * (inverse cameraNode.transform)
	local depth = -cameraPosition.z

	if depth <= 0.0 then
	(
		undefined -- Behind the camera (or exactly on its plane).
	)
	else
	(
		local halfHorizontalAngle = cameraNode.fov * 0.5
		local horizontalScale = tan halfHorizontalAngle
		if horizontalScale == 0.0 then undefined
		else
		(
			local normalizedX = 0.5 + ((cameraPosition.x / depth) / (2.0 * horizontalScale))
			local normalizedY = 0.5 - (((cameraPosition.y / depth) * imageAspect) / (2.0 * horizontalScale))
			if normalizedX < 0.0 or normalizedX > 1.0 or normalizedY < 0.0 or normalizedY > 1.0 then
				undefined
			else
				#(normalizedX, normalizedY)
		)
	)
)

fn PBD_IsPointHelper node =
(
	/* The class test avoids including other helper objects. */
	(isKindOf node helper) and ((classOf node) == Point)
)

fn PBD_SceneStateValueName value =
(
	if isProperty value #name then value.name as string else value as string
)

fn PBD_RestoreLayerState stateName =
(
	local layerProperties = #{3}
	sceneStateMgr.restore stateName layerProperties
	true
)

fn PBD_ExportPointPositions \
	startFrame:rendStart \
	endFrame:rendEnd \
	cameraNode:undefined \
	outputDirectory:(getDir #scene) =
(
	if cameraNode == undefined then cameraNode = PBD_GetActiveCamera()
	if cameraNode == undefined then
	(
		messageBox "The active viewport is not looking through a camera." title:"Point position export"
		return false
	)

	if renderWidth <= 0 or renderHeight <= 0 then
	(
		messageBox "The render output size must be greater than zero." title:"Point position export"
		return false
	)

	if maxFilePath == "" then
	(
		messageBox "Save the current scene before exporting point positions." title:"Point position export"
		return false
	)

	local poiDirectory = pathConfig.appendPath maxFilePath "links"
	outputDirectory = pathConfig.appendPath poiDirectory (PBD_SafeFileName cameraNode.name)
	makeDir outputDirectory all:true
	local imageAspect = (renderWidth as float * renderPixelAspect) / renderHeight
	local originalFrame = sliderTime
	local frameEntries = #()

	try
	(
		with redraw on
		(
			for frameTime = startFrame to endFrame do
			(
				sliderTime = frameTime
				local objectsAtFrame = #()
				local matchingObjects = #()

				for node in objects where PBD_IsPointHelper node do
					append matchingObjects node
				select matchingObjects

				for node in matchingObjects do
				(
					local projectedPosition = PBD_ProjectPoint node.transform.pos cameraNode imageAspect
					if projectedPosition != undefined then
						append objectsAtFrame #(node.name, projectedPosition)
				)
				append frameEntries #(frameTime, objectsAtFrame)
			)
		)
	)
	catch
	(
		sliderTime = originalFrame
		throw
	)
	sliderTime = originalFrame

	local json = "{"
	for frameEntryIndex = 1 to frameEntries.count do
	(
		local frameEntry = frameEntries[frameEntryIndex]
		local frameNumber = ((frameEntry[1] as integer) / ticksPerFrame) as integer
		local frameKey = PBD_FrameKey frameNumber
		json += "\"" + frameKey + "\":["
		local objectsAtFrame = frameEntry[2]

		for objectIndex = 1 to objectsAtFrame.count do
		(
			local objectEntry = objectsAtFrame[objectIndex]
			json += "{\"objectName\":\"" + PBD_JsonEscape objectEntry[1] + "\","
			json += "\"position\":[" + PBD_JsonNumber objectEntry[2][1] + "," + PBD_JsonNumber objectEntry[2][2] + "]}"
			if objectIndex < objectsAtFrame.count then json += ","
		)
		json += "]"
		if frameEntryIndex < frameEntries.count then json += ","
	)
	json += "}"

	local outputFileName = (PBD_SafeFileName cameraNode.name) + "-links.json"
	local outputPath = pathConfig.appendPath outputDirectory outputFileName
	local outputStream = createFile outputPath
	if outputStream == undefined then
	(
		messageBox ("Could not create output file:\n" + outputPath) title:"Point position export"
		return false
	)
	format "%" json to:outputStream
	close outputStream

	format "Exported frames % through % to %\n" startFrame endFrame outputPath
	true
)

fn PBD_ExportMatchingCameraStates =
(
	local stateNames = #()
	local stateCount = 0
	if isProperty sceneStateMgr #numSceneStates then stateCount = sceneStateMgr.numSceneStates
	else if isProperty sceneStateMgr #getCount then stateCount = sceneStateMgr.getCount()

	if stateCount > 0 then
	(
		if isProperty sceneStateMgr #getSceneStateName then
		(
			for stateIndex = 1 to stateCount do
				append stateNames (PBD_SceneStateValueName (sceneStateMgr.getSceneStateName stateIndex))
		)
		else if isProperty sceneStateMgr #getSceneState then
		(
			for stateIndex = 1 to stateCount do
				append stateNames (PBD_SceneStateValueName (sceneStateMgr.getSceneState stateIndex))
		)
		else if isProperty sceneStateMgr #getName then
		(
			for stateIndex = 1 to stateCount do
				append stateNames (PBD_SceneStateValueName (sceneStateMgr.getName stateIndex))
		)
	)
	local matchingCameras = #()
	local reportEntries = #()
	local cameraCount = 0

	for cameraNode in objects where PBD_IsCameraNode cameraNode do
	(
		cameraCount += 1
		local matchingState = undefined
		for stateName in stateNames while matchingState == undefined do
		(
			if (stateName as string) == cameraNode.name then matchingState = stateName
		)

		if matchingState != undefined then append matchingCameras #(cameraNode, matchingState)
	)

	if matchingCameras.count == 0 then
	(
		format "PBD export summary: cameras=% states=% matches=0\n" cameraCount stateNames.count
		return false
	)

	local originalTime = sliderTime
	try
	(
		for cameraState in matchingCameras do
		(
			local cameraNode = cameraState[1]
			local stateName = cameraState[2]
			local exportSucceeded = false
			local failureReason = "export returned false"

			try
			(
				PBD_RestoreLayerState stateName
				viewport.setCamera cameraNode
				exportSucceeded = PBD_ExportPointPositions cameraNode:cameraNode
				if exportSucceeded then failureReason = ""
			)
			catch
			(
				exportSucceeded = false
				failureReason = getCurrentException() as string
			)

			append reportEntries #(cameraNode.name, stateName as string, exportSucceeded, failureReason)
		)
	)
	catch
	(
		sliderTime = originalTime
		throw
	)
	sliderTime = originalTime

	format "PBD export summary (% matches):\n" reportEntries.count
	for reportEntry in reportEntries do
	(
		format "  Camera: % | Scene state: % | Result: %" reportEntry[1] reportEntry[2] (if reportEntry[3] then "OK" else "FAILED")
		if not reportEntry[3] then format " | Reason: %" reportEntry[4]
		format "\n"
	)
	true
)

/* Example: export every camera whose name matches a scene state. */
PBD_ExportMatchingCameraStates()
