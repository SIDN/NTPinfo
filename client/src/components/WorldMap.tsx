import L from 'leaflet'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet'
import { useEffect, useState, useRef } from 'react'
import { NTPData, RIPEData } from '../utils/types'
import greenProbeImg from '../assets/green-probe.png'
import yellowProbeImg from '../assets/yellow-probe.png'
import redProbeImg from '../assets/red-probe.png'
import darkRedProbeImg from '../assets/dark-red-probe.png'
import grayProbeImg from '../assets/gray-probe.png'
import ntpServerImg from '../assets/ntp-server-icon.png'
import vantagePointImg from '../assets/vantage-point-logo.png'
import { useIPInfo } from '../hooks/useIPInfo'

import '../styles/WorldMap.css'

/**
 * Standard code added for the proper functioning of the default icon when using Leaflet with Vite
 */
delete (L.Icon.Default.prototype as any)._getIconUrl

L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
  zIndexOffset: 1000
})

/**
 * Custom Icons used for markers on the map, each with a different color indicating the RTT time
 */
const greenIcon = new L.Icon({
  iconUrl: greenProbeImg,
  iconSize: [20, 20],
  iconAnchor: [10, 10],
  popupAnchor: [0, -8]
})

const yellowIcon = new L.Icon({
  iconUrl: yellowProbeImg,
  iconSize: [20, 20],
  iconAnchor: [10, 10],
  popupAnchor: [0, -8]
})

const redIcon = new L.Icon({
  iconUrl: redProbeImg,
  iconSize: [20, 20],
  iconAnchor: [10, 10],
  popupAnchor: [0, -8]
})

const darkRedIcon = new L.Icon({
  iconUrl: darkRedProbeImg,
  iconSize: [20, 20],
  iconAnchor: [10, 10],
  popupAnchor: [0, -8]
})

const grayIcon = new L.Icon({
  iconUrl: grayProbeImg,
  iconSize: [20, 20],
  iconAnchor: [10, 10],
  popupAnchor: [0, -8]
})

const ntpServerIcon = new L.Icon({
  iconUrl: ntpServerImg,
  iconSize: [30, 30],
  iconAnchor: [12, 15],
  popupAnchor: [0, -8],
  zIndexOffset: 1000
})

const vantagePointIcon = new L.Icon({
  iconUrl: vantagePointImg,
  iconSize: [30, 30],
  iconAnchor: [15, 30],
  popupAnchor: [0, -28],
  zIndexOffset: 500
})

/**
 * Interface used in assigning values to the map component
 */
interface MapComponentProps {
  probes: RIPEData[] | null
  ntpServers: NTPData[] | null
  vantagePointIp: string | null
  status: string | null
}

/**
 * A function that sets the zoom of the map to an appropiate value depeding on how spread out all the geolocations are
 * Depends on the size of the map component on the page
 * Made to change the zoom in a responsive way with the change of the map size
 * It changes zoom when the probes update, until the user interact with the map
 * @param probes the geolocation of all the probes to the shown on the map
 * @param ripeNtpServer the geolocation of the NTP server that the RIPE measurement was performed on
 * @param measurementNtpServer the geolocation of the NTP server that the vantage point measured on
 * @param vantagePoint the geolocation of the vantage point that the measurement was taken from
 */
const FitMapBounds = ({probes, ripeNtpServer, measurementNtpServer, vantagePoint}: {probes: L.LatLngExpression[], 
  ripeNtpServer: L.LatLngExpression | null, measurementNtpServer: L.LatLngExpression | null, vantagePoint: L.LatLngExpression | null}) => {
  const map = useMap()
  const userInteracted = useRef(false)
  const ignoreEvents = useRef(false)

  useEffect(() => {

    const onZoomOrMove = () => {
      if (ignoreEvents.current) return
      userInteracted.current = true
    }

    map.on('zoomstart', onZoomOrMove)
    map.on('dragstart', onZoomOrMove)

    return () => {
      map.off('zoomstart', onZoomOrMove)
      map.off('dragstart', onZoomOrMove)
    }
  }, [map])

  useEffect(() => {
    if (probes.length === 0 || !ripeNtpServer || !measurementNtpServer || !vantagePoint) return
    
    if (userInteracted.current) return

    const fitBounds = () => {
      const allPoints = [...probes, ripeNtpServer, measurementNtpServer, vantagePoint]
      const bounds = L.latLngBounds(allPoints)
      ignoreEvents.current = true
      map.fitBounds(bounds, { padding: [15, 15] })
      setTimeout(() => {
        ignoreEvents.current = false
      }, 100)
    }

    fitBounds()

    const handleWindowResize = () => {
      requestAnimationFrame(() => {
        fitBounds()
      })
    }
    window.addEventListener('resize', handleWindowResize)
    return () => {window.removeEventListener('resize', handleWindowResize)}
  }, [map, probes, ripeNtpServer, measurementNtpServer])

  return null
}

