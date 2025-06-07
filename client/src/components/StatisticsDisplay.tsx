import React from 'react';
import { NTPData } from '../utils/types';
import { Measurement } from '../utils/types';

interface StatisticsDisplayProps {
  data: Map<string, NTPData[]> | null;
  selectedMeasurement: Measurement;
  selectedOption: string;
  customRange?: { from: string; to: string };
}

const StatisticsDisplay: React.FC<StatisticsDisplayProps> = ({
  data,
  selectedMeasurement,
  selectedOption,
  customRange,
}) => {
  if (!data) return null;

  const calculateStats = (serverData: NTPData[]) => {
    const values = serverData.map(d => d[selectedMeasurement]);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const avg = values.reduce((a, b) => a + b, 0) / values.length;

    return {
      min: min.toFixed(6),
      max: max.toFixed(6),
      avg: avg.toFixed(6),
    };
  };

  return (
    <div className="statistics-container">
      {Array.from(data.entries()).map(([server, serverData]) => {
        const stats = calculateStats(serverData);
        return (
          <div key={server} className="server-stats">
            <h3>{server}</h3>
            <div className="stats-grid">
              <div className="stat-item">
                <span className="stat-label">Min:</span>
                <span className="stat-value">{stats.min}s</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Max:</span>
                <span className="stat-value">{stats.max}s</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Average:</span>
                <span className="stat-value">{stats.avg}s</span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default StatisticsDisplay;