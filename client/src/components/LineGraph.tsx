import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    ChartOptions,
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

/**
 *
 * @param labels The "timeline" of timestamps on the X axis
 * @param data the actual data points
 * @param formatter the specified way to format the X axis based on the selected option
 * @returns the data, aligned with the timeline, or null if no measurements were performed at a given time
 */
function alignDataWithTimeline(labels: string[], data: NTPData[], formatter: (date: Date) => string) : (NTPData | null)[] {

  const map = new Map<string, NTPData>()
  for (const d of data) {
    const label = formatter(new Date(d.time))
    if (!map.has(label)) {
      map.set(label, d)
    }
  }
  return labels.map(label => map.get(label) ?? null);
}


export default function LineChart({data, selectedMeasurement, selectedOption}: ChartInputData) {
    const measurementMap = {
        RTT: 'Round-trip time (s)',
        offset: 'Offset (s)'
    }
    if (data == null)
      return null

    //sort data chronologically
    const sortedData = [...data].sort((a, b) => new Date(a.time).getTime() - new Date(b.time).getTime())

    const now = new Date()

    //
    // format X axis labels based on which time interval is selected
    //
    let formatter: (date: Date) => string
    // start and end points, these can be modified for custom intervals
    let startingPoint = new Date(now)
    let endPoint = new Date(now)

    let datapoints_no = 2
    switch (selectedOption) {
      case "Last Hour":
        formatter = (d) => d.toLocaleTimeString([], { hour: "numeric", minute: "numeric" })
        datapoints_no = 6
        startingPoint.setHours(now.getHours() - 1)
        break
      case "Last Day":
        formatter = (d) => d.toLocaleTimeString([], { hour: "numeric" })
        datapoints_no = 12
        startingPoint.setDate(now.getDate() - 1)
        break
      case "Last Week":
        formatter = (d) => d.toLocaleDateString([], { day: "2-digit", month: "short"})
        datapoints_no = 7
        startingPoint.setDate(now.getDate() - 7)
        break
      case "Custom":
        //TODO
        //Here we will have the logic for setting the endpoint and starting point in case of a custom measurement
        //
          datapoints_no = 2
          formatter = (d) => d.toLocaleTimeString()
          break
      default:
        datapoints_no = 2
        formatter = (d) => d.toLocaleTimeString()
    }
   //
   //generate time labels on the X axis based on given formatting
   //
    const generateLabels = (start: Date, end: Date, datapoints_no: number): string[] => {
      const step = (end.getTime() - start.getTime()) / (datapoints_no - 1)
      const labels = [];
      for (let i = 0; i < datapoints_no; i++) {
        const timestamp = new Date(start.getTime() + i * step);
        labels.push(formatter(timestamp))
      }
     return labels
    }

    const labels = generateLabels(startingPoint, endPoint, datapoints_no)

    // align data with timeline to make sure measurements start in correct spots
    const alignedData = alignDataWithTimeline(labels, sortedData, formatter)

    const yValues = alignedData
      .filter((d): d is NTPData => d !== null)
      .map(d => d[selectedMeasurement]);

    let minY = 0, maxY = 1; // fallback values
    if (yValues.length > 0) {
      const dataMin = Math.min(...yValues);
      const dataMax = Math.max(...yValues);
      const range = dataMax - dataMin || 1; // avoid zero range
      minY = dataMin - range * 0.1;
      maxY = dataMax + range * 0.1;
      // Optionally, force minY to 0 for RTT
      if (selectedMeasurement === "RTT" && minY > 0) minY = 0;
    }

    const options: ChartOptions<'line'> = {
      spanGaps: true,
      responsive: true,
      interaction: {
        mode: 'nearest' as const,
        intersect: false,
      },
      plugins: {
        legend: {
          position: 'top' as const,
        },
        title: {
          display: false,
          text: 'Measurement time',
        },
        tooltip: {
          enabled: true,
        }
      },
      scales: {
        x: {
          type: 'category',
          labels: labels,
          ticks: {
            maxTicksLimit: 20
          }
        },
         y: {
          //TODO: Make this cleaner in the future if there are other options, for now works like this
          // min: selectedMeasurement === "offset" ? -1 : 0,
          // max: selectedMeasurement === "offset" ? 1 : 0.1,
          // ticks: {
          //   stepSize: selectedMeasurement === "offset" ? 0.2 : 0.01
          // },


          min: minY,
          max: maxY,
        },
      },
    }

    const chartData = {
        datasets: [
            {
                label: measurementMap[selectedMeasurement],
                data: alignedData.map(d => d != null ? d[selectedMeasurement] : 0),
                borderColor: 'rgba(53, 162, 235, 0.8)',
                backgroundColor: 'rgba(236, 240, 243, 0.3)',
                color: 'rgb(255, 255, 255)',
                tension: 0,
                pointRadius: 0
            }
        ]
    }
  return <Line options={options} data={chartData} />
}