import React, { createContext, useContext, useState } from 'react';

const TabsContext = createContext();

export function Tabs({ defaultValue, children, className = '' }) {
  const [activeTab, setActiveTab] = useState(defaultValue);

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className={`tabs-container ${className}`}>
        {children}
      </div>
    </TabsContext.Provider>
  );
}

export function TabsList({ children, className = '' }) {
  return (
    <div
      className={`tabs-list ${className}`}
      style={{
        display: 'flex',
        borderBottom: '2px solid #E2E8F0',
        marginBottom: '24px',
        gap: '8px'
      }}
    >
      {children}
    </div>
  );
}

export function TabsTrigger({ value, children, className = '' }) {
  const { activeTab, setActiveTab } = useContext(TabsContext);
  const isActive = activeTab === value;

  return (
    <button
      onClick={() => setActiveTab(value)}
      className={`tabs-trigger ${className}`}
      style={{
        padding: '12px 24px',
        border: 'none',
        background: 'none',
        borderBottom: isActive ? '3px solid #2563EB' : '3px solid transparent',
        color: isActive ? '#2563EB' : '#475569',
        fontWeight: isActive ? 600 : 400,
        fontSize: '16px',
        cursor: 'pointer',
        transition: 'all 150ms ease-in-out',
        marginBottom: '-2px'
      }}
    >
      {children}
    </button>
  );
}

export function TabsContent({ value, children, className = '' }) {
  const { activeTab } = useContext(TabsContext);

  if (activeTab !== value) return null;

  return (
    <div className={`tabs-content ${className}`}>
      {children}
    </div>
  );
}
