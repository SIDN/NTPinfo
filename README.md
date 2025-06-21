### **Group 15d**

# Are your time servers on time? Active Internet Measurements to evaluate time servers.

<p align="center">
  <img src="assets/NtpInfoLogo.png" alt="Project Logo" style="width:100%; max-width:100%;"/>
</p>

---

## Product Structure

The product is split into 2 parts. The first one is the server side, that handles the
measurements and API calls to `ntplib` and the Ripe Atlas API, stores measurements
in the database and interacts with it to retrieve historical data, and has classes and
an API to send data to the front end and client side. The second part is the client,
which contains all of the front-end of the application. It uses `React` with `Vite`, base
`CSS` for styling, `ChartJS` for data visualization, and `axios` for API interaction.

## Table of Contents

- [Server Setup and Running](#server-setup-and-running)
- [Client Setup and Running](#client-setup-and-running)
- [Docker Setup](#docker-setup)
- [Contributing](#contributing)

### Server Setup and Running

There are 2 ways in starting the server. The first one is to manually configure it, and the second one is using a docker
container.

To set up and run the back-end server, follow these steps:

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

2. **Install and prepare PostgreSQL database**

2.1. Go to: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads and select the version of PostgreSQL
you want to install.
2.2. Go to download file location
Double click the .exe file
Follow through the installation process and keep track of:
where you installed it,
the superuser (usually postgres),
the port (usually 5432),
the password (you should remember this one)
2.3. pgAdmin should automatically be installed, so accept to install it when prompted.
2.4. Restart your computer.
2.5. pgAdmin should be in your system if you followed the installation correctly. Open it, click on Server and put in
your password if necessary.
2.6. Right click on Databases, click "Create" and create an empty database, preferably named "measurements". Tables will
be handled once you run the back-end server, so do not worry about them right now.

---

3. **Create a `.env` file** in the `root` directory with your accounts credentials in the following format:

    ```dotenv
    #needed for back-end (server)
    DB_NAME=measurements # the database that you want to use from PostgreSQL, preferably named "measurements"
    DB_USER=postgres
    DB_PASSWORD=postgres
    DB_HOST=db# (or "localhost" if you run the project locally)
    DB_PORT=5432
    ripe_api_token={ripe API with persmission to perform measurments}
    ripe_account_email={email of your ripe account (you need to have credits)}
    ACCOUNT_ID={geolite account id}
    LICENSE_KEY={geolite key}
    UPDATE_CRON_SCHEDULE=0 0 * * * # once every day
    CLIENT_URL=http://localhost:5173 # change to desired value

    #needed for front-end (client)
    DOCKER_NETWORK_SUBNET=2001:db8:1::/64
    DOCKER_NETWORK_GATEWAY=2001:db8:1::1
    VITE_CLIENT_HOST=localhost # change to desired value
    VITE_CLIENT_PORT=5173 # change to desired value
    VITE_SERVER_HOST_ADDRESS=http://localhost:8000
    VITE_STATUS_THRESHOLD=1000 # in milliseconds, choose a value you think is reasonable for the offset threshold
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
    - Be sure to schedule running this file once every day or to manually update them, if you want up-to-date
      information.

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
sudo docker-compose build
```

or this command if the first one failed:

```bash
sudo docker-compose build --no-cache
```

**Common Errors**

- If it fails, and you received error `error during connect`, then make sure that you have Docker Desktop open.

---

### 5. Start the containers

```bash
sudo docker-compose up
```

### **‼️️ Very Important ‼️**

- Every time after you run `sudo docker-compose up` and it failed, and you want to try again, you need to run
  `sudo docker-compose down` before trying again. This also applies when **you want to build again**.

**Common Errors**

- If it fails with `exec /app/docker-entrypoint.sh: no such file or directory, exited with code 255` then it means that
  the file `docker-entrypoint.sh` (or `update.sh`) has CRLF format, and you need to change it to LF.

Use `-d` to run it in the background:

```bash
sudo docker-compose up -d
```

> Make sure there is not any network name `my-net` already in use.

This can be checked by running:

```bash
sudo docker network ls
```

---

### 6. Shut down the containers

To gracefully stop all services:

```bash
sudo docker-compose down
```

### This must be done every time changes have been done, or one of the containers failed.

---

## Everything should now be running at:

- **Frontend**: [http://localhost:5173](http://localhost:5173)
- **Backend API**: [http://localhost:8000](http://localhost:8000)

> Make sure ports `5173` (frontend) and `8000` (backend) are not in use before starting the containers.

## Contributing

We appreciate any new contributions from the open-source community

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also
simply open an issue with the tag "enhancement".

1. Fork the Project
2. Create your Feature Branch (`git checkout -b branch-name`)
3. Commit your Changes (`git commit -m 'Added feature'`)
4. Push to the Branch (`git push origin branch-name`)
5. Open a Pull Request