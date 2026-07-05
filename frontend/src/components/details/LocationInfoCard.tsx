import React from 'react';
import { Map, Flag, Database, Hash, Navigation } from 'lucide-react';
import type { Place } from '../../types/place';

interface LocationInfoCardProps {
  place: Place;
}

export const LocationInfoCard: React.FC<LocationInfoCardProps> = ({ place }) => {
  return (
    <div className="bg-gray-50 rounded-xl p-4 border border-gray-100 mb-4">
      <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
        Location Details
      </h3>
      <div className="grid grid-cols-2 gap-y-3 gap-x-4">
        {place.pincode && (
          <InfoRow icon={<Hash size={16} />} label="Pincode" value={place.pincode} />
        )}
        {place.district && (
          <InfoRow icon={<Map size={16} />} label="District" value={place.district} />
        )}
        {place.state && (
          <InfoRow icon={<Map size={16} />} label="State" value={place.state} />
        )}
        {place.country && (
          <InfoRow icon={<Flag size={16} />} label="Country" value={place.country} />
        )}
        <InfoRow 
          icon={<Database size={16} />} 
          label="Source" 
          value={place.source} 
          capitalize 
        />
        {place.distance_meters !== undefined && (
          <InfoRow 
            icon={<Navigation size={16} />} 
            label="Distance" 
            value={`${(place.distance_meters / 1000).toFixed(1)} km`} 
          />
        )}
        <InfoRow 
          icon={<Hash size={16} />} 
          label="Internal ID" 
          value={place.place_id ? place.place_id.toString() : place.id.toString()} 
        />
      </div>
    </div>
  );
};

const InfoRow = ({ icon, label, value, capitalize = false }: { icon: React.ReactNode; label: string; value: string; capitalize?: boolean }) => (
  <div className="flex items-start gap-2">
    <div className="text-gray-400 mt-0.5">{icon}</div>
    <div>
      <div className="text-xs text-gray-500">{label}</div>
      <div className={`text-sm font-medium text-gray-900 ${capitalize ? 'capitalize' : ''}`}>
        {value}
      </div>
    </div>
  </div>
);
