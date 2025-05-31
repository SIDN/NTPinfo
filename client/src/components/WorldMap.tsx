import L from 'leaflet'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet'
import { useEffect, useState } from 'react'
import { RIPEData } from '../utils/types'
import greenProbeImg from '../assets/green-probe.png'
import yellowProbeImg from '../assets/yellow-probe.png'
import redProbeImg from '../assets/red-probe.png'
import darkRedProbeImg from '../assets/dark-red-probe.png'
import grayProbeImg from '../assets/gray-probe.png'

/**
 * Standard code added for the proper functioning of the default icon when using Leaflet with Vite
 */
delete (L.Icon.Default.prototype as any)._getIconUrl

L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  shadowUrl: markerShadow
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

/**
 * Interface used in assigning values to the map component
 */
interface MapComponentProps {
  probes: RIPEData[] | null
  ntpServer: L.LatLngExpression
  err: Error | null
}

/**
 * A function that sets the zoom of the map to an appropiate value depeding on how spread out all the geolocations are
 * Depends on the size of the map component on the page
 * Made to change the zoom in a responsive way with the change of the map size
 * @param probes the geolocation of all the probes to the shown on the map
 * @param probes the geolocation of the NTP server that the measurement was performed on
 */
const FitMapBounds = ({probes, ntpServer}: {probes: L.LatLngExpression[], ntpServer: L.LatLngExpression}) => {
  const map = useMap()

  useEffect(() => {
    const fitBounds = () => {
      const allPoints = [...probes, ntpServer]
      const bounds = L.latLngBounds(allPoints)
      map.fitBounds(bounds, { padding: [15, 15] })
    }

    fitBounds()

    const handleWindowResize = () => {
      requestAnimationFrame(() => {
        fitBounds()
      })
    }
    window.addEventListener('resize', handleWindowResize)
    return () => {window.removeEventListener('resize', handleWindowResize)}
  }, [map, probes, ntpServer])

  return null
}

/**
 * A function to draw connecting lines from each probe to the NTP server on the map
 * @param probes the geolocation of all the probes to the shown on the map
 * @param probes the geolocation of the NTP server that the measurement was performed on
 */
const DrawConnectingLines = ({probes, ntpServer}: {probes: L.LatLngExpression[], ntpServer: L.LatLngExpression}) => {
  const map = useMap()

  useEffect(() => {
    probes.map(x => {
      L.polyline([x,ntpServer], {color: 'blue', opacity: 0.8}).addTo(map)
    })
  },[map, probes, ntpServer])

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
  if (value === -1) return "No Reply"
  else return value.toString()
}

/**
 * The function for creating the WorldMap Component
 * Shows error text in case that an error occurs in fetching RIPE Data
 * Used a base tile map offered by Carto, specifically the Dark Matter basemap
 * Each probe is shown on the map with an icon of a different color depending on the RTT measured by it
 * Each probe has a popup which shows the following:
 *  The RIPE probe ID, with a link to its page on the RIPE Atlas website
 *  The RTT measured
 *  The offset measured
 * The NTP server has a popup showing the following:
 *  The name of the NTP server
 *  The IP of the specifc NTP server which was used
 * The map has lines drawn in between each probe and the NTP server for better visualization
 * The map's zoom get automatically readjusted depending on the size of the map on the page
 * @param probes Data of all the measured probes, as an array of RIPEData values
 * @param ntpServer The geolocation of the NTP server
 * @param err a value containing an Error if an error occured when fetching the RIPE measurements
 * @returns a WorldMap component showing all probes, the NTP server and relevant values for all of them
 */
export default function WorldMap ({probes, ntpServer, err}: MapComponentProps) {
  const [statusMessage, setStatusMessage] = useState<string>("")
  useEffect(() => {
    if (probes == null) {
        if (err)
            setStatusMessage("Unknown error occurred")
        }
    }, [probes, err])

  if(probes == null)
    return <h2 id="not-found">{err ? `Error unknown: ${statusMessage}` : `Unknown error occurred`}</h2>

  const probe_locations = probes?.map(x => x.probe_location) ?? []
  const icons = probes?.map(x => getIconByRTT(x.measurementData.RTT, x.got_results)) ?? []
    return ( 
        <MapContainer  style={{height: '500px', width: '100%'}}>
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
                  RTT: {stringifyRTTAndOffset(probes[index].measurementData.RTT)}
                </Popup>
              </Marker>))}

              <Marker position = {ntpServer}>
                  <Popup>
                    NTP Server<br/>
                    IP: {probes[0].measurementData.ip}<br/>
                    Name: {probes[0].measurementData.server_name}
                  </Popup>
              </Marker>
              <FitMapBounds probes={probe_locations} ntpServer={ntpServer}/>
              <DrawConnectingLines probes={probe_locations} ntpServer={ntpServer}/>
            </>)}
        </MapContainer>
    )
}