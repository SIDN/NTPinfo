import L from 'leaflet'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'
import { MapContainer, Marker, Popup, TileLayer } from 'react-leaflet'

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
  vantagePoint: L.LatLngExpression
  probes: L.LatLngExpression[]
  ntpServer: L.LatLngExpression
}

export default function WorldMap ({vantagePoint, probes, ntpServer}: MapComponentProps) {
    return (
        <MapContainer center = {vantagePoint} zoom = {13} style={{height: '500px', width: '100%'}}>
            <TileLayer 
                url = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />

            <Marker position = {vantagePoint}>
                <Popup>Vantage Point</Popup>
            </Marker>
            
            {probes.map((pos, index) => (<Marker key = {index} position = {pos}/>))}

            <Marker position = {ntpServer}>
                <Popup>NTP Server</Popup>
            </Marker>
        </MapContainer>
    )
}