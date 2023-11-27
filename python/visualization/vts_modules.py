from xml.dom import minidom
from useful_functions.get_input_data import get_spacecraft

tolosat_specs = get_spacecraft("Tolosat")
iridium_specs = get_spacecraft("Iridium")
gps_specs = get_spacecraft("GPS")

iridium_antenna = iridium_specs["antenna_half_angle"]


def create_document():
    return minidom.Document()


def create_project(xml):
    project = xml.createElement("Project")
    project.setAttribute("Revision", "9032")
    xml.appendChild(project)
    return project


def set_start_end(xml, project, start_date_time, end_date_time):
    General = xml.createElement("General")
    General.setAttribute("Name", "")
    General.setAttribute("StartDateTime", start_date_time)
    General.setAttribute("EndDateTime", end_date_time)
    project.appendChild(General)


def generate_metadata(xml, project, description):
    MetaData = xml.createElement("MetaData")
    project.appendChild(MetaData)
    Description = xml.createElement("Description")
    DescriptionText = xml.createTextNode(description)
    Description.appendChild(DescriptionText)
    MetaData.appendChild(Description)


def generate_start_options(xml, project):
    StartOptions = xml.createElement("StartOptions")
    StartOptions.setAttribute("TimeRatio", "1")
    StartOptions.setAttribute("UseStateTimeRatio", "0")
    StartOptions.setAttribute("SysTimeSynced", "0")
    StartOptions.setAttribute("Paused", "0")
    StartOptions.setAttribute("Looped", "0")
    StartOptions.setAttribute("Minimized", "0")
    StartOptions.setAttribute("Hidden", "0")
    StartOptions.setAttribute("AutoClosed", "0")
    project.appendChild(StartOptions)


def generate_timeshifting(xml, project):
    Timeshifting = xml.createElement("Timeshifting")
    Timeshifting.setAttribute("Enabled", "0")
    project.appendChild(Timeshifting)


def generate_timeline_options(xml, project):
    TimelineOptions = xml.createElement("TimelineOptions")
    TimelineOptions.setAttribute("ProjectLocked", "1")
    TimelineOptions.setAttribute("CursorLocked", "0")
    TimelineOptions.setAttribute("CursorRatio", "0")
    TimelineOptions.setAttribute("ViewStart", "33282 0.000000")
    TimelineOptions.setAttribute("ViewSpan", "0")
    TimelineOptions.setAttribute("DateFormat", "ISODate")
    TimelineOptions.setAttribute("NoBadgeFiltered", "0")
    TimelineOptions.setAttribute("BadgeFiltered", "")
    project.appendChild(TimelineOptions)


def generate_sky(xml, project):
    Sky = xml.createElement("Sky")
    project.appendChild(Sky)
    Sun = xml.createElement("Sun")
    Sky.appendChild(Sun)
    Prop2d = xml.createElement("Prop2d")
    Sun.appendChild(Prop2d)
    Icon = xml.createElement("Icon")
    Icon.setAttribute("Anchor", "CENTER")
    Icon.setAttribute("Size", "MEDIUM")
    Icon.setAttribute("Opacity", "100")
    Prop2d.appendChild(Icon)
    Font = xml.createElement("Font")
    Font.setAttribute("Size", "8")
    Font.setAttribute("Color", "1 1 1")
    Icon.appendChild(Font)
    ImageLayer = xml.createElement("ImageLayer")
    ImageLayer.setAttribute("Type", "Default")
    Icon.appendChild(ImageLayer)
    Track = xml.createElement("Track")
    Sun.appendChild(Track)
    LineStyle = xml.createElement("LineStyle")
    LineStyle.setAttribute("Color", "0.862745 0.862745 0")
    LineStyle.setAttribute("Style", "SolidLine")
    LineStyle.setAttribute("Width", "1")
    Track.appendChild(LineStyle)
    VisibilityCircle = xml.createElement("VisibilityCircle")
    Sun.appendChild(VisibilityCircle)
    LineStyle = xml.createElement("LineStyle")
    LineStyle.setAttribute("Color", "0.501961 0.501961 0")
    LineStyle.setAttribute("Style", "SolidLine")
    LineStyle.setAttribute("Width", "1")
    VisibilityCircle.appendChild(LineStyle)
    FillStyle = xml.createElement("FillStyle")
    FillStyle.setAttribute("Color", "0 0 0")
    FillStyle.setAttribute("Opacity", "50")
    VisibilityCircle.appendChild(FillStyle)
    StarCatalog = xml.createElement("StarCatalog")
    StarCatalog.setAttribute("CatalogMode", "Builtin")
    Sky.appendChild(StarCatalog)
    Track = xml.createElement("Track")
    StarCatalog.appendChild(Track)
    LineStyle = xml.createElement("LineStyle")
    LineStyle.setAttribute("Color", "1 1 1")
    LineStyle.setAttribute("Style", "DotLine")
    LineStyle.setAttribute("Width", "1")
    Track.appendChild(LineStyle)


