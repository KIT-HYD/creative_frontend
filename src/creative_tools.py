from metacatalog_api import models
from shapely.geometry import shape


def entryToBbox(entry: models.Metadata) -> tuple[float] | None:
    if entry.datasource.spatial_scale is None:
        return None

    geom = shape(entry.datasource.spatial_scale.extent.model_dump())
    
    # return like (minx, miny, maxx, maxy)
    return geom.bounds

def get_static_metadata() -> dict:
    # this could be repalced by an actual config loader
    return dict(
        keywordScheme="foobar",
        keywordURI="http://gofuckyourself.com"
    )

def get_mandatory_extra(entry: models.Metadata) -> tuple[dict, list[str]]:
    extra = dict()
    errors = []
    
    for detail in entry.details:
        if detail.key == "RADAR:funding":
            extra['funding'] = detail.value
            break
    
    if 'funding' not in extra:
        errors.append("Funding is missing")
    
    return extra, errors
    