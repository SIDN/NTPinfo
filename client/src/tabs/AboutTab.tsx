import React from 'react';
import '../styles/AboutTab.css';
import Header from '../components/Header';
import DataAnalysis from '../assets/chart-svgrepo-com.png';
import Visualization from '../assets/graph-svgrepo-com.png';
import Comparison from '../assets/scale-unbalanced-svgrepo-com.png';

const AboutTab: React.FC = () => {
  return (
    <div className="about-tab">
      <Header />
      <div className="about-section">
        <h1>Welcome to our NTP measurement tool</h1>
        <p className="about-subtitle">
          This is an open-source tool for measuring the accuracy of NTP servers, made by 5 students from Delft University of Technology, hosted by SIDN Labs.
        </p>
        <div className="about-features">
          <div className="feature">
            <span className="feature-icon"><img src={DataAnalysis} alt="Data Analysis" /></span>
            <h3>Data Analysis</h3>
            <p>Comprehensive tools for analyzing NTP data</p>
          </div>
          <div className="feature">
            <span className="feature-icon"><img src={Visualization} alt="Visualization" /></span>
            <h3>Visualization</h3>
            <p>Interactive graphs for better understanding of NTP data</p>
          </div>
          <div className="feature">
            <span className="feature-icon"><img src={Comparison} alt="Comparison" /></span>
            <h3>Comparison</h3>
            <p>Compare different servers to gain deeper insights</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutTab