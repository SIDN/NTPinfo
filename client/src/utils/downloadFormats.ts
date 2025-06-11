import { NTPData, RIPEData } from '../utils/types.ts'
type InputData = (NTPData | RIPEData)[]


/**
 * Downloads the measurement data in a JSON format.
 * @param data array of measurements to be downloaded
 */
export function downloadJSON(data : InputData) {
    //parse to json string and make an object with the corresponding data
    const labeledData = data.map((entry) => ({
    type: 'probe_id' in entry ? 'RIPE Data' : 'NTP Data',
      ...entry
    }));
  const json = JSON.stringify(labeledData, null, 2);
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

  const labeledData: Record<string, unknown>[] = data.map((entry) => ({
    type: 'probe_id' in entry ? 'RIPE Data' : 'NTP Data',
    ...entry
  }));

  // Collect all unique headers across all entries (including type)
  const headersSet = new Set<string>();
  labeledData.forEach((entry) => {
    Object.keys(entry).forEach((key) => headersSet.add(key));
  });
  //get headers of csv
  const headers = Array.from(headersSet)
  const values = labeledData.map((entry) =>
    headers.map((key) => JSON.stringify((entry)[key] ?? '')).join(',')
  );


  const csvData = [headers.join(','), ...values].join('\n')
  const blob = new Blob([csvData], {type: 'text/csv'});
  //create a temporary download link for the data
  const downloadLink = document.createElement('a');
  downloadLink.href = window.URL.createObjectURL(blob)
  downloadLink.download = "data.csv"
  downloadLink.click()
  window.URL.revokeObjectURL(downloadLink.href)

}
