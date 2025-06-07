import React, { useState } from 'react';
import { NTPData } from '../utils/types.ts';
import LineChart from '../components/LineGraph';
import { Measurement } from '../utils/types.ts';
import { TimeInput } from '../components/TimeInput.tsx';
import Hero from '../components/Hero';
import StatisticsDisplay from '../components/StatisticsDisplay';
import '../styles/HistoricalDataTab.css';

// Define the props interface
interface HistoricalDataTabProps {
  data: Map<string, NTPData[]> | null;
}

// Create a functional component
const HistoricalDataTab: React.FC<HistoricalDataTabProps> = ({ data }) => {
  const [selMeasurement, setSelMeasurement] = useState<Measurement>("RTT");
  const [selOption, setSelOption] = useState("Last Day");
  const [customFrom, setCustomFrom] = useState<string>("");
  const [customTo, setCustomTo] = useState<string>("");

  const handleMeasurementChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSelMeasurement(event.target.value as Measurement);
  };

  const dropdown = {
    options: ["Last Hour", "Last Day", "Last Week", "Custom"],
    selectedOption: selOption,
    onSelectionChange: setSelOption,
  };

  return (
    <div className="historical-data-tab">
      <Hero />
      <div className="form-row">
        <TimeInput
          options={dropdown.options}
          selectedOption={selOption}
          onSelectionChange={setSelOption}
          customFrom={customFrom}
          customTo={customTo}
          onFromChange={setCustomFrom}
          onToChange={setCustomTo}
        />

        <div className="radio-group">
          <label className="radio-measurement-label">
            <input
              type="radio"
              name="measurement-tab"
              value="offset"
              checked={selMeasurement === "offset"}
              onChange={handleMeasurementChange}
            />
            Offset
          </label>
          <label className="radio-measurement-label">
            <input
              type="radio"
              name="measurement-tab"
              value="RTT"
              checked={selMeasurement === "RTT"}
              onChange={handleMeasurementChange}
            />
            Round-trip time
          </label>
        </div>
      </div>
      <div className="graph-statistics-container">
        <div className="data-display-container">
            <StatisticsDisplay
            data={data}
            selectedMeasurement={selMeasurement}
            selectedOption={selOption}
            customRange={{ from: customFrom, to: customTo }}
            />
            <div className="chart-box">
            <LineChart
                data={data}
                selectedMeasurement={selMeasurement}
                selectedOption={selOption}
                customRange={{ from: customFrom, to: customTo }}
            />
            </div>
        </div>
      </div>
    </div>
  );
};

export default HistoricalDataTab;
