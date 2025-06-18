### **Group 15d**

# Are your time servers on time. Active Internet Measurements to evaluate time servers.

## Product Structure

The product is split into 2 parts. The first one is the server side, that handles the
measurements and API calls to `ntplib` and the Ripe Atlas API, stores measurements
in the database and interacts with it to retrieve historical data, and has classes and
an API to send data to the front end and client side. The second part is the client,
which contains all of the front-end of the application. It uses `React` with `Vite`, base
`CSS` for styling, `ChartJS` for data visualization, and `axios` for API interaction.

## Table of Contents

- [Server](#server)
  - [Database design](#database-design)
  - [Server Setup and Running](#server-setup-and-running)
- [Client](#client)
  - [Client Setup and Running](#client-setup-and-running)
  - [Global Types](#global-types)
  - [API Usage](#api-usage)
  - [API Hooks](#api-hooks)
  - [TypeScript Components](#typescript-components)

### Server

#### Database design

The database used to store measurements uses `PostgreSQL` for its persistance.

The design for the two tables used to store data are shown in `database-schema.md`

#### Server Setup and Running

To set up and run the backend server, follow these steps:

---

1. **Create a virtual environment**:

    ```bash
    python -m venv venv
    ```

   Then activate the virtual environment:
    - On **macOS/Linux**:
        ```bash
        source venv/bin/activate
        ```
    - On **Windows**:
        ```bash
        .\venv\Scripts\activate
        ```

---

2. **Create a `.env` file** in the `root` directory with your accounts credentials in the following format:

    ```dotenv
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
    ```
   Besides, the config file with public data for the server is `server/server_config.yaml` and it contains the following variables:

      ```yaml
        ntp:
          version: 4
          timeout_measurement_s: 7  # in seconds
          number_of_measurements_for_calculating_jitter: 8


        edns:
          mask_ipv4: 24 # bits
          mask_ipv6: 56 # bits
          default_order_of_edns_servers: # you can add multiple servers ipv4 or ipv6. The first one has the highest priority.
            # The others are used in case the first one cannot solve the domain name
            - "8.8.8.8"
            - "1.1.1.1"
            - "2001:4860:4860::8888"
          edns_timeout_s: 3 # in seconds


        ripe_atlas:
          timeout_per_probe_ms: 4000
          packets_per_probe: 3
          number_of_probes_per_measurement: 3

        bgp_tools:
          anycast_prefixes_v4_url: "https://raw.githubusercontent.com/bgptools/anycast-prefixes/master/anycatch-v4-prefixes.txt"
          anycast_prefixes_v6_url: "https://raw.githubusercontent.com/bgptools/anycast-prefixes/master/anycatch-v6-prefixes.txt"

        max_mind: # see load_config_data if you want to change the path
          path_city: "GeoLite2-City.mmdb"
          path_country: "GeoLite2-Country.mmdb"
          path_asn: "GeoLite2-ASN.mmdb"
      ```

   **Note**:
    - Ensure PostgreSQL is running and accessible with the credentials provided in the `.env` file.
    - You can edit the config variables, but if there are any variables that are missing or have invalid data, the
      server will not start, and it will tell you exactly which config variables have problems.

---

3. **Install the backend dependencies**:

    ```bash
    cd server
    pip install -r requirements.txt
    ```

---

4. **Download the max mind and BGP tools databases, and schedule running this file once every day**:

    This will initialise the local dbs for geolocation and detecting anycast, and will schedule downloading them every day at 1 AM.
    Be sure that you are in the root folder, and `.env` file has all variables.

    ```bash
    cd ..
    crontab -e
    0 1 * * * /bin/bash /full_path_to/update_geolite_and_bgptools_dbs.sh >> /full_path_to/update_geolite_and_bgptools_dbs.log 2>&1
    ```
   But replace `/full_path_to` with the output of running :
   ```bash
    pwd
    ```
   Or if you want to manually run it without scheduling:
    ```bash
      ./update_geolite_and_bgptools_dbs.sh
    ```

   **Common errors**:
   - If you run `update_geolite_and_bgptools_dbs.sh` from Linux or WSL, the file `.env` may contain invisible Windows carriage return characters and this may make the `.sh` script to fail. You can see them using `cat -A .env`. Look for any "^M"
       at the end of lines. You can remove them by running this command: `dos2unix .env`. This should solve the problem.
   - If you are using Linux or WSL and you received `/bin/bash^M: bad interpreter: No such file or directory` then it may mean that your script has Windows-style line endings (CRLF, \r\n) instead of Unix-style (LF, \n)
   - If downloading the Geolite databases fails, consider that downloading them has a daily limit per account. (This limit is only for geolite databases)

    **Notes**:
    - Be sure to schedule running this file once every day.

---

5. **Run the server**:

    ```bash
    uvicorn server.app.main:create_app --reload --factory
    ```

    You should see the server running now!
### Client

#### Client Setup and Running

To set up and run the client, follow these steps:

1. **Ensure you have the prerequisites installed**

  - [Node.js](https://nodejs.org/)
  - npm (comes bundled with Node.js)

    ```bash
    node -v
    npm -v
    ```

  If not, install from https://nodejs.org/

2. **Install the dependencies**

    ```bash
    cd ./client
    npm install
    ```

    Ensure you are in the client folder

3. **Running the client**

    ```bash
    npm run dev
    ```

#### Global types

The global types that are used across multiple components are stored in ```client\src\utils\types.ts```.

* **NTPData**
    * This data type is used for storing the relevant variables of the measurements that displayed on the website and
      used for the visualisation of data. It stores the following:
>        * Offset
>        * Round-trip time
>        * Stratum of the NTP server
>        * Jitter
>        * Precision of the NTP server
>        * Time at which the measurement taken as UNIX time
>        * IP address of the NTP server
>        * Name of the NTP server
>        * Reference ID of the reference of the NTP server
>        * Root dispersion of the NTP server
>        * Root delay of the NTP server
>        * The IP address of the vantage point
* **RIPEData**
    * This data type is used for storing the relevant variables received and displayed from the measurements taken from the
      measurents taken by RIPE Atlas. it stores the following:
>        * An NTPData variable with all its data
>        * The ID of the probe that perfomed the measurement
>        * The country the probe is stored in
>        * The geolocation of the probe
>        * If the ripe measurement results were actually received
>        * The measurement ID of the measurement the probe was a part of
* **RIPEResp**
    * This data type is used for the response of the trigger call for the RIPE measurement. It stores the following:
>      * The measurement ID of the measurement that is going to start
>      * the IP of the vantage point that initiated the RIPE measurement
* **Measurement**
    * This data type is used for determining what measurement should be shown on the graphs.
>      It consists of a composite type of the form: ```"RTT" | "offset"```

#### API Usage

There are currently `5` different API endpoints used by the front-end of the application,
These can all be found in ```client\src\hooks```.

They all use ```axios``` for the requests, and each have a different function they implement.
The helper functions for transforming data and  the global types used can all be found in ```client\utils```

##### **API Hooks**

1. **useFetchIPData**

    This hook provides the query of the user as a payload to backend. It can be either an IP or a domain name.

    It performs a **POST** request to the backend to measure the given NTP server.
    If the query is a domain name, the result consists of all NTP servers that it measures from the domain name, if it's an IP, only the NTP
    server corresponding to that specific IP.
    It parses the JSON received from the backend my using the method ```transformJSONDataToNTPData```.

    It returns a **5-tuple**:

    | Return value     | Description                                                  |
    |------------------|--------------------------------------------------------------|
    | ```data```       | An array of NTP results                                      |
    | ```loading```    | ```boolean``` indicating if the measurement is still ongoing |
    | ```error```      | Error object if one occured                                  |
    | ```httpStatus``` | The HTTP status of the request                               |
    | ```fetchData```  | A function for initiating the POST request                   |

2. **useFetchHistoricalIPData**

    This hook provides the data over a specific period of time for the server queried by the user.

    It performs a **GET** request to the backend to fetch historical data.
    The server can, similarly to the previous hook, be either an IP or a domain name.
    The start time and end times are used in the ISO8601 format.
    It parses the JSON received from the backend my using the method ```transformJSONDataToNTPData```.

    It returns a **4-tuple**:

    | Return value     | Description                                                  |
    |------------------|--------------------------------------------------------------|
    | ```data```       | An array of NTP results                                      |
    | ```loading```    | ```boolean``` indicating if the measurement is still ongoing |
    | ```error```      | Error object if one occured                                  |
    | ```fetchData```  | A function for initiating the GET request                    |


3. **useTriggerRipeMeasurement**

    This hook is what send the trigger for the RIPE measurement to be started.

    It performs a **POST** requst to the backend with the queried server as a payload to trigger the measurement.
    As a result it gets a confirmation that the measurement started, as well as the measurement ID of the measurement started, and the IP of the
    vantage point that started the RIPE measurement.
    It parses the JSON received in place, since it a simple response.

    It returns a **4-tuple**:

    | Return value     | Description                                                  |
    |------------------|--------------------------------------------------------------|
    | ```data```       | The response of the trigger as ```RIPERest```                |
    | ```loading```    | ```boolean``` indicating if the measurement is still ongoing |
    | ```error```      | Error object if one occured                                  |
    | ```fetchData```  | A function for initiating the POST request                   |

4. **useFetchRipeData**

    This hook is what is used to receive the actual RIPE measurement data from the backend.

    It perfoms **polling** on the backend's endpoint to regularly update the data it receives.
    This is beacuse RIPE doesn't offer all the data at once, instead slowly sending the measurements from the probes its done.
    It has an adjustable polling rate from the method signature.
    Since the polling may begin before the RIPE measurement is ready, in the case it receives HTTP 405 from the backend (Method not allowed),
    it has a separate timer to retry after.
    The polling continues until there is an error, the measurement is complete, the measurement times out, or until a new one begins.
    In the case of the new measurement beggining, the previous polling call is cancelled in order to prevent interleaving and other issues.

    It returns a **3-tuple** consisting of:

    | Return value | Description                                                  |
    |--------------|--------------------------------------------------------------|
    | ```result``` | An array of RIPE results                                     |
    | ```status``` | compound type indicating the current state of the measurement|
    | ```error```  | Error object if one occured                                  |

- The compound type used for indicating the status is:  ```"pending" | "partial_results" | "complete" | "timeout" | "error"```

5. **useIpInfo**

    This hook is for fetching the geolocation of IPs in a way that does not require data communication with the backend

    It makes used of ```ip-api``` for the retreival of geolocation data from IPs via a **GET**.
    It saves both the coordinates retrieved and the country code.
    It is only used for getting the location of the NTP servers queried, as well as the vantage point.
    It saves the result as a ```IpInfoData``` data variable which consists of:
      - a ```[number,number]``` type: ```coordinates```
      - a `string` type: ```country_code```
    This type is not saved in ```client\utils``` since it is not widely used like the other types there

    It returns a **5-tuple**:

    | Return value     | Description                                                  |
    |------------------|--------------------------------------------------------------|
    | ```data```       | Geolocation data fetched as ```IpInfoData```                 |
    | ```loading```    | ```boolean``` indicating if the measurement is still ongoing |
    | ```error```      | Error object if one occured                                  |
    | ```fetchData```  | A function for initiating the GET request                    |
    | ```clearIP```    | A function for resetting the state of ```data```             |

    It is important to note that if the IP address provided is private, then the ```coordinates``` field of the result will have the following format: ```[undefined, undefined]```

#### TypeScript Components

For the better running, understanding and modularity of the code, several sections of the front-end were split into
different components.

* **DownloadButton**
* **Hero**
* **InputSection**
* **LineGraph**
    * A component that uses ChartJS to create line graph for the data provided. Uses the `Measurement` type to make the
      graph show either delay or offset
      as measures on the y-axis. These values are taken from data provided to the component as an array of `NTPData`.
    * The `Measurement` type conists of either the strings ``delay`` or ``offset``, to indicate which of the desired
      measure will be indicated.
    * On the x-axis is shows the time of measurement, as a string of a `Date` object, taken from the `time` field of
      `NTPData`.
* **LoadingSpinner**
* **ResultSummary**
* **TimeInput**
* **Visualization**
    * The popup that appears when pressing the "View Historical Data" button. It contains all the possible options for
      choosing which data to visualize
    * Contains **Dropdowns** for choosing the desired time period.
    * The `Custom` button allows the user to input a time period of their choice using the new fields that appear.
    * The `Delay` and `Offset` radios are used to pick the option of which measurement to be shown.
    * The **DownloadButtons** allow the user to download the data for the data during the selected time period.
* **WorldMap**
    * This component renders a map for all the geolocation data to be visualized
    * Makes use of `Leaflet` for rendering the map
    * The base tile used is ***Dark Matter*** offered by [CARTO](https://carto.com/)
    * It shows the location of the probes, NTP server(s) and vantage point
    * The icons used can be found in `src\assets`
    * Each point on the map show some information related to it, such as:
      - RTT, Offset and probe ID for the RIPE probes
      - IP and name for the NTP server(s)
      - IP and location for the vantage point