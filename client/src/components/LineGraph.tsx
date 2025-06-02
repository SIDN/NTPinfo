import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    TimeScale,
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
import 'chartjs-adapter-date-fns';

type ChartInputData = {
    data: NTPData[] | null
    selectedMeasurement: Measurement
    selectedOption: string
    customRange?: { from: string; to: string }
}

ChartJS.register(CategoryScale, LinearScale, TimeScale, PointElement, LineElement, Title, Tooltip, Legend)

/**
 * Remove points that are closer than `thresholdMs` to the previous *kept* point.
 * – `pts` must be time-sorted (you already have `sortedData` for that)
 * – Returns a new array; does NOT mutate the input.
 */
function thinByProximity<T extends { time: string | number | Date }>(
  pts: T[],
  thresholdMs: number
): T[] {
  if (pts.length === 0) return [];
  const out: T[] = [pts[0]];
  let last = new Date(pts[0].time).getTime();

  for (let i = 1; i < pts.length; i++) {
    const t = new Date(pts[i].time).getTime();
    if (t - last >= thresholdMs) {     // keep only if far enough apart
      out.push(pts[i]);
      last = t;
    }
  }
  return out;
}

function unitForSpan(spanMs: number): { unit: 'second'|'minute'|'hour'|'day'|'month'|'year', fmt: string } {
  const s = 1000, m = 60*s, h = 60*m, d = 24*h, y = 365*d;

  if (spanMs <= 2*h)          return { unit: 'minute', fmt: 'HH:mm' };       // up to ~2 h → show minutes
  if (spanMs <= 2*d)          return { unit: 'hour',   fmt: 'HH:mm' };       // up to ~2 days → hours
  if (spanMs <= 90*d)         return { unit: 'day',    fmt: 'dd MMM' };      // up to 3 months → days
  if (spanMs <= 2*y)          return { unit: 'month',  fmt: 'MMM yyyy' };    // up to 2 years → months
  return                        { unit: 'year',   fmt: 'yyyy' };             // above 2 years → years
}

export default function LineChart({data, selectedMeasurement, selectedOption, customRange}: ChartInputData) {
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
  let customTimeUnit: 'second'|'minute'|'hour'|'day'|'month'|'year' | null = null;
  let customFmt = '';

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
      if (customRange?.from) startingPoint = new Date(customRange.from);
      if (customRange?.to)   endPoint     = new Date(customRange.to);

      const { unit, fmt } = unitForSpan(endPoint.getTime() - startingPoint.getTime());

      formatter      = (d: Date) => d.toLocaleString();
      customTimeUnit = unit;
      customFmt      = fmt;
      break;
    default:
      datapoints_no = 2
      formatter = (d) => d.toLocaleTimeString()
  }

  const SAMPLE_DENSITY = 100;  // tweak this one knob only

  const axisMs     = endPoint.getTime() - startingPoint.getTime();
  const thresholdMs =
        SAMPLE_DENSITY > 0 && axisMs > 0
          ? axisMs / SAMPLE_DENSITY
          : 0;

  const thinned = thinByProximity(sortedData, thresholdMs);

  const points = thinned.map(d => ({
    x: new Date(d.time).toISOString(),
    y: d[selectedMeasurement]
  }))

  const yValues = points.map(p => p.y);
  let minY = 0, maxY = 1;
  if (yValues.length) {
    const minV = Math.min(...yValues);
    const maxV = Math.max(...yValues);
    const pad  = (maxV - minV || 1) * 0.1; // 10% padding above and below the min/max values
    minY = minV - pad;
    maxY = maxV + pad;
    if (selectedMeasurement === 'RTT' && minY < 0.01) minY = 0; // fix floating point error
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
        type: 'time',
        min : startingPoint.toISOString(),
        max : endPoint.toISOString(),
        time: {
          unit:  selectedOption === "Custom" && customTimeUnit
                   ? customTimeUnit
                   : selectedOption === "Last Hour" ? 'minute'
                   : selectedOption === "Last Day"  ? 'hour'
                   : 'day',
          displayFormats: {
            minute: 'HH:mm',
            hour  : 'HH:mm',
            day   : 'dd MMM',
            month : 'MMM yyyy',
            year  : 'yyyy',
            // override on custom
            ...(selectedOption === "Custom" && customTimeUnit
              ? { [customTimeUnit]: customFmt }
              : {}),
          },
        }
      },
        y: {
        min: minY,
        max: maxY,
      },
    },
  }

  const chartData = {
    datasets: [
      {
        label: measurementMap[selectedMeasurement],
        data: points,
        borderColor: 'rgba(53, 162, 235, 0.8)',
        backgroundColor: 'rgba(236, 240, 243, 0.3)',
        color: 'rgb(255, 255, 255)',
        tension: 0,
        pointRadius: 3
      }
    ]
  }

  return <Line options={options} data={chartData} />
}