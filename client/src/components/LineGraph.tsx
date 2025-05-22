import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js'
import { Line } from 'react-chartjs-2'
ChartJS.defaults.color = 'rgba(239,246,238,1)'
import { NTPData } from '../utils/types.ts'
import { Measurement } from '../utils/types.ts'
  
type ChartInputData = {
    data: NTPData[] | null
    selectedMeasurement: Measurement
    selectedOption: string
}

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

const options = {
  responsive: true,
  plugins: {
    legend: {
      position: 'top' as const,
    },
    title: {
      display: false,
      text: 'Measurement time',
    },
  },
};

export default function LineChart({data, selectedMeasurement, selectedOption}: ChartInputData) {
    const measurementMap = {
        RTT: 'Round-trip time (ms)',
        offset: 'Offset (ms)'
    }
    if (data == null)
      return null
    
    //sort data chronologically
    const sortedData = [...data].sort((a, b) => new Date(a.time).getTime() - new Date(b.time).getTime())
    
    const now = new Date()

    
    // format X axis labels based on which time interval is selected
    let formatter: (date: Date) => string
    let startingPoint = new Date(now)
    // let endPoint = Date.now()
    let datapoints_no = 1 
    switch (selectedOption) {
      case "Last Hour":
        formatter = (d) => d.toLocaleTimeString([], { hour: "numeric", minute: "numeric" })
        datapoints_no = 6
        startingPoint.setHours(now.getHours() - 1)
        break
      case "Last Day":
        formatter = (d) => d.toLocaleTimeString([], { hour: "numeric" })
        datapoints_no = 24
        startingPoint.setDate(now.getDate() - 1)
        break
      case "Last Week":
        formatter = (d) => d.toLocaleDateString([], { day: "2-digit", month: "short"})
        datapoints_no = 7
        startingPoint.setDate(now.getDate() - 7)
        break
      default:
        formatter = (d) => d.toLocaleTimeString();
    }
    

    // set a number of datapoints to make the chart less crowded
    const step = Math.ceil(sortedData.length / datapoints_no)
    const sampled = sortedData.filter((_, index) => index % step === 0).slice(0, datapoints_no)

    const chartData = {
        labels: sampled.map((d) => formatter(new Date(d.time))),
        datasets: [
            {
                label: measurementMap[selectedMeasurement],
                data: sortedData.map(d => d[selectedMeasurement]),
                borderColor: 'rgba(53, 162, 235, 0.8)',
                backgroundColor: 'rgba(236, 240, 243, 0.3)',
                color: 'rgb(255, 255, 255)',
                tension: 0.1
            }
        ]
    }
  return <Line options={options} data={chartData} />
}