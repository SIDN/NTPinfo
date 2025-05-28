import L, { LatLngExpression } from 'leaflet'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet'
import { useEffect } from 'react'
import { NTPData } from '../utils/types'

delete (L.Icon.Default.prototype as any)._getIconUrl

L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  shadowUrl: markerShadow
})
/*
const blueIcon = new L.Icon({
  iconUrl: '/icons/blue-marker.png',
  iconSize: [21, 34],
  iconAnchor: [10, 34],
  popupAnchor: [0, -30]
})

const greenIcon = new L.Icon({
  iconUrl: '/icons/green-marker.png',
  iconSize: [21, 34],
  iconAnchor: [10, 34],
  popupAnchor: [0, -30]
})

const redIcon = new L.Icon({
  iconUrl: '/icons/red-marker.png',
  iconSize: [21, 34],
  iconAnchor: [10, 34],
  popupAnchor: [0, -30]
})*/

interface MapComponentProps {
  probes: [NTPData,L.LatLngExpression][]
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

export default function WorldMap ({probes, ntpServer}: MapComponentProps) {
  const probe_location = probes.map(x => x[1])
    return (
        <MapContainer  style={{height: '500px', width: '100%'}}>
            <TileLayer 
                url = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                attribution= '&copy; <a href="https://carto.com/">CARTO</a>'
                subdomains={['a', 'b', 'c', 'd']}
                maxZoom={19}
            />
            
            {probe_location.map((pos, index) => (<Marker key = {index} position = {pos}>
              <Popup>
                Probe ID: 11012<br/>
                Offset: {probes[index][0].offset.toString()}<br/>
                RTT: {probes[index][0].RTT.toString()}
              </Popup>
            </Marker>))}

            <Marker position = {ntpServer}>
                <Popup>
                  NTP Server<br/>
                  IP: {probes[0][0].ip}<br/>
                  Name: {probes[0][0].server_name}
                </Popup>
            </Marker>
            <FitMapBounds probes={probe_location} ntpServer={ntpServer}/>
            <DrawConnectingLines probes={probe_location} ntpServer={ntpServer}/>
        </MapContainer>
    )
}