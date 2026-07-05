import React from 'react';
import { Crosshair, Navigation2, Bookmark, Copy, Car, Flag } from 'lucide-react';
import type { Place } from '../../types/place';

interface QuickActionBarProps {
  place: Place;
}

export const QuickActionBar: React.FC<QuickActionBarProps> = ({ place }) => {
  return (
    <div className="grid grid-cols-3 gap-2 mt-2 mb-6">
      <ActionButton 
        icon={<Crosshair size={18} />} 
        label="Center Map" 
        onClick={() => {
          // This will be handled by the parent component or map context
          // For now, it's just a UI placeholder as requested
          window.dispatchEvent(new CustomEvent('center-map', { detail: { lat: place.latitude, lng: place.longitude } }));
        }} 
      />
      <ActionButton 
        icon={<Navigation2 size={18} />} 
        label="Navigate" 
        onClick={() => {}} 
      />
      <ActionButton 
        icon={<Bookmark size={18} />} 
        label="Save" 
        onClick={() => {}} 
      />
      <ActionButton 
        icon={<Copy size={18} />} 
        label="Copy Coords" 
        onClick={() => {
          navigator.clipboard.writeText(`${place.latitude.toFixed(6)},${place.longitude.toFixed(6)}`);
        }} 
      />
      <ActionButton 
        icon={<Car size={18} />} 
        label="Pickup" 
        onClick={() => {}} 
        primary
      />
      <ActionButton 
        icon={<Flag size={18} />} 
        label="Destination" 
        onClick={() => {}} 
        primary
      />
    </div>
  );
};

const ActionButton = ({ 
  icon, 
  label, 
  onClick, 
  primary = false 
}: { 
  icon: React.ReactNode; 
  label: string; 
  onClick: () => void;
  primary?: boolean;
}) => (
  <button
    onClick={onClick}
    className={`flex flex-col items-center justify-center gap-1.5 p-3 rounded-xl transition-all shadow-sm ${
      primary 
        ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-blue-200' 
        : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-50'
    }`}
  >
    {icon}
    <span className={`text-[10px] font-semibold uppercase tracking-wider ${primary ? 'text-blue-50' : 'text-gray-500'}`}>
      {label}
    </span>
  </button>
);
