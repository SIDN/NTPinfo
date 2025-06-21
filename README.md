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

There aer 2 ways in starting the server. The first one is manually configured it, and the second one is using a docker container.

To set up and run the backend server, follow these steps:

#### Locally configure the server
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

2. **Install and prepare PostreSQL database**

Make sure you have PostgreSQL installed and create an empty database. We recommend to name it something like "measurements". You will use the name of your database in DB_NAME later.
You need to create an empty database called "measurements" in PostgreSQL. Do not worry about the tables, everything
   is handled when you run the server.

---
3. **Create a `.env` file** in the `root` directory with your accounts credentials in the following format:

    ```dotenv
    DB_NAME={db_name} # the database that you want to use from PostgreSQL
    DB_USER=postgres
    DB_PASSWORD=postgres
    DB_HOST=localhost (or "db" if you run the project with docker)
    DB_PORT=5432
    IPINFO_LITE_API_TOKEN={API}
    ripe_api_token={ripe API with persmission to perform measurments}
    ripe_account_email={email of your ripe account (you need to have credits)}
    ACCOUNT_ID={geolite account id}
    LICENSE_KEY={geolite key}
    UPDATE_CRON_SCHEDULE=0 0 * * * # once every day
    VITE_SERVER_HOST_ADDRESS=http://localhost:8000
    VITE_STATUS_THRESHOLD=1000
    DOCKER_NETWORK_SUBNET=2001:db8:1::/64
    DOCKER_NETWORK_GATEWAY=2001:db8:1::1
    VITE_CLIENT_HOST=localhost # change to desired value
    VITE_CLIENT_PORT=5173 # change to desired value
    CLIENT_URL=http://localhost:5173 # change to desired value
    ```
   Besides, the config file with public data for the server is `server/server_config.yaml` and it contains the following
   variables that you can change:

      ```yaml
        ntp:
          version: 4
          timeout_measurement_s: 7  # in seconds
          number_of_measurements_for_calculating_jitter: 8
          server_timeout: 60 # in seconds


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

4. **Install the backend dependencies**:

    ```bash
    cd server
    pip install -r requirements.txt
    ```

---


5. **Download the max mind and BGP tools databases, and schedule running this file once every day**

   This will initialise the local dbs for geolocation and detecting anycast, and will schedule downloading them every
   day at 1 AM.
   Be sure that you are in the root folder, and `.env` file has all variables.

   If you want to schedule updating the databases, run this:

    ```bash
    cd ..
    crontab -e
    0 1 * * * /bin/bash /full_path_to/update_geolite_and_bgptools_dbs.sh >> /full_path_to/update_geolite_and_bgptools_dbs.log 2>&1
    ```
   But replace `/full_path_to` with the output of running :
   ```bash
    pwd
    ```
   Or if you just want to download the databases once without scheduling:
    ```bash
      ./update_geolite_and_bgptools_dbs.sh
    ```

   **Common errors**:
    - If you run `update_geolite_and_bgptools_dbs.sh` from Linux or WSL, the file `.env` may contain invisible Windows
      carriage return characters and this may make the `.sh` script to fail. You can see them using `cat -A .env`. Look
      for any "^M"
      at the end of lines. You can remove them by running this command: `dos2unix .env`. This should solve the problem.
    - If you are using Linux or WSL and you received `/bin/bash^M: bad interpreter: No such file or directory` then it
      may mean that your script has Windows-style line endings (CRLF, \r\n) instead of Unix-style (LF, \n). Another 
   solution to change from CRLF to LF is to open the file in VS Code and to change them to LF.
    - If downloading the Geolite databases fails, consider that downloading them has a daily limit per account. (This
      limit is only for geolite databases)

   **Notes**:
    - Be sure to schedule running this file once every day or to manually update them, if you want up-to-date information.

---

6. **Run the server (from the root directory)**:

    ```bash
    uvicorn server.app.main:create_app --reload --factory
    ```

   You should see the server running now!



#### Client Setup and Running

To set up and run the client, follow these steps carefully:

1. **Ensure you have the prerequisites installed**

- [Node.js](https://nodejs.org/)
  - npm (comes bundled with Node.js)

    ```bash
    node -v
    npm -v
    ```
    If not, install from https://nodejs.org/
2. **Create `.env` file in client**

   Create a `.env` file in `client` and add the following to the file:
    ```dotenv
    VITE_SERVER_HOST_ADDRESS=http://localhost:8000/ # address of our server (back-end)
    VITE_STATUS_THRESHOLD=1000 # in ms
    VITE_CLIENT_HOST=localhost # change to desired value
    VITE_CLIENT_PORT=5173 # change to desired value
    CLIENT_URL=http://localhost:5173 # change to desired value
     ```
    
3. **Install the dependencies**

   Ensure you are in the client folder
    ```bash
    cd ./client
    npm install
    ```

4. **Running the client**

    ```bash
    npm run dev
    ```
   Everything should be set now!



# Docker Setup

To run the full stack (server + client + database) using `docker-compose`, follow these steps:

---

### 1. Install Docker

Follow the instructions for your OS here:  
👉 [https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)

---

### 2. Install `docker-compose` (Linux)

```bash
sudo apt update
sudo apt install docker-compose
```

---

### 3. Add a .env file in the root directory

**Create a `.env` file** in the `root` directory (the same directory with you `docker-compose.yml`) with your accounts
credentials. (You can see this `.env` at the above of the page)

---

### 4. Build the Docker containers

From the root of the project, run this, but make sure that Docker Desktop is open:

```bash
docker-compose build
```
or this command if the first one failed:
```bash
docker-compse build --no-cache
```

**Common Errors**
- If it fails, and you received error `error during connect`, then make sure that you have Docker Desktop open.
---

### 5. Start the containers

```bash
docker-compose up
```
**Common Errors**
- If it fails with `exec /app/docker-entrypoint.sh: no such file or directory, exited with code 255` then it means that 
the file `docker-entrypoint.sh` (or `update.sh`) has CRLF format, and you need to change it to LF.

**Very Important**
- Every time after you run `docker-compose up` and it failed, and you want to try again, you need to run `docker-compose down` before trying again.
Use `-d` to run it in the background:

```bash
docker-compose up -d
```

> Make sure there is not any network name `my-net` already in use.

This can be checked by running:

```bash
docker network ls
```

---

### 6. Shut down the containers

To gracefully stop all services:

```bash
docker-compose down
```

---

## Everything should now be running at:

- **Frontend**: [http://localhost:5173](http://localhost:5173)
- **Backend API**: [http://localhost:8000](http://localhost:8000)

> Make sure ports `5173` (frontend) and `8000` (backend) are not in use before starting the containers.

#### API Usage

There are currently `5` different API endpoints used by the front-end of the application,
These can all be found in ```client\src\hooks```.
