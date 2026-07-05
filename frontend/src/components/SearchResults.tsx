import React from 'react';
import type { Place } from '../types/place';
import { ResultCard } from './ResultCard';
import { MapPin } from 'lucide-react';

interface SearchResultsProps {
  results: Place[];
  isLoading: boolean;
  error: string | null;
  query: string;
  selectedId: number | null;
  onSelect: (place: Place) => void;
  isLocationActive?: boolean;
  isSearchingContext?: boolean;
  onAddMissingPlace?: () => void;
}

export const SearchResults: React.FC<SearchResultsProps> = ({ 
  results, 
  isLoading, 
  error, 
  query,
  selectedId,
  onSelect,
  isLocationActive = false,
  isSearchingContext = false,
  onAddMissingPlace
}) => {
  if (!query) return null;

  if (error) {
    return (
      <div className="p-8 text-center text-red-500 bg-red-50 rounded-2xl border border-red-100 mt-4">
        {error}
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="p-8 text-center bg-white rounded-2xl border border-gray-100 mt-4 shadow-sm animate-pulse">
        <div className="h-6 w-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
        <p className="text-gray-500 font-medium">Searching...</p>
        
        {/* Development mode search status */}
        {isSearchingContext && (
          <div className="mt-4 text-xs text-gray-400 flex flex-col gap-1 items-center">
            <span>✓ GoRide</span>
            <span>✓ Nominatim</span>
            <span>✓ Merged</span>
            <span>✓ Ranked</span>
          </div>
        )}
      </div>
    );
  }

  const MissingPlaceAction = () => (
    <div className="mt-4 p-4 border border-dashed border-gray-300 rounded-xl bg-gray-50 flex flex-col items-center justify-center text-center">
      <p className="text-gray-600 text-sm mb-3">Can't find your place?</p>
      <button
        onClick={onAddMissingPlace}
        className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-blue-600 hover:bg-gray-50 transition-colors flex items-center gap-2 shadow-sm"
      >
        <MapPin className="w-4 h-4" />
        Add a Missing Place
      </button>
    </div>
  );

  if (results.length === 0) {
    return (
      <div className="p-8 text-center bg-white rounded-2xl border border-gray-100 mt-4 shadow-sm flex flex-col items-center">
        <p className="text-gray-500 font-medium mb-4">No places found.</p>
        <MissingPlaceAction />
      </div>
    );
  }

  return (
    <div className="mt-4 flex flex-col h-full max-h-full overflow-hidden">
      <div className="flex justify-between items-center px-2 mb-2">
        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
          Results ({results.length})
        </span>
        <span className={`text-xs px-2 py-1 rounded-full font-medium ${isLocationActive ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'}`}>
          {isLocationActive ? 'Nearby' : 'Text Ranking'}
        </span>
      </div>
      
      <div className="flex flex-col h-full overflow-y-auto pr-2 custom-scrollbar pb-10">
        {results.map((place, index) => (
          <ResultCard 
            key={`${place.id}-${index}`} 
            place={place} 
            isSelected={place.id === selectedId}
            onClick={() => onSelect(place)}
          />
        ))}
        <MissingPlaceAction />
      </div>
    </div>
  );
};
