/*
  FilterControls.tsx - MillDash Frontend Dashboard Filter Controls Component

  This file implements the filter controls for the MillDash dashboard using React and TypeScript. It provides a user interface for selecting time range, machine, shift, and day of week, enabling users to customize the analytics displayed on the dashboard. The component fetches available machines from the backend and uses custom UI components for a consistent and accessible layout.

  Key Features:
  - Uses React functional component with props for filter state and update handler.
  - Fetches machine list from backend using React Query.
  - Provides input fields for start/end time, machine selection, shift, and day of week.
  - Handles loading and error states for machine list.
  - Utilizes custom UI components (Input, Label, Select, SelectItem, SelectTrigger, SelectValue).
  - Responsive layout using Tailwind CSS grid utilities.

  This component is essential for interactive analytics, allowing users to filter dashboard data by relevant criteria.
*/

import React from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useQuery } from '@tanstack/react-query';
import { getMachines } from '@/lib/api';

interface FilterControlsProps {
  // Filters object containing dashboard filter values
  filters: {
    start_time: string;
    end_time: string;
    machine_ids: string;
    shift: string;
    day_of_week: string;
  };
  // Function to update filters state
  setFilters: (filters: {
    start_time: string;
    end_time: string;
    machine_ids: string;
    shift: string;
    day_of_week: string;
  }) => void;
}

const FilterControls: React.FC<FilterControlsProps> = ({ filters, setFilters }) => {
  /**
   * Handles input changes for filter controls.
   * Updates the corresponding field in the filters state.
   * @param field - The filter field name to update
   * @param value - The new value for the filter field
   */
  const handleInputChange = (field: string, value: string): void => {
    setFilters({ ...filters, [field]: value });
  };

  /**
   * Fetches the list of available machines from the backend for machine selection.
   * Uses React Query for caching and loading/error state management.
   */
  const { data: machines, isLoading: isLoadingMachines, error: machinesError } = useQuery<{ id: string, name: string }[]>({
    queryKey: ['machines'],
    queryFn: getMachines,
  });

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div>
        <Label htmlFor="startTime">Start Time</Label>
        <Input
          id="startTime"
          type="datetime-local"
          value={filters.start_time}
          onChange={(e) => handleInputChange('start_time', e.target.value)}
        />
      </div>
      <div>
        <Label htmlFor="endTime">End Time</Label>
        <Input
          id="endTime"
          type="datetime-local"
          value={filters.end_time}
          onChange={(e) => handleInputChange('end_time', e.target.value)}
        />
      </div>
      <div>
        <Label htmlFor="machineIds">Machine</Label>
        <Select onValueChange={(value) => handleInputChange('machine_ids', value)} value={filters.machine_ids}>
          <SelectTrigger>
            <SelectValue placeholder="Select a machine" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="All">All</SelectItem>
            {isLoadingMachines && <SelectItem value="loading" disabled>Loading machines...</SelectItem>}
            {machinesError && <SelectItem value="error" disabled>Error loading machines</SelectItem>}
            {machines?.map((machine) => (
              <SelectItem key={machine.id} value={machine.id}>
                {machine.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div>
        <Label htmlFor="shift">Shift</Label>
        <Select onValueChange={(value) => handleInputChange('shift', value)} value={filters.shift}>
          <SelectTrigger>
            <SelectValue placeholder="Select a shift" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="All">All</SelectItem>
            <SelectItem value="DAY">Day</SelectItem>
            <SelectItem value="NIGHT">Night</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div>
        <Label htmlFor="day_of_week">Day of Week</Label>
        <Select onValueChange={(value) => handleInputChange('day_of_week', value)} value={filters.day_of_week}>
          <SelectTrigger>
            <SelectValue placeholder="Select a day" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="All">All</SelectItem>
            <SelectItem value="MONDAY">Monday</SelectItem>
            <SelectItem value="TUESDAY">Tuesday</SelectItem>
            <SelectItem value="WEDNESDAY">Wednesday</SelectItem>
            <SelectItem value="THURSDAY">Thursday</SelectItem>
            <SelectItem value="FRIDAY">Friday</SelectItem>
            <SelectItem value="SATURDAY">Saturday</SelectItem>
            <SelectItem value="SUNDAY">Sunday</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
};

export default FilterControls;
