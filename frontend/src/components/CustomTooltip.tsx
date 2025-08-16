import React from 'react';

interface CustomTooltipProps {
  active?: boolean;
  payload?: any[];
  label?: string;
}

export const CustomTooltip = ({ active, payload, label }: CustomTooltipProps) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 border border-gray-300 shadow-md rounded-md">
        <p className="font-bold text-gray-800 mb-1">{label}</p>
        {
          payload.map((entry, index) => (
            <p key={`item-${index}`} className="text-sm text-gray-700">
              <span style={{ color: entry.color || entry.fill }}>{entry.name || entry.dataKey}: </span>
              <span style={{ color: entry.color || entry.fill }}>
                {typeof entry.value === 'number' ? `${Math.round(entry.value * 100) / 100}` : entry.value}
                {entry.unit}
              </span>
            </p>
          ))
        }
      </div>
    );
  }

  return null;
};
