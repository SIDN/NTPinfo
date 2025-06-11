import React, { useState } from 'react';
import '../styles/Sidebar.css';
import houseIcon from '../assets/house-svgrepo-com.png';
import compareIcon from '../assets/scale-unbalanced-svgrepo-com.png';
import graphIcon from '../assets/graph-svgrepo-com.png';
import aboutIcon from '../assets/info-square-svgrepo-com.png';
import hamburgerIcon from '../assets/hamburger-md-svgrepo-com.png';

interface SidebarProps {
  selectedTab: number;
  setSelectedTab: (tab: number) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ selectedTab, setSelectedTab }) => {
  const [open, setOpen] = useState(false);

  const navItems = [
    {
      id: 1,
      label: 'Home',
      icon: <img src={houseIcon} alt="Home" className="sidebar__icon" />,
    },
    {
      id: 2,
      label: 'Historical Data',
      icon: <img src={graphIcon} alt="Graph" className="sidebar__icon" />,
    },
    {
      id: 3,
      label: 'Compare',
      icon: <img src={compareIcon} alt="Compare" className="sidebar__icon" />,
    },
    {
      id: 4,
      label: 'About',
      icon: <img src={aboutIcon} alt="About" className="sidebar__icon" />,
    },
  ];

  return (
    <aside className={`sidebar ${open ? 'open' : 'closed'}`}>
      <button
        className="sidebar__toggle"
        onClick={() => setOpen(!open)}
        aria-label="Toggle sidebar"
      >
        <img src={hamburgerIcon} alt="Menu" className="sidebar__icon" />
      </button>

      <nav className="sidebar__nav">
        {navItems.map(({ id, label, icon }) => (
          <button
            key={id}
            className={`sidebar__item ${selectedTab === id ? 'active' : ''}`}
            onClick={() => setSelectedTab(id)}
            aria-current={selectedTab === id ? 'page' : undefined}
          >
            {icon}
            {open && <span className="sidebar__label">{label}</span>}
          </button>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar