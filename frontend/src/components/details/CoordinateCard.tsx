import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';
import type { Place } from '../../types/place';

interface CoordinateCardProps {
  place: Place;
}

export const CoordinateCard: React.FC<CoordinateCardProps> = ({ place }) => {
  const [copiedLat, setCopiedLat] = useState(false);
  const [copiedLng, setCopiedLng] = useState(false);
  const [copiedBoth, setCopiedBoth] = useState(false);

  const copyToClipboard = (text: string, setter: React.Dispatch<React.SetStateAction<boolean>>) => {
    navigator.clipboard.writeText(text);
    setter(true);
    setTimeout(() => setter(false), 2000);
  };

  return (
    <div className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm mb-4">
      <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
        Coordinates
      </h3>
      
      <div className="space-y-3">
        <div className="flex items-center justify-between bg-gray-50 rounded-lg p-2.5 border border-gray-100">
          <div>
            <div className="text-xs text-gray-500 mb-0.5">Latitude</div>
            <div className="text-sm font-mono text-gray-900">{place.latitude.toFixed(6)}</div>
          </div>
          <button 
            onClick={() => copyToClipboard(place.latitude.toString(), setCopiedLat)}
            className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
            title="Copy Latitude"
          >
            {copiedLat ? <Check size={16} /> : <Copy size={16} />}
          </button>
        </div>

        <div className="flex items-center justify-between bg-gray-50 rounded-lg p-2.5 border border-gray-100">
          <div>
            <div className="text-xs text-gray-500 mb-0.5">Longitude</div>
            <div className="text-sm font-mono text-gray-900">{place.longitude.toFixed(6)}</div>
          </div>
          <button 
            onClick={() => copyToClipboard(place.longitude.toString(), setCopiedLng)}
            className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
            title="Copy Longitude"
          >
            {copiedLng ? <Check size={16} /> : <Copy size={16} />}
          </button>
        </div>

        <button 
          onClick={() => copyToClipboard(`${place.latitude.toFixed(6)},${place.longitude.toFixed(6)}`, setCopiedBoth)}
          className="w-full flex items-center justify-center gap-2 py-2 mt-2 text-sm font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
        >
          {copiedBoth ? <Check size={16} /> : <Copy size={16} />}
          {copiedBoth ? 'Copied Coordinates' : 'Copy Coordinates'}
        </button>
      </div>
    </div>
  );
};
