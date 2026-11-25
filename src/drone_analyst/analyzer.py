from .models import Entity, Frame

COLORS = ("blue", "white", "black", "silver", "red")

VEHICLE_MODELS: tuple[tuple[str, str, str], ...] = (
    ("delivery van", "", "Delivery Van"),
    ("f150", "Ford", "F150"),
    ("truck", "", "Truck"),
    ("van", "", "Van"),
    ("car", "", "Car"),
)

VEHICLE_CATEGORIES: dict[str, tuple[str, ...]] = {
    "truck": ("F150", "Truck"),
    "van": ("Delivery Van", "Van"),
    "car": ("Car",),
}


def detect_color(text: str) -> str:
    lowered = text.lower()
    return next((color for color in COLORS if color in lowered), "")


def parse_entities(text: str) -> list[Entity]:
    lowered = text.lower()
    entities: list[Entity] = []
    if "person" in lowered:
        entities.append(Entity(kind="person", color="", make="", model=""))
    for token, make, model in VEHICLE_MODELS:
        if token in lowered:
            entities.append(
                Entity(
                    kind="vehicle",
                    color=detect_color(lowered),
                    make=make,
                    model=model,
                )
            )
            break
    return entities


def analyze_frame(frame: Frame) -> Frame:
    frame.entities = parse_entities(frame.description)
    return frame
