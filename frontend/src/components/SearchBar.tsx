import React from 'react';
import { Search, LocateFixed, Loader2 } from 'lucide-react';
import type { LocationStatus } from '../hooks/useSearch';

interface SearchBarProps {
  query: string;
  onChange: (value: string) => void;
  locationStatus?: LocationStatus;
  onUseLocation?: () => void;
}

export const SearchBar: React.FC<SearchBarProps> = ({ 
  query, onChange, locationStatus = 'idle', onUseLocation 
}) => {
  
  const getStatusText = () => {
    switch (locationStatus) {
      case 'acquiring': return '📍 Acquiring location...';
      case 'active': return '📍 Using Current Location';
      case 'denied': return '📍 Permission denied';
      case 'error': return '📍 Location unavailable';
      default: return null;
    }
  };

  const statusText = getStatusText();

  return (
    <div className="flex flex-col gap-2 w-full">
      <div className="relative w-full shadow-lg rounded-2xl overflow-hidden bg-white/80 backdrop-blur-md border border-gray-100 transition-all duration-300 focus-within:ring-2 focus-within:ring-blue-500 focus-within:shadow-xl flex items-center">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-blue-500" />
        </div>
        <input
          type="text"
          className="block w-full pl-12 pr-14 py-4 sm:text-lg bg-transparent outline-none placeholder-gray-400 text-gray-800 font-medium"
          placeholder="Search for a place..."
          value={query}
          onChange={(e) => onChange(e.target.value)}
        />
        {onUseLocation && (
          <button
            onClick={onUseLocation}
            className="absolute inset-y-0 right-0 pr-4 flex items-center justify-center text-gray-400 hover:text-blue-600 transition-colors"
            title="Use My Location"
          >
            {locationStatus === 'acquiring' ? (
              <Loader2 className="h-5 w-5 animate-spin text-blue-500" />
            ) : (
              <LocateFixed className={`h-5 w-5 ${locationStatus === 'active' ? 'text-blue-600' : ''}`} />
            )}
          </button>
        )}
      </div>
      
      {statusText && (
        <div className={`text-xs px-2 font-medium ${locationStatus === 'active' ? 'text-blue-600' : 'text-gray-500'}`}>
          {statusText}
        </div>
      )}
    </div>
  );
};
