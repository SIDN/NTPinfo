import psycopg2
from server.app.db.config import DB_CONFIG
from server.app.models.NtpMeasurement import NtpMeasurement


def insert_measurement(measurement : NtpMeasurement) :

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO times (
            client_sent, client_sent_prec,
            server_recv, server_recv_prec,
            server_sent, server_sent_prec,
            client_recv, client_recv_prec
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        measurement.timestamps.client_sent_time.seconds, measurement.timestamps.client_sent_time.fraction,
        measurement.timestamps.server_recv_time.seconds, measurement.timestamps.server_recv_time.fraction,
        measurement.timestamps.server_sent_time.seconds, measurement.timestamps.server_sent_time.fraction,
        measurement.timestamps.client_recv_time.seconds, measurement.timestamps.client_recv_time.fraction
    ))

    time_id = cur.fetchone()[0]
    print(time_id)

    cur.execute("""
        INSERT INTO measurements(
            ntp_server_ip, ntp_server_name,
            ntp_version, ntp_server_ref_parent,
            ref_name, time_id,
             "offset", delay,
            stratum, precision,
            reachability, 
            root_delay,
            ntp_last_sync_time,
            root_delay_prec,
            ntp_last_sync_time_prec
        )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        str(measurement.server_info.ntp_server_ip), measurement.server_info.ntp_server_name,
        measurement.server_info.ntp_version, str(measurement.server_info.ntp_server_ref_parent_ip),
        measurement.server_info.ref_name, time_id,
        measurement.main_details.offset, measurement.main_details.delay,
        measurement.main_details.stratum, measurement.main_details.precision,
        measurement.main_details.reachability,
        measurement.extra_details.root_delay.seconds, measurement.extra_details.ntp_last_sync_time.seconds,
        measurement.extra_details.root_delay.fraction, measurement.extra_details.ntp_last_sync_time.fraction
    ))

    conn.commit()
    cur.close()
    conn.close()


