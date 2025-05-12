from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.app.api.routing import router
from server.app.db.connection import insert_measurement
from server.app.db.connection import get_measurements_timestamps_ip, get_measurements_timestamps_dn
from server.app.db.config import pool
from server.app.utils.perform_measurements import perform_ntp_measurement_ip
from server.app.utils.perform_measurements import human_date_to_ntp_precise_time
from server.app.utils.perform_measurements import perform_ntp_measurement_domain_name
from server.app.utils.validate import is_ip_address
from server.app.utils.validate import ensure_utc
from server.app.utils.validate import parse_ip
from datetime import datetime

app = FastAPI()
app.include_router(router)
"""
Creates a FastAPI application instance.
This instance is used to define all API endpoints and serve the application.
"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)



