import React, { useState } from 'react';
import { Copy, Check, MapPin } from 'lucide-react';
import type { Place } from '../../types/place';

interface AddressCardProps {
  place: Place;
}

export const AddressCard: React.FC<AddressCardProps> = ({ place }) => {
  const [copied, setCopied] = useState(false);

  // Construct the address parts
  const addressParts = [
    place.name,
    place.district,
    place.state,
    place.country,
    place.pincode
  ].filter(Boolean); // Remove empty/undefined parts

  const formattedAddress = addressParts.join(',\n');
  const inlineAddress = addressParts.join(', ');

  const copyToClipboard = () => {
    navigator.clipboard.writeText(inlineAddress);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (addressParts.length <= 1) {
    return null; // Not enough info to show a dedicated address block
  }

  return (
    <div className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm mb-4">
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-1.5">
          <MapPin size={16} />
          Full Address
        </h3>
        <button 
          onClick={copyToClipboard}
          className="text-xs flex items-center gap-1 text-blue-600 hover:text-blue-700 font-medium"
        >
          {copied ? <Check size={14} /> : <Copy size={14} />}
          {copied ? 'Copied' : 'Copy Address'}
        </button>
      </div>
      
      <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
        <p className="text-sm text-gray-800 leading-relaxed whitespace-pre-line">
          {formattedAddress}
        </p>
      </div>
    </div>
  );
};
