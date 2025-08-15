import React, { useState, ReactNode } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface CollapsibleLegendProps {
  title: string;
  children: ReactNode;
}

export const CollapsibleLegend = ({ title, children }: CollapsibleLegendProps) => {
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
      {isOpen && <div className="mt-2">{children}</div>}
    </div>
  );
};
