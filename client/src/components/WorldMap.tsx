import L, { LatLngTuple } from 'leaflet'
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
import unavailableNtpImg from '../assets/unavailable-ntp-server-icon.png'

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

const unavailableNtpServerIcon = new L.Icon({
  iconUrl: unavailableNtpImg,
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
  vantagePointInfo: [LatLngTuple,string] | null
  status: string | null
}

type LocationInfo = {
  location: LatLngTuple
  ip: string
  server_name: string
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
const FitMapBounds = ({probes, ripeNtpServers, measurementNtpServers, intersectionNtpServers, unavailableNtpServers, vantagePoint}: {probes: LatLngTuple[], 
  ripeNtpServers: LatLngTuple[], measurementNtpServers: LatLngTuple[], intersectionNtpServers: LatLngTuple[], unavailableNtpServers: LatLngTuple[], vantagePoint: LatLngTuple}) => {
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
    if (probes.length === 0 || !vantagePoint) return
    
    if (userInteracted.current) return

    const fitBounds = () => {
      const allPoints = [...probes, ...ripeNtpServers, ...measurementNtpServers, ...intersectionNtpServers, ...unavailableNtpServers, vantagePoint]
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
  }, [map, probes, ripeNtpServers, measurementNtpServers, intersectionNtpServers, unavailableNtpServers])

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
const DrawConnectingLines = ({probes, measurementNtpServers, intersectionNtpServers, unavailableNtpServers, vantagePoint}: {probes: RIPEData[], 
  measurementNtpServers: LatLngTuple[], intersectionNtpServers: LatLngTuple[], unavailableNtpServers: LatLngTuple[], vantagePoint: LatLngTuple}) => {
  const map = useMap()

  useEffect(() => {
    if (!vantagePoint || probes.length === 0) return
    probes.map(x => {
      L.polyline([x.probe_location,x.measurementData.coordinates], {color: 'blue', opacity: 0.8, weight: 1}).addTo(map)
    })
    measurementNtpServers.map(x => {
      L.polyline([x,vantagePoint], {color:'blue', opacity: 0.8, weight: 1}).addTo(map)
    })
    intersectionNtpServers.map(x => {
      L.polyline([x,vantagePoint], {color:'blue', opacity: 0.8, weight: 1}).addTo(map)
    })
    unavailableNtpServers.map(x => {
      L.polyline([x,vantagePoint], {color:'gray', opacity: 0.8, weight: 1}).addTo(map)
    })
  },[map, probes, measurementNtpServers, intersectionNtpServers, unavailableNtpServers])

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
export default function WorldMap ({probes, ntpServers, vantagePointInfo, status}: MapComponentProps) {
  const [statusMessage, setStatusMessage] = useState<string>("")

  const [ripeOnlyLocations, setRipeOnlyLocations] = useState<LocationInfo[]>([])
  const [ntpOnlyLocations, setNtpOnlyLocations] = useState<LocationInfo[]>([])
  const [intersectedLocations, setIntersectedLocations] = useState<LocationInfo[]>([])
  const [failedLocations, setFailedLocations] = useState<LocationInfo[]>([])

  const [isAnycast, setIsAnycast] = useState<boolean>(false)

  useEffect(() => {
    if (!probes || !ntpServers) return
    
    const probeIPMap = new Map<String, RIPEData>()

    const ripeLocations = new Map<string, LocationInfo>()
    const ntpLocations = new Map<string, LocationInfo>()
    const failedLocations = new Map<string, LocationInfo>()

    for (const probe of probes) {
      const ip = probe.measurementData.ip
      const loc = probe.measurementData.coordinates
      const locStr = loc.join(',')
      const server_name = probe.measurementData.server_name
      probeIPMap.set(ip, probe)
      ripeLocations.set(locStr, { location: loc, ip, server_name })
    }
    
    const probeIps = new Set(probeIPMap.keys())
    const inMeasurements = ntpServers.filter(x => !probeIps.has(x.ip))
    const unavailable = inMeasurements.filter(x => x.RTT === -1)

    for (const ntp of ntpServers) {
      const loc = ntp.coordinates
      const locStr = loc.join(',')
    ntpLocations.set(locStr, { location: loc, ip: ntp.ip, server_name: ntp.server_name })
    }

    for (const ntp of unavailable) {
      const loc = ntp.coordinates
      const locStr = loc.join(',')
      if (!ripeLocations.has(locStr)) {
      failedLocations.set(locStr, { location: loc, ip: ntp.ip, server_name: ntp.server_name })
      }
    }

    const intersected = new Map<string, LocationInfo>()
    const ripeOnly = new Map<string, LocationInfo>()
    const ntpOnly = new Map<string, LocationInfo>()

    for (const [locStr, info] of ripeLocations) {
      if (ntpLocations.has(locStr)) {
        intersected.set(locStr, info)
      } else {
        ripeOnly.set(locStr, info)
      }
    }

    for (const [locStr, info] of ntpLocations) {
      if (!ripeLocations.has(locStr)) {
        ntpOnly.set(locStr, info)
      }
    }

    setRipeOnlyLocations(Array.from(ripeOnly.values()))
    setNtpOnlyLocations(Array.from(ntpOnly.values()))
    setIntersectedLocations(Array.from(intersected.values()))
    setFailedLocations(Array.from(failedLocations.values()))
  }, [probes,ntpServers])

  useEffect(() => {
    if (!probes || !ntpServers) return

    setIsAnycast(probes.some(x => x.measurementData.is_anycast === true) || ntpServers.some(x => x.is_anycast === true))
  })

  /**
   * Effect to dynamically update the status shown depening on the progress of the RIPE measurement
   */
  useEffect(() => {
    if (status === "pending"){
      setRipeOnlyLocations([])
      setNtpOnlyLocations([])
      setIntersectedLocations([])
      setFailedLocations([])
      return 
    } else if (status === "partial_results"){
      setStatusMessage("Map Loading...")
    } else if(status === "complete" || status === "timeout") {
      setStatusMessage("Map Fully Loaded")
    } else if (status === "error") {
      setStatusMessage("Error loading RIPE data")
    }
    }, [probes, status])

  const probe_locations = probes?.map(x => x.probe_location) ?? []
  const icons = probes?.map(x => getIconByRTT(x.measurementData.RTT, x.got_results)) ?? []
  console.log(probes)
  console.log(ntpServers)
    return (
      <div style={{height: '500px', width: '100%'}}>
        <h2>{statusMessage}</h2>
        {isAnycast && <h2>This server uses Anycast. Server Geolocation might be inaccurate</h2>}
        <MapContainer style={{height: '100%', width: '100%'}}>
            <TileLayer 
                url = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                attribution= '&copy; <a href="https://carto.com/">CARTO</a>'
                subdomains={['a', 'b', 'c', 'd']}
                maxZoom={19}
            />
            
            {probe_locations && icons && probes && (
            <>
              {probe_locations.map((pos, index) => (<Marker key = {index} position = {pos} icon = {icons[index]}>
                <Popup>
                  Probe ID: <a href = {`https://atlas.ripe.net/probes/${probes[index].probe_id}/overview`} target='_blank' rel="noopener noreferrer">{probes[index].probe_id}</a><br/>
                  Offset: {stringifyRTTAndOffset(probes[index].measurementData.offset)}<br/>
                  RTT: {stringifyRTTAndOffset(probes[index].measurementData.RTT)}<br/>
                  Location: {pos[0]}, {pos[1]}
                </Popup>
              </Marker>))}

              {ripeOnlyLocations.map((x,index) => (
                <Marker key={index} position={x.location} icon={ntpServerIcon}>
                  <Popup>
                    NTP Server (RIPE)<br/>
                    IP: {x.ip}<br/>
                    Name: {x.server_name}
                    Location: {x.location}
                  </Popup>
                </Marker>
              ))}

              {ntpOnlyLocations.map((x,index) => (
                <Marker key={index} position={x.location} icon={ntpServerIcon}>
                  <Popup>
                    NTP Server (Vantage Point)<br/>
                    IP: {x.ip}<br/>
                    Name: {x.server_name}
                    Location: {x.location}
                  </Popup>
                </Marker>
              ))}

              {intersectedLocations.map((x,index) => (
                <Marker key={index} position={x.location} icon={ntpServerIcon}>
                  <Popup>
                    NTP Server<br/>
                    IP: {x.ip}<br/>
                    Name: {x.server_name}
                    Location: {x.location}
                  </Popup>
                </Marker>
              ))}

              {failedLocations.map((x,index) => (
                <Marker key={index} position={x.location} icon={unavailableNtpServerIcon}>
                  <Popup>
                    NTP Server (Unavailable)<br/>
                    IP: {x.ip}<br/>
                    Name: {x.server_name}
                    Location: {x.location}
                  </Popup>
                </Marker>
              ))}

              {vantagePointInfo &&
              <>
                <Marker position = {vantagePointInfo[0]} icon = {vantagePointIcon}>
                    <Popup>
                      Vantage Point<br/>
                      IP: {vantagePointInfo[1]}<br/>
                      Location: {vantagePointInfo[0]}
                    </Popup>
                </Marker>
                <FitMapBounds probes={probe_locations} ripeNtpServers={ripeOnlyLocations.map(x=>x.location)} measurementNtpServers = {ntpOnlyLocations.map(x=>x.location)}
                  intersectionNtpServers={intersectedLocations.map(x=>x.location)} unavailableNtpServers={failedLocations.map(x=>x.location)}
                  vantagePoint={vantagePointInfo[0]}/>
                <DrawConnectingLines probes={probes} measurementNtpServers = {ntpOnlyLocations.map(x=>x.location)}
                  intersectionNtpServers={intersectedLocations.map(x=>x.location)} unavailableNtpServers={failedLocations.map(x=>x.location)}
                  vantagePoint={vantagePointInfo[0]}/>
              </>}
            </>)}
        </MapContainer>
          <div style={{display: "flex", gap: "10px", alignItems: "center"}}>
            <div><img src = {ntpServerImg} className="logo"/>: NTP Servers</div>
            <div><img src = {unavailableNtpImg} className="logo"/>: Failing NTP Servers</div>
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