def generate_apps(xml, project):
    ToBeUsedApps = xml.createElement("ToBeUsedApps")
    project.appendChild(ToBeUsedApps)
    Application = xml.createElement("Application")
    Application.setAttribute("Name", "SurfaceView")
    Application.setAttribute("Id", "0")
    Application.setAttribute("Label", "")
    Application.setAttribute("AutoStarted", "1")
    ToBeUsedApps.appendChild(Application)
    Application = xml.createElement("Application")
    Application.setAttribute("Name", "Celestia")
    Application.setAttribute("Id", "1")
    Application.setAttribute("Label", "")
    Application.setAttribute("AutoStarted", "1")
    ToBeUsedApps.appendChild(Application)


def generate_entities(xml, project):
    Entities = xml.createElement("Entities")
    project.appendChild(Entities)
    return Entities


def add_earth(xml, entities):
    Body = xml.createElement("Body")
    Body.setAttribute("Name", "Earth")
    Body.setAttribute("ParentPath", "Sol")
    entities.appendChild(Body)
    Prop2d = xml.createElement("Prop2d")
    Body.appendChild(Prop2d)
    Icon = xml.createElement("Icon")
    Icon.setAttribute("Anchor", "CENTER")
    Icon.setAttribute("Size", "MEDIUM")
    Icon.setAttribute("Opacity", "100")
    Prop2d.appendChild(Icon)
    Font = xml.createElement("Font")
    Font.setAttribute("Size", "8")
    Font.setAttribute("Color", "1 1 1")
    Icon.appendChild(Font)
    ImageLayer = xml.createElement("ImageLayer")
    ImageLayer.setAttribute("Type", "Default")
    Icon.appendChild(ImageLayer)
    Track = xml.createElement("Track")
    Body.appendChild(Track)
    LineStyle = xml.createElement("LineStyle")
    LineStyle.setAttribute("Color", "0 0.212329 1")
    LineStyle.setAttribute("Style", "SolidLine")
    LineStyle.setAttribute("Width", "1")
    Track.appendChild(LineStyle)
    VisibilityCircle = xml.createElement("VisibilityCircle")
    Body.appendChild(VisibilityCircle)
    LineStyle = xml.createElement("LineStyle")
    LineStyle.setAttribute("Color", "0.838834 1 0")
    LineStyle.setAttribute("Style", "SolidLine")
    LineStyle.setAttribute("Width", "1")
    VisibilityCircle.appendChild(LineStyle)
    FillStyle = xml.createElement("FillStyle")
    FillStyle.setAttribute("Color", "0.919417 1 0.499992")
    FillStyle.setAttribute("Opacity", "60")
    VisibilityCircle.appendChild(FillStyle)
    EphemerisMode = xml.createElement("EphemerisMode")
    EphemerisMode.setAttribute("Mode", "Default")
    Body.appendChild(EphemerisMode)
    Layers = xml.createElement("Layers")
    Body.appendChild(Layers)
    BuiltinLayer = xml.createElement("BuiltinLayer")
    BuiltinLayer.setAttribute("Name", "defaultLayer")
    Layers.appendChild(BuiltinLayer)

