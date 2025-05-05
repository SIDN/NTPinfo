import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
ChartJS.defaults.color = 'rgba(239,246,238,1)'

type NTPData = {
    offset: number;
    delay: number;
    stratum: number;
    jitter: number;
    reachability: number;
    passing: boolean;
    time: number;
};

type Measurement = 'delay' | 'offset'
  
type ChartInputData = {
    data: NTPData[];
    selectedMeasurement: Measurement;
};

// Register the required components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

// Line chart options
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

export default function LineChart({data, selectedMeasurement}: ChartInputData) {
    const measurementMap = {
        delay: 'Delay (ms)',
        offset: 'Offset (ms)'
    };

    const chartData = {
        labels: data.map(d => new Date(d.time).toLocaleTimeString()),
        datasets: [
            {
                label: measurementMap[selectedMeasurement],
                data: data.map(d => d[selectedMeasurement]),
                borderColor: 'rgba(53, 162, 235, 0.8)',
                backgroundColor: 'rgba(236, 240, 243, 0.3)',
                color: 'rgb(255, 255, 255)',
                tension: 0.1
            }
        ]
    };
  return <Line options={options} data={chartData} />;
}