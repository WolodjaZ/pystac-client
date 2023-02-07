from typing import Dict, Union, List, Any
from datetime import datetime

from shapely import geometry, box, intersects
from item_search import Datetime, BBox, Intersects, Query

def translate_op(operator):
    if operator == "eq":
        operator = "=="
    elif operator == "neq":
        operator = "!="
    elif operator == "gt":
        operator = ">"
    elif operator == "gte":
        operator = ">="
    elif operator == "lt":
        operator = "<"
    elif operator == "lte":
        operator = "<="
    else:
        raise ValueError(f"Operator {operator} not supported for type numerical")
    return operator

def intersects_datetime(
    query: Datetime,
    item: Union[datetime, List[datetime]],
) -> bool:
    """Returns True if the item intersects the given datetime range.

    Args:
        query: The datetime range to check.
        item: The item to check.

    Returns:
        True if the item intersects the given datetime range.
    """
    query_datetime = query.split("/")
    start_qdatetime = datetime.fromisoformat(query_datetime[0])
    end_qdatetime = datetime.fromisoformat(query_datetime[1])
    if isinstance(item, list):
        starti_datetime = item[0]
        endi_datetime = item[1]
    else:
        starti_datetime = item
        endi_datetime = item
    
    if start_qdatetime >= starti_datetime and start_qdatetime <= endi_datetime:
        return True
    elif end_qdatetime >= starti_datetime and end_qdatetime <= endi_datetime:
        return True
    
    return False

def intersects_bbox(
    query: BBox,
    item: BBox
) -> bool:
    """Returns True if the item intersects the given bbox.

    Args:
        query: The bbox to check.
        item: The item to check.

    Returns:
        True if the item intersects the given bbox.
    """
    query_box = box(*query)
    item_box = box(*item)
    return intersects(query_box, item_box)

def intersects_geometry(
    query: Intersects,
    item: Dict[str, Any]
) -> bool:
    """Returns True if the item intersects the given geometry.
    
    Args:
        geometry: The geometry to check.
        item: The item to check.
    Returns:
        True if the item intersects the given geometry.
    """
    guery_geometry = geometry.shape(query)
    item_geometry = geometry.shape(item)
    return intersects(guery_geometry, item_geometry)

def intersects_query(
    query: Query,
    item: Dict[str, str],
    type: str = "soft"
) -> bool:
    """Returns True if the item intersects the given query.
    
    Reference:
        https://github.com/radiantearth/stac-api-spec/tree/master/fragments/query

    Args:
        query: The query to check.
        item: The item to check.
        type: The type of query to check. Can be "hard" or "soft".
            "hard" returns false if query parameter don't exists in item.
            "soft" returns only false if query parameter not intersect with item,

    Returns:
        True if the item intersects the given query.
    """
    if type not in ["hard", "soft"]:
        raise ValueError(f"Invalid query type: {type}")
    
    for key, querry_value in query.items():
        if key not in item:
            if type == "hard":
                return False
            continue
        
        item_value = item[key]
        for ope, val in querry_value.items():
            if isinstance(val, str):
                if ope == "startsWith":
                    if not str(item_value).startswith(val):
                        return False
                elif ope == "endsWith":
                    if not str(item_value).endswith(val):
                        return False
                elif ope == "contains":
                    if not val in str(item_value):
                        return False
                else:
                    raise ValueError(f"Operator {ope} not supported for type str")
            elif isinstance(val, (int, float)):
                ope = translate_op(ope)
                expresion = f"{item_value} {ope} {val}"
                if not eval(expresion):
                    return False
            elif isinstance(val, list):
                if not item_value in val:
                    return False
            else:
                raise ValueError(f"type {type(val)} not supported")

    return True