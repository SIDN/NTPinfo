import { NTPData } from '../utils/types.ts'
type InputData = {
  data: NTPData[]
}

/**
 * Downloads the measurement data in a JSON format.
 * @param data array of measurements to be downloaded
 */
export function downloadJSON(data : InputData) {
    //parse to json string and make an object with the corresponding data
  const json = JSON.stringify(data);
  const blob = new Blob([json], {type: 'application/json'});
  //create a temporary download link for the data
  const downloadLink = document.createElement('a');
  downloadLink.href = window.URL.createObjectURL(blob)
  downloadLink.download = "data.json"
  downloadLink.click()
  window.URL.revokeObjectURL(downloadLink.href)

}
/**
 * Downloads the measurement data in a CSV format.
 * @param data array of measurements to be downloaded
 */
export function downloadCSV(data : InputData) {

  const json = JSON.parse(JSON.stringify(data));
  //get headers of csv
  const headers = Object.keys(json.data[0])
  const values = json.data.map((row : NTPData) =>
      headers.map((key) => JSON.stringify((row as any)[key])).join(','))

  const csvData = [headers.join(','), ...values].join('\n')
  const blob = new Blob([csvData], {type: 'text/csv'});
  //create a temporary download link for the data
  const downloadLink = document.createElement('a');
  downloadLink.href = window.URL.createObjectURL(blob)
  downloadLink.download = "data.csv"
  downloadLink.click()
  window.URL.revokeObjectURL(downloadLink.href)

}
