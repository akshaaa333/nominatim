import { useState } from 'react';
import { SearchBar } from './components/SearchBar';
import { SearchResults } from './components/SearchResults';
import { MapView } from './components/MapView';
import { useSearch } from './hooks/useSearch';
import { PlaceDetailsPanel } from './components/details/PlaceDetailsPanel';
import { MissingPlaceModal } from './components/missing_place/MissingPlaceModal';
import type { Place } from './types/place';

function App() {
  const { 
    query, results, isLoading, error, 
    handleSearch, userLocation, locationStatus, acquireLocation, isSearchingContext
  } = useSearch();
  
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [isMissingPlaceOpen, setIsMissingPlaceOpen] = useState(false);

  const selectedPlace = results.find(p => p.id === selectedId) || null;

  const handleSelect = (place: Place) => {
    setSelectedId(place.id);
  };

  const handleCloseDetails = () => {
    setSelectedId(null);
  };

  const handleMissingPlaceSuccess = () => {
    if (query) {
      handleSearch(query);
    }
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] flex flex-col md:flex-row p-4 md:p-6 gap-6 h-screen overflow-hidden">
      
      {/* Sidebar / Top area for Search and Results */}
      <div className="w-full md:w-[400px] lg:w-[450px] flex flex-col h-[50vh] md:h-full shrink-0 z-10">
        <div className="mb-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600 flex items-center gap-2">
            GoRide Search
          </h1>
        </div>
        <div className="mb-4">
          <SearchBar 
            query={query} 
            onChange={handleSearch} 
            locationStatus={locationStatus}
            onUseLocation={acquireLocation}
          />
        </div>
        
        <div className="flex-1 overflow-hidden pb-4 flex flex-col">
          <SearchResults 
            results={results} 
            isLoading={isLoading} 
            error={error} 
            query={query}
            selectedId={selectedId}
            onSelect={handleSelect}
            isLocationActive={!!userLocation}
            isSearchingContext={isSearchingContext}
            onAddMissingPlace={() => setIsMissingPlaceOpen(true)}
          />
        </div>
      </div>

      {/* Map Area */}
      <div className="flex-1 h-[50vh] md:h-full relative rounded-2xl overflow-hidden shadow-lg border border-gray-200">
        <MapView 
          results={results} 
          selectedId={selectedId} 
          userLocation={userLocation}
          onSelect={handleSelect}
        />
        
        {/* Place Details Overlay / Side Panel */}
        <div className="absolute inset-y-0 left-0 z-20 pointer-events-none">
          <div className="h-full pointer-events-auto">
            <PlaceDetailsPanel 
              place={selectedPlace}
              isOpen={selectedId !== null}
              onClose={handleCloseDetails}
            />
          </div>
        </div>
      </div>

      <MissingPlaceModal
        isOpen={isMissingPlaceOpen}
        onClose={() => setIsMissingPlaceOpen(false)}
        onSuccess={handleMissingPlaceSuccess}
      />
    </div>
  );
}

export default App;
