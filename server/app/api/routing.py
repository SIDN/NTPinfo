from fastapi import HTTPException, APIRouter, Request, Depends

from datetime import datetime, timezone
from typing import Any, Optional, Generator
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from server.app.utils.location_resolver import get_country_for_ip, get_coordinates_for_ip
from server.app.utils.ip_utils import client_ip_fetch, get_server_ip_if_possible, get_server_ip_strict
from server.app.models.CustomError import DNSError, MeasurementQueryError
from server.app.utils.ip_utils import ip_to_str
from server.app.models.CustomError import InputError, RipeMeasurementError
from server.app.utils.ip_utils import get_server_ip
from server.app.db_config import get_db

from server.app.services.api_services import fetch_ripe_data
from server.app.services.api_services import perform_ripe_measurement
from server.app.rate_limiter import limiter
from server.app.dtos.MeasurementRequest import MeasurementRequest
from server.app.services.api_services import get_format, measure, fetch_historic_data_with_timestamps

router = APIRouter()


@router.get("/")
def read_root() -> dict[str, str]:
    """
    Root endpoint for basic service health check.

    Returns:
        dict: A simple JSON message {"Hello": "World"}
    """
    return {"Hello": "World"}


@router.post("/measurements/")
@limiter.limit("5/second")
async def read_data_measurement(payload: MeasurementRequest, request: Request,
                                session: Session = Depends(get_db)) -> JSONResponse:
    """
    Compute a live NTP measurement for a given server (IP or domain).

    This endpoint receives a JSON payload containing the server to be measured.
    It uses the `measure()` function to perform the NTP synchronization measurement,
    and formats the result using `get_format()`. User can choose whether they want to measure IPv4 of IPv6,
    but this will take effect only for domain names. If user inputs an IP, we will measure the type of that IP.

    This endpoint is also limited to 5 requests per minute to prevent abuse and reduce server load.

    Args:
        payload (MeasurementRequest): A Pydantic model containing:
            - server (str): IP address (IPv4/IPv6) or domain name of the NTP server.
            - ipv6_measurement (bool): True if the type of IPs that we want to measure is IPv6. False otherwise.
        request (Request): The Request object that gives you the IP of the client.
        session (Session): The currently active database session.

    Returns:
        dict: On success, returns {"measurement": <formatted_measurement_dict>}.
              On failure, returns {"Error": "Could not perform measurement, DNS or IP not reachable."}

    Raises:
        HTTPException:
            - 400 If the `server` field is empty or no response
            - 503 If we could not get client IP address or our server's IP address.

    """
    server = payload.server
    wanted_ip_type = 6 if payload.ipv6_measurement else 4
    if len(server) == 0:
        raise HTTPException(status_code=400, detail="Either 'ip' or 'dn' must be provided.")
    client_ip: Optional[str] = client_ip_fetch(request=request)

    this_server_ip_strict = get_server_ip_strict(wanted_ip_type)
    if this_server_ip_strict is None: # which means we cannot perform this type of NTP measurements from our server
        raise HTTPException(status_code=422, detail=f"Our server cannot perform IPv{wanted_ip_type} measurements currently. Try the other IP type.")
    try:
        response = measure(server, wanted_ip_type, session, client_ip)
        # print(response)
        if response is not None:
            new_format = []
            for r in response:
                result, jitter, nr_jitter_measurements = r
                new_format.append(get_format(result, jitter, nr_jitter_measurements))
            return JSONResponse(
                status_code=200,
                content={
                    "measurement": new_format
                }
            )
        else:
            raise HTTPException(status_code=400, detail="Server is not reachable.")
    except HTTPException as e:
        print(e)
        raise e
    except DNSError as e:
        print(e)
        raise HTTPException(status_code=422, detail="Domain name cannot be resolved.")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}.")


@router.get("/measurements/history/")
@limiter.limit("5/second")
async def read_historic_data_time(server: str,
                                  start: datetime, end: datetime, request: Request,
                                  session: Session = Depends(get_db)) -> JSONResponse:
    """
    Retrieve historic NTP measurements for a given server and optional time range.

    This endpoint fetches past measurement data for the specified server using the
    `fetch_historic_data_with_timestamps()` function. It can optionally filter results
    based on a time range (start and end datetime).

    This endpoint is also limited to 5 requests per minute to prevent abuse and reduce server load.

    Args:
        server (str): IP address or domain name of the NTP server.
        start (datetime, optional): Start timestamp for data filtering.
        end (datetime, optional): End timestamp for data filtering.
        request (Request): Request object for making the limiter work
        session (Session): The currently active database session.

    Returns:
        JSONResponse: A json response containing a list of formatted measurements under "measurements".

    Raises:
        HTTPException:
            Raises:
        HTTPException:
            - 400: If `server` parameter is empty, or the start and end dates are badly formatted (e.g., `start >= end`, `end` in future).
            - 500: If there's an internal server error, such as a database access issue (`MeasurementQueryError`) or any other unexpected server-side exception.
    """
    if len(server) == 0:
        raise HTTPException(status_code=400, detail="Either 'ip' or 'domain name' must be provided")

    if start >= end:
        raise HTTPException(status_code=400, detail="'start' must be earlier than 'end'")

    if end > datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="'end' cannot be in the future")

    # utc_time_from_9am = datetime(2025, 5, 7, 7, 0, tzinfo=timezone.utc)
    # current_utc_time = datetime(2025, 5, 7, 11, 15, tzinfo=timezone.utc)
    #
    # start_test = utc_time_from_9am
    # end_test = current_utc_time
    try:
        result = fetch_historic_data_with_timestamps(server, start, end, session)
        formatted_results = [get_format(entry, nr_jitter_measurements=0) for entry in result]
        return JSONResponse(
            status_code=200,
            content={
                "measurements": formatted_results
            }
        )
    except MeasurementQueryError as e:
        raise HTTPException(status_code=500, detail=f"There was an error with accessing the database: {str(e)}.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sever error: {str(e)}.")


