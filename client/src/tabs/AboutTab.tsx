import React from 'react';
import '../styles/AboutTab.css';
import Hero from '../components/Hero';

const AboutTab: React.FC = () => {
  return (
    <div className="about-tab">
      <Hero />
      <div className="hero-section">
        <h1>Welcome to our NTP measurement tool</h1>
        <p className="hero-subtitle">
          This is an open-source tool for measuring the accuracy of NTP servers, made by 5 students from Delft University of Technology, in collaboration with SIDN Labs.
        </p>
        <div className="hero-features">
          <div className="feature">
            <span className="feature-icon">📊</span>
            <h3>Data Analysis</h3>
            <p>Comprehensive tools for analyzing NTP data</p>
          </div>
          <div className="feature">
            <span className="feature-icon">📈</span>
            <h3>Visualization</h3>
            <p>Interactive graphs for better understanding of NTP data</p>
          </div>
          <div className="feature">
            <span className="feature-icon">🔄</span>
            <h3>Comparison</h3>
            <p>Compare different servers to gain deeper insights</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutTab