### **Group 15d**

# Are your time servers on time. Active Internet Measurements to evaluate time servers.

## Product Structure

The product is split into 2 parts. The first one is the server side, that handles the
measurements and API calls to `ntplib` and the Ripe Atlas API, stores measurements
in the database and interacts with it to retrieve historical data, and has classes and
an API to send data to the front end and client side. The second part is the client,
which contains all of the front-end of the application. It uses `React` with `Vite`, base
`CSS` for styling, `ChartJS` for data visualization, and `axios` for API interaction.

### Server

#### Database design

The database used to store measurements uses `PostgreSQL` for its persistance.

The design for the two tables used to store data are as follows:
> * **measurements**
>    * id -                      `bigint`, **Non-nullable**, ***primary key***, key to identify each measurement
>    * ntp_server_ip -           `inet`, the IP adress of the NTP server that was measured. Supports IPv4 or IPv6.
>    * ntp_server_name -         `text`, the name of the NTP server that was measured.
>    * ntp_version -             `smallint`, the version of NTP used for the measurement.
>    * ntp_server_ref_parent -   `inet`, the IPv4 or IPv6 adress of the parent of the NTP server.
>    * ref_name -                `text`, the name of the server the measured NTP server references.
>    * time_id -                 `bigint`,
>    * time_offset -             `double precision`,
>    * delay -                   `double precistion`, the delay of the NTP server.
>    * stratum -                 `integer`, the stratum the NTP server operates on.
>    * precision -               `double precision`, the precistion of the NTP server.
>    * reachability -            `text`, the status of the NTP server, made in accordance to the RCF8663 standard.
>    * root_delay -              `bigint`,
>    * ntp_last_sync_time -      `bigint`,
>    * root_delay_prec -         `bigint`,
>    * ntp_last_sync_time -      `bigint`,
>* **times**
>  * id -         `bigint`, **Non-nullable**, ***primary key***, key to identify each measurement
>  * client_sent -             `bigint`, the time the request was sent by the client in Epoch time.
>  * client_sent_prec -        `bigint`, the 32 bits of accuracy for the client sent time.
>  * server_recv -             `bigint`, the time the request was received by the server in Epoch time.
>  * server_recv_prec -        `bigint`, the 32 bits of accuracy for the server receive time.
>  * server_sent -             `bigint`, the time when the request was sent back by the server in Epoch time.
>  * server_sent_prec -        `bigint`, the 32 bits of accuracy for the server send back time.
>  * client_recv -             `bigint`, the time when the request was received back by the client in Epoch time.
>  * client_recv_prec -        `bigint`, the 32 bits of accuracy for the client receive back time.

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

2. **Create a `.env` file** in the `root` directory with your database credentials in the following format:

    ```dotenv
    DB_NAME={db_name}
    DB_USER=postgres
    DB_PASSWORD=postgres
    DB_HOST=localhost
    DB_PORT=5432
    ```

   **Note**: Ensure PostgreSQL is running and accessible with the credentials provided in the `.env` file.

---

3. **Install the backend dependencies**:

    ```bash
    cd server
    pip install -r requirements.txt
    ```

---

4. **Run the server**:

    ```bash
    uvicorn server.app.api.routing:app --reload
    ```

### Client

#### Running the client

To start and run the client, input the command ```npm run dev``` in the terminal.

##### Global types

The global types that are used across multiple components are stored in ```client\src\types.ts```.

* **NTPData**
    * This data type is used for storing the relevant variables of the measurements that displayed on the website and
      used for the visualisation of data. It stores the following:
        * offset
        * delay
        * stratum
        * jitter
        * reachability
        * passing
        * time

#### API Usage

There are currently `4` different API endpoints used by the front-end of the application
These can all be found in ```client\src\hooks```.

They modify the JSON send by the back-end into `NTPData` type by calling the **transformJSONData** function located
at ```client\src\transformJSONData.ts```.

The values represent the same things as what is in the JSON, with the exception of **time** which is the process value
of `"client_sent_time"` to know when the measurement was taken.

##### **APIs**

All of the APIs converts the JSON received from the back-end to the desired type by using the **transformJSONData**
function.
The format for the API link is `url/user_input/client_ip` for fetching measurement data, and
`url/historical/user_input/client_ip`
for fetching historical data. The IP is be transmitted to the back-end for both rate limiting and for using NTP
measurements from
the NTP servers that the client IP would access for those that support it, such as Apple, Microsoft, AWS and pool.ntp.

* **useFetchIPData**
    * uses the IP address provided by the user to send a request for a time measurement on the NTP server with the given
      IP.
    * returns 4-tuple consisting of the received data as an `NTPValue` variable: ```data```, if the measurement is
      currently still ongoing as a `boolean`: ```loading```
      if an error occurred as an `Error`: ```error```, and the function for fecthing data from an API endpoint as a
      `string`: ```fetchData```.
* **useFetchHistoricalIPData**
    * uses the IP address provided by the user to send a request for the retreival of historical data over the period
      of time specified by the user from the NTP server with the given IP adress.
    * returns 4-tuple consisting of the received data as an array of `NTPValue` variables: ```data```, if the
      measurement is currently still ongoing as a `boolean`: ```loading```
      if an error occurred as an `Error`: ```error```, and the function for fecthing data from an API endpoint as a
      `string`: ```fetchData```.

#### TypeScript Components

For the better running, understanding and modularity of the code, several sections of the front-end were split into
different components.

* **DownloadButton**
* **Dropdown**
    * Allows the user to easily build and define the elements within the dropdown menu, as defined by `DropdownProps`:
        * `label`: The name of the dropdown menu that will be displayed on the page.
        * `options`: The options that will be available from within the dropdown menu.
        * `selectedValue`: The current value picked on the dropdown menu. Has the default value of the first option
          given.
        * `onSelect`: The function that dictated what will change when the target option of the dropdown is selected.
        * `className`: The desired class name of the dropdown menu for CSS styling.
* **Hero**
* **LineGraph**
    * A component that uses ChartJS to create line graph for the data provided. Uses the `Measurement` type to make the
      graph show either delay or offset
      as measures on the y-axis. These values are taken from data provided to the component as an array of `NTPData`.
    * The `Measurement` type conists of either the strings ``delay`` or ``offset``, to indicate which of the desired
      measure will be indicated.
    * On the x-axis is shows the time of measurement, as a string of a `Date` object, taken from the `time` field of
      `NTPData`.
* **Visualization**
    * The popup that appears when pressing the "View Historical Data" button. It contains all the possible options for
      choosing which data to visualize
    * Contains **Dropdowns** for choosing the desired time period.
    * The `Custom` button allows the user to input a time period of their choice using the new fields that appear.
    * The `Delay` and `Offset` radios are used to pick the option of which measurement to be shown.
    * The **DownloadButtons** allow the user to download the data for the data during the selected time period.