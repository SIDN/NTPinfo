import React, { useState } from 'react';
import '../styles/Sidebar.css';

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
      icon: <span className="sidebar__icon">🏠</span>,
    },
    {
      id: 2,
      label: 'Historical Data',
      icon: <span className="sidebar__icon">📈</span>,
    },
    {
      id: 3,
      label: 'Compare',
      icon: <span className="sidebar__icon">📊</span>,
    },
    {
      id: 4,
      label: 'About',
      icon: <span className="sidebar__icon">ℹ️</span>,
    },
  ];

  return (
    <aside className={`sidebar ${open ? 'open' : 'closed'}`}>
      <button
        className="sidebar__toggle"
        onClick={() => setOpen(!open)}
        aria-label="Toggle sidebar"
      >
        ☰
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