def add_sensor(xml, name: str, quaternion: str):
    # create sensor satellite
    SensorSatellite = xml.createElement("SensorSatellite")

    # create sensor
    Sensor = xml.createElement("Sensor")
    Sensor.setAttribute("Name", name)

    # create sensor properties
    SensorProp = xml.createElement("SensorProp")

    # create sensor propereties - elliptical
    SensorElliptical = xml.createElement("SensorElliptical")
    SensorElliptical.setAttribute("HalfAngleX", "0.174532925199433")
    SensorElliptical.setAttribute("HalfAngleY", "0.174532925199433")

    # create sensor properties - graphics
    SensorGraphics = xml.createElement("SensorGraphics")
    SensorGraphics.setAttribute("Range", "10000")
    SensorGraphics.setAttribute("VolumeColor", "1 0.499992 0.611658")
    SensorGraphics.setAttribute("VolumeOpacity", "60")

    # create sensor properties - graphics - contour
    SensorContour = xml.createElement("SensorContour")

    # create sensor properties - graphics - contour - linestyle
    LineStyle = xml.createElement("LineStyle")
    LineStyle.setAttribute("Color", "1 0 0.223331")
    LineStyle.setAttribute("Style", "SolidLine")
    LineStyle.setAttribute("Width", "1")

    # create sensor properties - graphics - trace
    SensorTrace = xml.createElement("SensorTrace")
    SensorTrace.setAttribute("Duration", "0")
    SensorTrace.setAttribute("Opacity", "60")

    # create geometry
    Geometry = xml.createElement("Geometry")

    # create geometry - position
    Position = xml.createElement("Position")
    Value_Position = xml.createElement("Value")
    Fixed_Position = xml.createElement("Fixed")
    Fixed_Position.setAttribute("Data", "0 0 0")

    # create geometry - orientation
    Orientation = xml.createElement("Orientation")
    Quaternion = xml.createElement("Quaternion")
    Value_Quaternion = xml.createElement("Value")
    Fixed_Quaternion = xml.createElement("Fixed")
    Fixed_Quaternion.setAttribute("Data", quaternion)

    # append everything
    SensorSatellite.appendChild(Sensor)

    SensorProp.appendChild(SensorElliptical)
    SensorContour.appendChild(LineStyle)
    SensorGraphics.appendChild(SensorContour)
    SensorGraphics.appendChild(SensorTrace)
    SensorProp.appendChild(SensorGraphics)
    Sensor.appendChild(SensorProp)

    Value_Position.appendChild(Fixed_Position)
    Position.appendChild(Value_Position)
    Geometry.appendChild(Position)

    Value_Quaternion.appendChild(Fixed_Quaternion)
    Quaternion.appendChild(Value_Quaternion)
    Orientation.appendChild(Quaternion)
    Geometry.appendChild(Orientation)

    Sensor.appendChild(Geometry)

    return SensorSatellite

