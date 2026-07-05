import React, { useEffect } from 'react';
import type { Place } from '../../types/place';
import { PanelHeader } from './PanelHeader';
import { LocationInfoCard } from './LocationInfoCard';
import { CoordinateCard } from './CoordinateCard';
import { AddressCard } from './AddressCard';
import { QuickActionBar } from './QuickActionBar';
import { MapPin } from 'lucide-react';

interface PlaceDetailsPanelProps {
  place: Place | null;
  isOpen: boolean;
  onClose: () => void;
}

export const PlaceDetailsPanel: React.FC<PlaceDetailsPanelProps> = ({ place, isOpen, onClose }) => {
  // Handle ESC key to close
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Center map listener
  useEffect(() => {
    const handleCenterMap = (e: Event) => {
      const customEvent = e as CustomEvent;
      // In a real app, this would use a map context or be passed up
      console.log('Centering map to', customEvent.detail);
    };
    
    window.addEventListener('center-map', handleCenterMap);
    return () => window.removeEventListener('center-map', handleCenterMap);
  }, []);

  if (!isOpen) return null;

  return (
    <>
      {/* Mobile Backdrop */}
      <div 
        className={`md:hidden fixed inset-0 bg-black/20 z-40 transition-opacity duration-300 ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
        onClick={onClose}
        aria-hidden="true"
      />
      
      {/* Panel Container */}
      <div 
        className={`
          fixed md:relative z-50 md:z-10
          bottom-0 md:bottom-auto left-0 md:left-auto
          w-full md:w-[400px] lg:w-[450px] shrink-0
          bg-white md:bg-white/95 
          h-[85vh] md:h-full 
          rounded-t-2xl md:rounded-2xl
          shadow-[0_-10px_40px_rgba(0,0,0,0.1)] md:shadow-lg
          border-t md:border border-gray-200
          flex flex-col overflow-hidden
          transition-transform duration-300 ease-out
          ${isOpen 
            ? 'translate-y-0 md:translate-x-0' 
            : 'translate-y-full md:-translate-x-[120%]'
          }
        `}
        role="dialog"
        aria-label="Place Details"
      >
        {/* Mobile handle indicator */}
        <div className="w-full flex justify-center pt-3 pb-1 md:hidden bg-white/90 sticky top-0 z-20">
          <div className="w-12 h-1.5 bg-gray-300 rounded-full" />
        </div>

        {place ? (
          <>
            <PanelHeader place={place} onClose={onClose} />
            
            <div className="flex-1 overflow-y-auto custom-scrollbar p-4 bg-white">
              <QuickActionBar place={place} />
              
              <LocationInfoCard place={place} />
              
              <AddressCard place={place} />
              
              <CoordinateCard place={place} />
              
              {/* Future Expansion Slots */}
              {/* <OpeningHoursCard /> */}
              {/* <ContactInfoCard /> */}
              {/* <ReviewsCard /> */}
              
              <div className="h-8" /> {/* Bottom padding */}
            </div>
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-gray-500">
            <div className="w-24 h-24 bg-blue-50 rounded-full flex items-center justify-center mb-6 text-blue-200">
              <MapPin size={48} />
            </div>
            <h3 className="text-xl font-medium text-gray-700 mb-2">No Place Selected</h3>
            <p className="text-sm">Select a place from the search results to view its details.</p>
          </div>
        )}
      </div>
    </>
  );
};
