import React, { useState, useEffect } from 'react';
import { NTPData } from '../utils/types.ts';
import { Measurement } from '../utils/types.ts';
import Header from '../components/Header.tsx';
import StatisticsDisplay from '../components/StatisticsDisplay';
import DynamicGraph from '../components/DynamicGraph.tsx';
import '../styles/HistoricalDataTab.css';

// Define the props interface
interface HistoricalDataTabProps {
  data: Map<string, NTPData[]> | null;
}

// Create a functional component
const HistoricalDataTab: React.FC<HistoricalDataTabProps> = ({ data }) => {
  const [selMeasurement, setSelMeasurement] = useState<Measurement>("RTT");
  const [currentServer, setCurrentServer] = useState<string>("");

  // Extract server name from the initial data prop
  useEffect(() => {
    if (data && data.size > 0) {
      const serverName = Array.from(data.keys())[0];
      setCurrentServer(serverName);
    }
  }, [data]);

  return (
    <div className="historical-data-tab">
      <Header />
      <div className="graph-statistics-container">
        <div className="data-display-container">
          <StatisticsDisplay
            data={data}
            selectedMeasurement={selMeasurement}
          />
          <div className="chart-box">
            <DynamicGraph
              servers={currentServer ? [currentServer] : []}
              selectedMeasurement={selMeasurement}
              onMeasurementChange={setSelMeasurement}
              legendDisplay={false}
              showTimeInput={true}
              existingData={data}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default HistoricalDataTab