def add_satellite(xml, entities, name, oem_file, aem_file, model_name=None):
    Satellite = xml.createElement("Satellite")
    Satellite.setAttribute("Name", name)
    Satellite.setAttribute("ParentPath", "Sol/Earth")
    entities.appendChild(Satellite)
    Track = xml.createElement("Track")
    Satellite.appendChild(Track)
    LineStyle = xml.createElement("LineStyle")
    if name == "TOLOSAT":
        LineStyle.setAttribute("Color", "0.459159 1 0")
        LineStyle.setAttribute("Style", "SolidLine")
    else:
        LineStyle.setAttribute("Color", "1 1 0")
        LineStyle.setAttribute("Style", "DotLine")
    LineStyle.setAttribute("Width", "1")
    Track.appendChild(LineStyle)
    Prop2d = xml.createElement("Prop2d")
    Satellite.appendChild(Prop2d)
    Icon = xml.createElement("Icon")
    Icon.setAttribute("Anchor", "CENTER")
    Icon.setAttribute("Size", "MEDIUM")
    Icon.setAttribute("Opacity", "100")
    Prop2d.appendChild(Icon)
    Font = xml.createElement("Font")
    if name == "TOLOSAT":
        Font.setAttribute("Size", "10")
        Font.setAttribute("Color", "1 1 0")
    else:
        Font.setAttribute("Size", "6")
        Font.setAttribute("Color", "1 1 1")
    Icon.appendChild(Font)
    ImageLayer = xml.createElement("ImageLayer")
    ImageLayer.setAttribute("Type", "Default")
    Icon.appendChild(ImageLayer)
    VisibilityCircle = xml.createElement("VisibilityCircle")
    Satellite.appendChild(VisibilityCircle)
    LineStyle = xml.createElement("LineStyle")
    LineStyle.setAttribute("Color", "0 1 0.498329")
    LineStyle.setAttribute("Style", "SolidLine")
    LineStyle.setAttribute("Width", "1")
    VisibilityCircle.appendChild(LineStyle)
    FillStyle = xml.createElement("FillStyle")
    FillStyle.setAttribute("Color", "0.499992 1 0.749157")
    FillStyle.setAttribute("Opacity", "60")
    VisibilityCircle.appendChild(FillStyle)
    EclipseCircle = xml.createElement("EclipseCircle")
    Satellite.appendChild(EclipseCircle)
    LineStyle = xml.createElement("LineStyle")
    LineStyle.setAttribute("Color", "1 0.167834 0")
    LineStyle.setAttribute("Style", "DashLine")
    LineStyle.setAttribute("Width", "1")
    EclipseCircle.appendChild(LineStyle)
    FillStyle = xml.createElement("FillStyle")
    FillStyle.setAttribute("Color", "1 0.583917 0.499992")
    FillStyle.setAttribute("Opacity", "60")
    EclipseCircle.appendChild(FillStyle)
    Component = xml.createElement("Component")
    Component.setAttribute("Name", name)
    if model_name is not None:
        Graphics3d = xml.createElement("Graphics3d")
        Component.appendChild(Graphics3d)
        File3ds = xml.createElement("File3ds")
        File3ds.setAttribute("Name", model_name)
        Graphics3d.appendChild(File3ds)
        Radius = xml.createElement("Radius")
        Radius.setAttribute("Value", "1")
        Graphics3d.appendChild(Radius)
        LightSensitive = xml.createElement("LightSensitive")
        LightSensitive.setAttribute("Value", "1")
        Graphics3d.appendChild(LightSensitive)
        Use3dsCoords = xml.createElement("Use3dsCoords")
        Use3dsCoords.setAttribute("Value", "0")
        Use3dsCoords.setAttribute("MeshScale", "1")
        Graphics3d.appendChild(Use3dsCoords)
        AxesPosition = xml.createElement("AxesPosition")
        AxesPosition.setAttribute("Value", "1")
        Graphics3d.appendChild(AxesPosition)
        RotationCenter = xml.createElement("RotationCenter")
        RotationCenter.setAttribute("X", "0")
        RotationCenter.setAttribute("Y", "0")
        RotationCenter.setAttribute("Z", "0")
        Graphics3d.appendChild(RotationCenter)

    Geometry = xml.createElement("Geometry")
    Component.appendChild(Geometry)

    Position = xml.createElement("Position")
    Geometry.appendChild(Position)

    Value = xml.createElement("Value")
    Position.appendChild(Value)

    File = xml.createElement("File")
    File.setAttribute("Name", oem_file)
    Value.appendChild(File)
    Orientation = xml.createElement("Orientation")
    Geometry.appendChild(Orientation)

    Quaternion = xml.createElement("Quaternion")
    Orientation.appendChild(Quaternion)
    Value = xml.createElement("Value")
    Quaternion.appendChild(Value)
    File = xml.createElement("File")
    File.setAttribute("Name", aem_file)
    Value.appendChild(File)

    # ========== Sensor 1 ==========
    Component.appendChild(add_sensor(xml, 'Sensor1', '1 0 0 0'))

    # add default events
    Events = xml.createElement("Events")
    Satellite.appendChild(Events)

    # ========== Sensor 2 : Antenna 1 ==========
    Component.appendChild(add_sensor(xml, 'Sensor2', '1 1 0 0'))

    # add default events
    Events = xml.createElement("Events")
    Satellite.appendChild(Events)

    # ========== Sensor 3 : Antenna 2 ==========
    Component.appendChild(add_sensor(xml, 'Sensor3', '1 0 1 0'))

    # add default events
    Events = xml.createElement("Events")
    Satellite.appendChild(Events)

    # ========== Sensor 4 : Antenna 3 ==========
    Component.appendChild(add_sensor(xml, 'Sensor4', '1 -1 0 0'))

    # add default events
    Events = xml.createElement("Events")
    Satellite.appendChild(Events)

    # ========== Sensor 5 : Antenna 4 ==========
    Component.appendChild(add_sensor(xml, 'Sensor5', '1 0 -1 0'))

    # add default events
    Events = xml.createElement("Events")
    Satellite.appendChild(Events)

    # Final step : add component with all sensors to the satellite
    Satellite.appendChild(Component)

