from pydantic import BaseModel
from typing import List, Dict

from server.app.dtos.ProbeData import ServerLocation


class RipeMeasurementTriggerResponse(BaseModel):
    measurement_id: str
    vantage_point_ip: str
    vantage_point_location: ServerLocation
    status: str = "started"
    message: str = "You can fetch the result at /measurements/ripe/{measurement_id}"
