import React, { useState } from 'react';
import { MapPin, ChevronDown, ChevronUp, Navigation2 } from 'lucide-react';
import type { Place } from '../types/place';
import { formatDistance } from '../utils/distance';

interface ResultCardProps {
  place: Place;
  isSelected: boolean;
  onClick: () => void;
}

export const ResultCard: React.FC<ResultCardProps> = ({ place, isSelected, onClick }) => {
  const [showDebug, setShowDebug] = useState(false);
  const isGoRide = place.source === 'goride.places';
  const displayDistance = formatDistance(place.distance_meters);

  return (
    <div 
      onClick={onClick}
      className={`cursor-pointer p-4 rounded-xl border transition-all duration-200 mb-3 group hover:shadow-md ${
        isSelected 
          ? 'bg-blue-50 border-blue-400 shadow-md ring-1 ring-blue-400' 
          : 'bg-white border-gray-100 hover:border-gray-200'
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3 flex-1">
          <div className={`mt-1 rounded-full p-2 ${isGoRide ? 'bg-blue-100 text-blue-600' : 'bg-green-100 text-green-600'}`}>
            <MapPin className="h-5 w-5" />
          </div>
          <div className="flex-1">
            <div className="flex justify-between items-start">
              <h3 className="font-semibold text-gray-900 leading-tight group-hover:text-blue-600 transition-colors pr-2">
                {place.name}
              </h3>
              {displayDistance && (
                <div className="flex items-center gap-1 text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-1 rounded-md shrink-0">
                  <Navigation2 className="h-3 w-3" />
                  {displayDistance}
                </div>
              )}
            </div>
            <p className="text-sm text-gray-500 capitalize">{place.category}</p>
            <p className="text-xs text-gray-400 mt-1">
              {[place.district, place.state].filter(Boolean).join(', ')}
            </p>
          </div>
        </div>
      </div>
      
      <div className="mt-4 flex items-center justify-between text-xs font-medium">
        <span className={`px-2 py-1 rounded-md ${isGoRide ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'}`}>
          {isGoRide ? 'GoRide' : 'Nominatim'}
        </span>
        
        <button 
          onClick={(e) => {
            e.stopPropagation();
            setShowDebug(!showDebug);
          }}
          className="text-gray-400 hover:text-gray-600 flex items-center gap-1 px-2 py-1 bg-gray-50 rounded-md transition-colors"
        >
          Debug {showDebug ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
        </button>
      </div>

      {showDebug && (
        <div className="mt-3 pt-3 border-t border-gray-100 text-xs text-gray-600 grid grid-cols-2 gap-x-4 gap-y-2">
          <div className="flex justify-between"><span>Provider:</span> <span className="font-mono">{place.source}</span></div>
          <div className="flex justify-between"><span>Matched By:</span> <span className="font-mono">{place.matched_by || place.match_type}</span></div>
          <div className="flex justify-between"><span>Base Score:</span> <span className="font-mono">{place.base_score?.toFixed(1) || 0}</span></div>
          <div className="flex justify-between"><span>Token Bonus:</span> <span className="font-mono">{place.token_bonus?.toFixed(1) || 0}</span></div>
          <div className="flex justify-between"><span>Category Bonus:</span> <span className="font-mono">{place.category_bonus?.toFixed(1) || 0}</span></div>
          <div className="flex justify-between"><span>Admin Bonus:</span> <span className="font-mono">{place.admin_bonus?.toFixed(1) || 0}</span></div>
          <div className="flex justify-between"><span>Pincode Bonus:</span> <span className="font-mono">{place.pincode_bonus?.toFixed(1) || 0}</span></div>
          <div className="flex justify-between"><span>Provider Bonus:</span> <span className="font-mono">{place.provider_bonus?.toFixed(1) || 0}</span></div>
          <div className="flex justify-between"><span>Importance Bonus:</span> <span className="font-mono">{place.importance_bonus?.toFixed(1) || 0}</span></div>
          <div className="flex justify-between"><span>Popularity Bonus:</span> <span className="font-mono">{place.popularity_bonus?.toFixed(1) || 0}</span></div>
          
          {place.distance_meters !== undefined && place.distance_meters !== null && (
            <div className="flex justify-between col-span-2 text-blue-600 font-semibold border-t border-blue-50 pt-1 mt-1">
              <span>Distance / Bonus:</span> 
              <span className="font-mono">{Math.round(place.distance_meters)}m / +{place.distance_bonus?.toFixed(2) || 0}</span>
            </div>
          )}
          
          <div className="flex justify-between col-span-2 text-green-600 font-bold border-t border-green-50 pt-1 mt-1">
            <span>Final Score:</span> 
            <span className="font-mono">{place.final_score?.toFixed(1) || place.score?.toFixed(1) || 0}</span>
          </div>
        </div>
      )}
    </div>
  );
};
