import React from 'react';
import { X, MapPin } from 'lucide-react';
import type { Place } from '../../types/place';

interface PanelHeaderProps {
  place: Place;
  onClose: () => void;
}

export const PanelHeader: React.FC<PanelHeaderProps> = ({ place, onClose }) => {
  return (
    <div className="flex justify-between items-start sticky top-0 bg-white/90 backdrop-blur-md z-10 p-4 border-b border-gray-100">
      <div className="flex items-start gap-3 flex-1 pr-4">
        <div className="p-2 bg-blue-50 text-blue-600 rounded-lg shrink-0 mt-1">
          <MapPin size={24} />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900 leading-tight">
            {place.name}
          </h2>
          <div className="flex items-center gap-2 mt-1 flex-wrap">
            <span className="text-sm font-medium px-2 py-0.5 bg-gray-100 text-gray-700 rounded-md">
              {place.category}
            </span>
            {place.type && place.type !== place.category && (
              <span className="text-sm text-gray-500 capitalize">
                {place.type.replace(/_/g, ' ')}
              </span>
            )}
          </div>
        </div>
      </div>
      <button 
        onClick={onClose}
        className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors"
        aria-label="Close details"
      >
        <X size={20} />
      </button>
    </div>
  );
};