/**
 * A function to draw connecting lines from each probe to the NTP server on the map
 * It also draws a line from the vantage point to the NTP server it measured
 * @param probes the geolocation of all the probes to the shown on the map
 * @param ripeNtpServer the geolocation of the NTP server that the RIPE measurement was performed on
 * @param measurementNtpServer the geolocation of the NTP server that the vantage point measured on
 * @param vantagePoint the geolocation of the vantage point that the measurement was taken from
 */
const DrawConnectingLines = ({probes, ripeNtpServer, measurementNtpServer, vantagePoint}: {probes: L.LatLngExpression[], 
  ripeNtpServer: L.LatLngExpression | null, measurementNtpServer: L.LatLngExpression | null, vantagePoint: L.LatLngExpression | null}) => {
  const map = useMap()

  useEffect(() => {
    if (!ripeNtpServer || !measurementNtpServer || !vantagePoint) return
    probes.map(x => {
      L.polyline([x,ripeNtpServer], {color: 'blue', opacity: 0.8, weight: 1}).addTo(map)
    })
    L.polyline([vantagePoint, measurementNtpServer], {color: 'blue', opacity: 0.8, weight: 1}).addTo(map)
  },[map, probes, ripeNtpServer, measurementNtpServer, vantagePoint])

  return null
}

/**
 * Function returning an icon with a specific color depeding on the RTT measured by a specific probe
 * Cutoff values set similarly to RIPE
 * @param rtt the RTT measured by a specific probe
 * @param measured boolean indicating whether the measurement was actually successful
 * @returns the specific icon which should be shown on the map for the probe
 */
const getIconByRTT = (rtt: number, measured: boolean): L.Icon => {
  if (measured == false) return grayIcon;
  if (rtt < 15) return greenIcon;
  if (rtt < 40) return yellowIcon;
  if (rtt < 150) return redIcon;
  return darkRedIcon;
}

/**
 * Function returining a string with the measurement result of the probe
 * Returns either the string of the measurenemt value or No Reply if the measurement wasn't performed
 * @param value RTT/offset value measured by the probe
 * @returns a string indicating this specific value
 */
const stringifyRTTAndOffset = (value: number): string => {
  if (value === -1000) return "No Reply"
  else return value.toString()
}

/**
 * A function to compare if two LatLngExpressions are equal to each other
 * @param a the first LatLngExpression to be checked
 * @param b the second LatLngExpression to be checked
 * @returns if the two LatLngExpressions are both equal
 */
const equalCoords = (a: L.LatLngExpression | null, b: L.LatLngExpression | null): boolean => {
  if (a === null && b === null) return true
  if (a === null) return false
  if (b === null) return false
  const exprA = L.latLng(a)
  const exprB = L.latLng(b)
  return exprA.lat === exprB.lat && exprA.lng === exprB.lng
}

/**
 * The function for creating the WorldMap Component
 * Shows error text in case that an error occurs in fetching RIPE Data
 * Used a base tile map offered by Carto, specifically the Dark Matter basemap
 * Shows the status of the map(loading, finished, error)
 * Each probe is shown on the map with an icon of a different color depending on the RTT measured by it
 * Besides this, the vantage point and the NTP server(s) are also shown 
 * The NTP server that the RIPE probes measured on is compared with the whole list of NTP servers measured by the vantage point
 * If one of the NTP servers measured by the vantage point is the same as the one used for the RIPE measurement, only one NTP server will appear on the map
 * Each probe has a popup which shows the following:
 *  The RIPE probe ID, with a link to its page on the RIPE Atlas website
 *  The RTT measured
 *  The offset measured
 *  The location of the probe
 * The NTP server(s) has a popup showing the following:
 *  Possibly, if the probes or the vantage point did measurements on the server
 *  The name of the NTP server
 *  The IP of the specifc NTP server which was used
 * The vantage point has a popup that shows:
 *  The IP of the vantage point
 *  The location of the vantage point
 * The map has lines drawn in between each probe and the NTP server for better visualization
 * It also has a line between the vantage point and the NTP server it measured on
 * The map's zoom get automatically readjusted depending on the size of the map on the page
 * @param probes Data of all the measured probes, as an array of RIPEData values
 * @param status the current status of the polling of the RIPE measurements 
 * @returns a WorldMap component showing all probes, the NTP server and relevant values for all of them
 */