def generate_window(xml, name, id):
    app = xml.createElement("Application")
    app.setAttribute("Name", name)
    app.setAttribute("Id", id)
    app.setAttribute("Label", "")
    app.setAttribute("AutoStarted", "1")
    return app
def generate_windows(xml):
    apps = xml.createElement("ToBeUsedApps")

    app0 = generate_window(xml, "SurfaceView", 0)
    app1 = generate_window(xml, "Celestia", 1)
    app2 = generate_window(xml, "SensorView", 2)
    app3 = generate_window(xml, "InfoBox", 3)
    app4 = generate_window(xml, "NadirView", 4)

    apps.apendChild(app0)
    apps.apendChild(app1)
    apps.apendChild(app2)
    apps.apendChild(app3)
    apps.apendChild(app4)

def generate_events(xml, project):
    Events = xml.createElement("Events")
    project.appendChild(Events)
    return Events

# TO REDO DYNAMICALLY
#  <States>
#   <Instant Time="33282 0" TimeRatio="1" Label="Initial state">
#    <AppState Id="0">
#     <Command Str="CMD PROP WindowGeometry 0 0 960 516"/>
#    </AppState>
#    <AppState Id="1">
#     <Command Str="CMD PROP WindowGeometry 0 516 960 516"/>
#     <Command Str="CMD STRUCT LabelVisible &quot;Sol/Earth/TOLOSAT&quot; false"/>
#     <Command Str="CMD STRUCT FrameAxesVisible &quot;Sol/Earth/TOLOSAT&quot; false"/>
#     <Command Str="CMD STRUCT SunDirectionVisible &quot;Sol/Earth/TOLOSAT&quot; true"/>
#    </AppState>
#    <AppState Id="2">
#     <Command Str="CMD PROP WindowGeometry 960 103 960 412"/>
#    </AppState>
#    <AppState Id="3">
#     <Command Str="CMD PROP WindowGeometry 960 0 960 103"/>
#    </AppState>
#    <AppState Id="4">
#     <Command Str="CMD PROP WindowGeometry 960 516 960 516"/>
#    </AppState>
#   </Instant>
#  </States>
def generate_states(xml, project, spacecraft_names):
    States = xml.createElement("States")
    project.appendChild(States)
    Instant = xml.createElement("Instant")
    Instant.setAttribute("Time", "33282 0")
    Instant.setAttribute("TimeRatio", "1")
    Instant.setAttribute("Label", "Initial state")
    States.appendChild(Instant)
    AppState = xml.createElement("AppState")
    AppState.setAttribute("Id", "0")
    Instant.appendChild(AppState)
    Command = xml.createElement("Command")
    Command.setAttribute("Str", "CMD PROP WindowGeometry 0 0 1280 971")
    AppState.appendChild(Command)
    for spacecraft_name in spacecraft_names:
        if spacecraft_name == "TOLOSAT":
            continue
        Command = xml.createElement("Command")
        Command.setAttribute(
            "Str", f'CMD STRUCT TrackVisible "Sol/Earth/{spacecraft_name}" false'
        )
        AppState.appendChild(Command)
    AppState = xml.createElement("AppState")
    AppState.setAttribute("Id", "1")
    Instant.appendChild(AppState)
    Command = xml.createElement("Command")
    Command.setAttribute("Str", "CMD PROP WindowGeometry 0 0 1280 971")
    AppState.appendChild(Command)
    Command = xml.createElement("Command")
    Command.setAttribute("Str", 'CMD STRUCT LabelVisible "Sol/Earth/TOLOSAT" false')
    AppState.appendChild(Command)
    Command = xml.createElement("Command")
    Command.setAttribute("Str", 'CMD STRUCT FrameAxesVisible "Sol/Earth/TOLOSAT" false')
    AppState.appendChild(Command)
    Command = xml.createElement("Command")
    Command.setAttribute(
        "Str", 'CMD STRUCT SunDirectionVisible "Sol/Earth/TOLOSAT" true'
    )
    AppState.appendChild(Command)


def write_xml(xml, file_name):
    xml_str = xml.toprettyxml(indent=" ", encoding="UTF-8").decode("utf-8")
    with open(file_name, "w") as f:
        f.write(xml_str)
