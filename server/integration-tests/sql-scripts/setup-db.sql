CREATE TABLE IF NOT EXISTS times
(
    id bigserial NOT NULL,
    client_sent bigint,
    client_sent_prec bigint NOT NULL,
    server_recv bigint,
    server_recv_prec bigint,
    server_sent bigint,
    server_sent_prec bigint,
    client_recv bigint,
    client_recv_prec bigint,
    CONSTRAINT times_pkey PRIMARY KEY (id),
    CONSTRAINT pk UNIQUE (id)
);


CREATE TABLE IF NOT EXISTS measurements
(
    id bigserial NOT NULL,
    ntp_server_ip inet,
    ntp_server_name text COLLATE pg_catalog."default",
    ntp_version smallint,
    ntp_server_ref_parent inet,
    ref_name text COLLATE pg_catalog."default",
    time_id bigint,
    time_offset double precision,
    rtt double precision,
    stratum integer,
    "precision" double precision,
    reachability text COLLATE pg_catalog."default",
    root_delay bigint,
    ntp_last_sync_time bigint,
    root_delay_prec bigint,
    ntp_last_sync_time_prec bigint,
    vantage_point_ip inet,
    CONSTRAINT measurements_pkey PRIMARY KEY (id),
    CONSTRAINT fk FOREIGN KEY (time_id)
        REFERENCES public.times (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
);