export default function WorldMap ({probes, ntpServers, vantagePointIp, status}: MapComponentProps) {
  const [statusMessage, setStatusMessage] = useState<string>("")
  const [ripeNtpServerLoc, setRipeNtpServerLoc] = useState<L.LatLngExpression | null>(null)
  const [measurementNtpServerLoc, setMeasurementNtpServerLoc] = useState<L.LatLngExpression | null>(null)
  const [vantagePointLoc, setVantagePointLoc] = useState<L.LatLngExpression | null>(null)
  const [chosenNtpServer, setChosenNtpServer] = useState<NTPData | null>(null)
  const [restNtpServers, setRestNtpServers] = useState<NTPData[] | null>(null)
  const { fetchIPInfo } = useIPInfo()

  /**
   * Effect to dynamically update the status shown depening on the progress of the RIPE measurement
   */
  useEffect(() => {
    if (status === "pending"){
      setRipeNtpServerLoc(null)
      setMeasurementNtpServerLoc(null)
      setVantagePointLoc(null)
      return 
    } else if (status === "partial_results"){
      setStatusMessage("Map Loading...")
    } else if(status === "complete" || status === "timeout") {
      setStatusMessage("Map Fully Loaded")
    } else if (status === "error") {
      setStatusMessage("Error loading RIPE data")
    }
    }, [probes, status])
  
  /**
   * Effect used for detecting if the list of NTP servers measured by the vantage point contains the same server as the one used by the RIPE measurement
   * If it finds that the list contains it, sets the chosen NTP server to the one used by RIPE
   * If not it uses one from the list
   */
  useEffect(() => {
    if (!probes || !ntpServers) return
    const ripe_ip = probes[0].measurementData.ip
    const chosen = ntpServers.find(x => x.ip === ripe_ip) || ntpServers[0]
    const rest = ntpServers.filter(x => x !== chosen) || ntpServers.slice(1)
    setChosenNtpServer(chosen)
    setRestNtpServers(rest)
  }, [probes, ntpServers])


  /**
   * Effect for updating and getting the location of the NTP servers and vantage point
   * @param ripeIpInfo.coords is the geolocation of the NTP server used by the RIPE measurement
   * @param measurementIpInfo.coords is the geolocation of the NTP server used by the measurement from the vantage point
   * @param vantagePointIpInfo.coords is the geolocation of the vantage point
   * The vantage point needs to have a public IP address in order for the location to be fetched
   * In the case that the IP is not public, the map component will fail to load due to the data being undefined
   */
  useEffect(() => {
    const fetchLocation = async () => {
      const ripe_ip = probes?.[0].measurementData.ip

      if (ripe_ip && chosenNtpServer && chosenNtpServer && vantagePointIp) {
        const ripeIpInfo = await fetchIPInfo(ripe_ip)
        const measurementIpInfo = await fetchIPInfo(chosenNtpServer.ip)
        const vantagePointIpInfo = await fetchIPInfo(vantagePointIp)
        if (ripeIpInfo)
          setRipeNtpServerLoc(ripeIpInfo.coordinates)
        if(measurementIpInfo)
          setMeasurementNtpServerLoc(measurementIpInfo.coordinates)
        if(vantagePointIpInfo)
          setVantagePointLoc(vantagePointIpInfo.coordinates)
      }
    };
    fetchLocation()
  }, [probes, ntpServers, vantagePointIp, chosenNtpServer])

  const probe_locations = probes?.map(x => x.probe_location) ?? []
  const icons = probes?.map(x => getIconByRTT(x.measurementData.RTT, x.got_results)) ?? []
  console.log(restNtpServers)
    return (
      <div style={{height: '500px', width: '100%'}}>
        <h2>{statusMessage}</h2>
        <MapContainer style={{height: '100%', width: '100%'}}>
            <TileLayer 
                url = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                attribution= '&copy; <a href="https://carto.com/">CARTO</a>'
                subdomains={['a', 'b', 'c', 'd']}
                maxZoom={19}
            />
            
            {probe_locations && icons && probes && chosenNtpServer && (
            <>
              {probe_locations.map((pos, index) => (<Marker key = {index} position = {pos} icon = {icons[index]}>
                <Popup>
                  Probe ID: <a href = {`https://atlas.ripe.net/probes/${probes[index].probe_id}/overview`} target='_blank' rel="noopener noreferrer">{probes[index].probe_id}</a><br/>
                  Offset: {stringifyRTTAndOffset(probes[index].measurementData.offset)}<br/>
                  RTT: {stringifyRTTAndOffset(probes[index].measurementData.RTT)}<br/>
                  Location: {pos[0]}, {pos[1]}
                </Popup>
              </Marker>))}


              {!equalCoords(ripeNtpServerLoc, measurementNtpServerLoc) && 
                <>
                <Marker position = {ripeNtpServerLoc ?? [0,0]} icon = {ntpServerIcon}>
                    <Popup>
                      NTP Server (RIPE)<br/>
                      IP: {probes[0].measurementData.ip}<br/>
                      Name: {probes[0].measurementData.server_name}
                    </Popup>
                </Marker>

                <Marker position = {measurementNtpServerLoc ?? [0,0]} icon = {ntpServerIcon}>
                    <Popup>
                      NTP Server (Vantage Point)<br/>
                      IP: {chosenNtpServer.ip}<br/>
                      Name: {chosenNtpServer.server_name}
                    </Popup>
                </Marker>
                </>
              }

              {equalCoords(ripeNtpServerLoc, measurementNtpServerLoc) &&
                <Marker position = {ripeNtpServerLoc ?? [0,0]} icon = {ntpServerIcon}>
                    <Popup>
                      NTP Server<br/>
                      IP: {probes[0].measurementData.ip}<br/>
                      Name: {probes[0].measurementData.server_name}
                    </Popup>
                </Marker>
              }

              {restNtpServers && restNtpServers.map((x,index) => (
                <Marker key={index} position={[0,0]} icon = {ntpServerIcon}>
                  <Popup>
                    NTP Server (Vantage Point)<br/>
                    IP: {x.ip}<br/>
                    Name: {x.server_name}
                  </Popup>
                </Marker>
              ))}

              {ripeNtpServerLoc && measurementNtpServerLoc && vantagePointLoc &&
              <>
                <Marker position = {vantagePointLoc ?? [0,0]} icon = {vantagePointIcon}>
                    <Popup>
                      Vantage Point<br/>
                      IP: {vantagePointIp}<br/>
                    </Popup>
                </Marker>
                <FitMapBounds probes={probe_locations} ripeNtpServer={ripeNtpServerLoc} measurementNtpServer = {measurementNtpServerLoc} vantagePoint = {vantagePointLoc}/>
                <DrawConnectingLines probes={probe_locations} ripeNtpServer={ripeNtpServerLoc} measurementNtpServer = {measurementNtpServerLoc} vantagePoint = {vantagePointLoc}/>
              </>}
            </>)}
        </MapContainer>
          <div style={{display: "flex", gap: "10px", alignItems: "center"}}>
            <div><img src = {ntpServerImg} className="logo"/>: NTP Servers</div>
            <div><img src = {vantagePointImg} className="logo"/>: Vantage Point</div>
            <div><img src = {greenProbeImg} className="logo"/>: &lt; 15 ms RTT</div>
            <div><img src = {yellowProbeImg} className="logo"/>: &lt; 40 ms RTT</div>
            <div><img src = {redProbeImg} className="logo"/>: &lt; 150 ms RTT</div>
            <div><img src = {darkRedProbeImg} className="logo"/>: &gt; 150 ms RTT</div>
            <div><img src = {grayProbeImg} className="logo"/>: No response</div>
          </div>
      </div>
    )
}