@router.post("/measurements/ripe/trigger/")
@limiter.limit("5/second")
async def trigger_ripe_measurement(payload: MeasurementRequest, request: Request) -> JSONResponse:
    """
    Trigger a RIPE Atlas NTP measurement for a specified server.

    This endpoint initiates a RIPE Atlas measurement for the given NTP server
    (IP address or domain name) provided in the payload. Once the measurement
    is triggered, it returns a measurement ID which can later be used to fetch
    the result using the `/measurements/ripe/{measurement_id}` endpoint.

    This endpoint is also limited to 5 requests per minute to prevent abuse and reduce server load.

    Args:
        payload (MeasurementRequest): A Pydantic model that includes:
            - server (str): The IP address or domain name of the target server
            - ipv6_measurement (bool): True if the type of IPs that we want to measure is IPv6. False otherwise.
        request (Request): The FastAPI request object, used to extract the client IP address

    Returns:
        JSONResponse: A json response containing:
            - measurement_id (str): The ID of the triggered RIPE measurement
            - status (str): Status message ("started")
            - message (str): Instructions on how to retrieve the result
            - ip_list (list[str]): List of ips for ntp server

    Raises:
        HTTPException:
            - 400: If the `server` field is empty
            - 500: If the RIPE measurement could not be initiated
            - 502: If the RIPE measurement was initiated but failed
            - 503: If we could not get client IP address or our server's IP address
    """
    server = payload.server
    wanted_ip_type = 6 if payload.ipv6_measurement else 4
    if len(server) == 0:
        raise HTTPException(status_code=400, detail="Either 'ip' or 'dn' must be provided")

    client_ip: Optional[str] = client_ip_fetch(request=request)
    try:
        measurement_id = perform_ripe_measurement(server, client_ip=client_ip, wanted_ip_type=wanted_ip_type)
        this_server_ip = get_server_ip_if_possible(wanted_ip_type) # this does not affect the measurement
        return JSONResponse(
            status_code=200,
            content={
                "measurement_id": measurement_id,
                "vantage_point_ip": ip_to_str(this_server_ip),
                "vantage_point_location": {
                    "country_code": get_country_for_ip(ip_to_str(this_server_ip)),
                    "coordinates": get_coordinates_for_ip(ip_to_str(this_server_ip))
                },
                "status": "started",
                "message": "You can fetch the result at /measurements/ripe/{measurement_id}",
            }
        )
    except InputError as e:
        print(e)
        raise HTTPException(status_code=400,
                            detail=f"Input parameter is invalid. Failed to initiate measurement: {str(e)}")
    except RipeMeasurementError as e:
        print(e)
        raise HTTPException(status_code=502, detail=f"Ripe measurement initiated, but it failed: {str(e)}")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Failed to initiate measurement: {str(e)}")


@router.get("/measurements/ripe/{measurement_id}")
@limiter.limit("5/second")
async def get_ripe_measurement_result(measurement_id: str, request: Request) -> JSONResponse:
    """
    Retrieve the results of a previously triggered RIPE Atlas measurement.

    This endpoint checks the RIPE Atlas API for a given measurement ID. It determines
    if the measurement is complete (all probes have been scheduled) and returns
    the data accordingly. If the results are not yet ready, it informs the client
    that the measurement is still pending.

    This endpoint is also limited to 5 requests per minute to prevent abuse and reduce server load.

    Args:
        measurement_id (str): The ID of the RIPE measurement to fetch
        request (Request): The FastAPI Request object (used for rate limiting)

    Returns:
        dict[str, Any]: A dictionary with the status and measurement results:
            - If complete: {"status": "complete", "results": <ripe_data>}
            - If pending: {"status": "pending", "message": "..."}
            - If partial results received: {"status": "partial_results", "results": <ripe_data>}
    Raises:
        HTTPException:
            - 500: There is an error with processing.
            - 405: If fetching the measurement did not work.
    Notes:
        - A result is only marked "complete" when all requested probes have been scheduled
    """
    try:
        ripe_measurement_result, status = fetch_ripe_data(measurement_id=measurement_id)
        if not ripe_measurement_result:
            return JSONResponse(status_code=202, content="Measurement is still being processed.")
        if status == "Complete":
            return JSONResponse(
                status_code=200,
                content={
                    "status": "complete",
                    "message": "Measurement has been completed.",
                    "results": ripe_measurement_result
                }
            )

        if status == "Ongoing":
            return JSONResponse(
                status_code=206,
                content={
                    "status": "partial_results",
                    "message": "Measurement is still in progress. These are partial results.",
                    "results": ripe_measurement_result
                }
            )
        return JSONResponse(
            status_code=504,
            content={
                "status": "timeout",
                "message": "RIPE data likely completed but incomplete probe responses."
            }
        )
    except RipeMeasurementError as e:
        print(e)
        raise HTTPException(status_code=405, detail=f"RIPE call failed: {str(e)}. Try again later!")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Sever error: {str(e)}.")
