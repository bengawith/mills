import React, { useState, ReactNode } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface LegendItem {
  value: string;
  color?: string;
  // Add other properties if needed, e.g., type, payload
}

interface CollapsibleLegendProps {
  title: string;
  payload: LegendItem[]; // Data for the legend items
}

export const CollapsibleLegend = ({ title, payload }: CollapsibleLegendProps) => {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="border rounded-md p-2 mt-4">
      <button
        className="flex justify-between items-center w-full text-left font-semibold"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span>{title}</span>
        {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>
      {isOpen && (
        <div className="mt-2 space-y-1">
          {payload.map((entry, index) => (
            <div key={`legend-item-${index}`} className="flex items-center">
              <span
                className="inline-block w-3 h-3 rounded-full mr-2"
                style={{ backgroundColor: entry.color || '#8884d8' }} // Default color if not provided
              ></span>
              <span className="text-sm text-gray-700">{entry.value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
