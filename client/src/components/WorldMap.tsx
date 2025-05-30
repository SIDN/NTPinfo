import L, { LatLngExpression } from 'leaflet'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet'
import { useEffect } from 'react'
import { RIPEData } from '../utils/types'
import greenProbeImg from '../assets/green-probe.png'
import yellowProbeImg from '../assets/yellow-probe.png'
import redProbeImg from '../assets/red-probe.png'
import darkRedProbeImg from '../assets/dark-red-probe.png'
import grayProbeImg from '../assets/gray-probe.png'

delete (L.Icon.Default.prototype as any)._getIconUrl

L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  shadowUrl: markerShadow
})

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

interface MapComponentProps {
  probes: RIPEData[]
  ntpServer: L.LatLngExpression
}

const FitMapBounds = ({probes, ntpServer}: {probes: L.LatLngExpression[], ntpServer: L.LatLngExpression}) => {
  const map = useMap()

  useEffect(() => {
    const allPoints = [...probes, ntpServer]
    const bounds = L.latLngBounds(allPoints)
    map.fitBounds(bounds, { padding: [15, 15] })
  }, [map, probes, ntpServer])

  return null
}

//draw lines from the probes to the NTP server
const DrawConnectingLines = ({probes, ntpServer}: {probes: L.LatLngExpression[], ntpServer: L.LatLngExpression}) => {
  const map = useMap()

  useEffect(() => {
    probes.map(x => {
      L.polyline([x,ntpServer], {color: 'blue', opacity: 0.8}).addTo(map)
    })
  },[map, probes, ntpServer])

  return null
}

const getIconByRTT = (rtt: number, measured: boolean): L.Icon => {
  if (measured == false) return grayIcon;
  if (rtt < 15) return greenIcon;
  if (rtt < 40) return yellowIcon;
  if (rtt < 150) return redIcon;
  return darkRedIcon;
}

const stringifyRTTAndOffset = (value: number): string => {
  if (value === -1) return "No Reply"
  else return value.toString()
}

export default function WorldMap ({probes, ntpServer}: MapComponentProps) {
  const probe_location = probes.map(x => x.probe_location)
  const icons = probes.map(x => getIconByRTT(x.measurementData.RTT, x.got_results))
    return (
        <MapContainer  style={{height: '500px', width: '100%'}}>
            <TileLayer 
                url = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                attribution= '&copy; <a href="https://carto.com/">CARTO</a>'
                subdomains={['a', 'b', 'c', 'd']}
                maxZoom={19}
            />
            
            {probe_location.map((pos, index) => (<Marker key = {index} position = {pos} icon = {icons[index]}>
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
            <FitMapBounds probes={probe_location} ntpServer={ntpServer}/>
            <DrawConnectingLines probes={probe_location} ntpServer={ntpServer}/>
        </MapContainer>
    )
}