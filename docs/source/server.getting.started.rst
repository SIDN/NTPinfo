Server Setup and Running
========================

To set up and run the backend server, follow these steps:

1. Create a virtual environment
-------------------------------

.. code-block:: bash

   python -m venv venv

Then activate the virtual environment:

- On **macOS/Linux**:

  .. code-block:: bash

     source venv/bin/activate

- On **Windows**:

  .. code-block:: bash

     .\venv\Scripts\activate

2. Create a `.env` file
------------------------

In the project **root** directory, create a file named ``.env`` with your account credentials:

.. code-block:: ini

   DB_NAME={db_name}
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=localhost
   DB_PORT=5432
   IPINFO_LITE_API_TOKEN={API}
   ripe_api_token={ripe API with persmission to perform measurments}
   ripe_account_email={email of your ripe account}
   ACCOUNT_ID={geolite account id}
   LICENSE_KEY={geolite key}

In addition, the config file with public data is located at ``server/server_config.yaml``:

.. code-block:: yaml

   ntp:
     version: 4
     timeout_measurement_s: 7  # in seconds
     number_of_measurements_for_calculating_jitter: 8

   edns:
     mask_ipv4: 24  # bits
     mask_ipv6: 56  # bits
     default_order_of_edns_servers:
       - "8.8.8.8"
       - "1.1.1.1"
       - "2001:4860:4860::8888"
     edns_timeout_s: 3  # in seconds

   ripe_atlas:
     timeout_per_probe_ms: 4000
     packets_per_probe: 3
     number_of_probes_per_measurement: 3

   bgp_tools:
     anycast_prefixes_v4_url: "https://raw.githubusercontent.com/bgptools/anycast-prefixes/master/anycatch-v4-prefixes.txt"
     anycast_prefixes_v6_url: "https://raw.githubusercontent.com/bgptools/anycast-prefixes/master/anycatch-v6-prefixes.txt"

   max_mind:
     path_city: "GeoLite2-City.mmdb"
     path_country: "GeoLite2-Country.mmdb"
     path_asn: "GeoLite2-ASN.mmdb"

.. note::

   - Make sure PostgreSQL is running and accessible with the credentials in ``.env``.
   - If any required variable in the config is missing or invalid, the server will not start and will show which variable is incorrect.

3. Install backend dependencies
-------------------------------

.. code-block:: bash

   cd server
   pip install -r requirements.txt

4. Schedule maxmind and BGP tools DB downloads
----------------------------------------------

This step initializes the local databases for geolocation and anycast detection, and sets up automatic daily updates.

Make sure you are in the root directory and that ``.env`` is configured.

.. code-block:: bash

   cd ..
   crontab -e

Add the following line:

.. code-block:: bash

   0 1 * * * /bin/bash /full_path_to/update_geolite_and_bgptools_dbs.sh >> /full_path_to/update_geolite_and_bgptools_dbs.log 2>&1

Replace ``/full_path_to`` with the output of:

.. code-block:: bash

   pwd

To run the update script manually:

.. code-block:: bash

   ./update_geolite_and_bgptools_dbs.sh

Common errors
^^^^^^^^^^^^^

- If the ``.env`` file was created on Windows, it may contain invisible carriage return characters (``^M``), which can cause the shell script to fail.

  Use:

  .. code-block:: bash

     cat -A .env
     dos2unix .env

- If you see:

  .. code-block:: bash

     /bin/bash^M: bad interpreter: No such file or directory

  This means your script likely has CRLF line endings instead of LF. Convert using:

  .. code-block:: bash

     dos2unix update_geolite_and_bgptools_dbs.sh

- Downloading the GeoLite databases has a daily limit per account.

.. note::

   You should schedule this script to run every day.

5. Run the server
-----------------

.. code-block:: bash

   uvicorn server.app.main:create_app --reload --factory

You should now see the server running!
