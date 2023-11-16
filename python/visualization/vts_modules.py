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
    Satellite.appendChild(Component)
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

    #     < SensorSatellite >
    #     < Sensor
    #     Name = "newSensor" >
    #     < SensorProp >
    #     < SensorElliptical
    #     HalfAngleX = "0.174532925199433"
    #     HalfAngleY = "0.174532925199433" / >
    #     < SensorGraphics
    #     Range = "10000"
    #     VolumeColor = "0.499992 1 0.651911"
    #     VolumeOpacity = "60" >
    #     < SensorContour >
    #     < LineStyle
    #     Color = "0 1 0.303838"
    #     Style = "SolidLine"
    #     Width = "1" / >
    #
    # < / SensorContour >
    # < SensorTrace
    # Duration = "0"
    # Opacity = "60" / >
    # < / SensorGraphics >
    # < / SensorProp >
    # < Geometry >
    # < Position >
    # < Value >
    # < Fixed
    # Data = "0 0 0" / >
    # < / Value >
    # < / Position >
    # < Orientation >
    # < Quaternion >
    # < Value >
    # < Fixed
    # Data = "1 0 0 0" / >
    # < / Value >
    # < / Quaternion >
    # < / Orientation >
    # < / Geometry >
    # < / Sensor >
    # < / SensorSatellite >

    # Automate this
    SensorSatellite = xml.createElement("SensorSatellite")
    Satellite.appendChild(SensorSatellite)
    Sensor = xml.createElement("Sensor")
    Sensor.setAttribute("Name", "newSensor")
    SensorSatellite.appendChild(Sensor)
    SensorProp = xml.createElement("SensorProp")
    Sensor.appendChild(SensorProp)
    SensorElliptical = xml.createElement("SensorElliptical")
    SensorElliptical.setAttribute("HalfAngleX", "0.174532925199433")




def generate_events(xml, project):
    Events = xml.createElement("Events")
    project.appendChild(Events)
    return Events


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
