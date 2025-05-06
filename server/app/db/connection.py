from app.models.NtpMeasurement import NtpMeasurement

# inserts measurements in the database
def insert_measurement(measurement : NtpMeasurement, pool) :

    # uses a connection pool because connecting everytime
    # to the database is inefficient and can quickly exhaust resource
    with pool.connection() as conn :
        # if anything fails inside the transaction() block, it rolls back.
        # otherwise, it commits when the block exits cleanly.
        with conn.transaction() :
            with conn.cursor() as cur :

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

                # used because we have it as a foreign key in the measurements table
                time_id = cur.fetchone()[0]

                cur.execute("""
                    INSERT INTO measurements(
                        ntp_server_ip, ntp_server_name,
                        ntp_version, ntp_server_ref_parent,
                        ref_name, time_id,
                        time_offset, delay,
                        stratum, precision,
                        reachability, 
                        root_delay,
                        ntp_last_sync_time,
                        root_delay_prec,
                        ntp_last_sync_time_prec
                    )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    measurement.server_info.ntp_server_ip, measurement.server_info.ntp_server_name,
                    measurement.server_info.ntp_version, measurement.server_info.ntp_server_ref_parent_ip,
                    measurement.server_info.ref_name, time_id,
                    measurement.main_details.offset, measurement.main_details.delay,
                    measurement.main_details.stratum, measurement.main_details.precision,
                    measurement.main_details.reachability,
                    measurement.extra_details.root_delay.seconds, measurement.extra_details.ntp_last_sync_time.seconds,
                    measurement.extra_details.root_delay.fraction, measurement.extra_details.ntp_last_sync_time.fraction
                ))


# get all the measurements in the database
def get_all_measurements(pool) :
    with pool.connection() as conn :
        # if anything fails inside the transaction() block, it rolls back.
        # otherwise, it commits when the block exits cleanly.
        with conn.transaction() :
            with conn.cursor() as cur :
                cur.execute("""
                    SELECT *
                    FROM measurements m JOIN times t ON m.time_id = t.id
                """)
                return cur.fetchall()
