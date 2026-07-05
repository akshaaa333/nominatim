import React, { useState } from 'react';
import { X, MapPin, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { geocodeAddress, checkDuplicatePlace, addManualPlace } from '../../services/api';
import { GeocodePreviewMap } from './GeocodePreviewMap';
import { ConfirmationDialog } from './ConfirmationDialog';

interface MissingPlaceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const MissingPlaceModal = ({ isOpen, onClose, onSuccess }: MissingPlaceModalProps) => {
  const [step, setStep] = useState<1 | 2>(1);
  const [name, setName] = useState('');
  const [address, setAddress] = useState('');
  const [category, setCategory] = useState('');
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [geocodedData, setGeocodedData] = useState<any>(null);
  const [showConfirm, setShowConfirm] = useState(false);

  if (!isOpen) return null;

  const handleGeocode = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !address) return;
    
    setIsLoading(true);
    setError(null);
    try {
      const data = await geocodeAddress(address);
      setGeocodedData({ ...data, name, category: category || 'amenity' });
      setStep(2);
    } catch (err: any) {
      setError(err.response?.data?.detail || "The exact address could not be located. Try removing the building name or simplifying the address.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleLocationChange = (lat: number, lon: number) => {
    if (geocodedData) {
      setGeocodedData({ ...geocodedData, latitude: lat, longitude: lon });
    }
  };

  const isLocationValid = () => {
    if (!geocodedData) return false;
    const { latitude, longitude } = geocodedData;
    if (latitude == null || longitude == null) return false;
    // Basic bounds for India
    if (latitude < 6.0 || latitude > 36.0 || longitude < 68.0 || longitude > 98.0) {
      return false;
    }
    return true;
  };

  const handleSubmit = async () => {
    if (!geocodedData || !isLocationValid()) {
      setError("Invalid location. Ensure the marker is within India.");
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      // Check duplicate
      const dupRes = await checkDuplicatePlace(geocodedData.latitude, geocodedData.longitude, geocodedData.name);
      if (dupRes.is_duplicate) {
        setError("This place seems to already exist in our system nearby.");
        setIsLoading(false);
        setShowConfirm(false);
        return;
      }
      
      // Submit
      await addManualPlace(geocodedData);
      onSuccess(); // Triggers a refresh of search results in parent
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to add place.");
    } finally {
      setIsLoading(false);
      setShowConfirm(false);
    }
  };

  const resetState = () => {
    setStep(1);
    setGeocodedData(null);
    setError(null);
  };

  return (
    <>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
        <div className="absolute inset-0 bg-black/40 backdrop-blur-sm transition-opacity" onClick={onClose} />
        
        <div className="relative w-full max-w-xl bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[95vh] animate-in slide-in-from-bottom-4 fade-in duration-300">
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-white/50 backdrop-blur sticky top-0 z-10">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
              <MapPin className="w-5 h-5 text-blue-500" />
              {step === 1 ? 'Add Missing Place' : 'Verify Location'}
            </h2>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="p-6 overflow-y-auto">
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-100 text-red-600 rounded-lg text-sm">
                {error}
              </div>
            )}

            {step === 1 ? (
              <form id="geocode-form" onSubmit={handleGeocode} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Place Name *</label>
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                    placeholder="e.g. Central Perk Cafe"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Address *</label>
                  <textarea
                    required
                    value={address}
                    onChange={(e) => setAddress(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all resize-none h-24"
                    placeholder="Enter the full address to search..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Category (Optional)</label>
                  <input
                    type="text"
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                    placeholder="e.g. restaurant, hospital, atm"
                  />
                </div>
              </form>
            ) : (
              <div className="space-y-4 animate-in fade-in slide-in-from-right-4 duration-300">
                {geocodedData?.exact_match === false && (
                  <div className="flex items-start gap-3 bg-yellow-50 text-yellow-800 p-3 rounded-lg border border-yellow-200">
                    <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
                    <p className="text-sm">We found the closest matching location. Please verify the marker before saving.</p>
                  </div>
                )}
                
                {geocodedData && (
                  <GeocodePreviewMap
                    initialLat={geocodedData.latitude}
                    initialLon={geocodedData.longitude}
                    onLocationChanged={handleLocationChange}
                  />
                )}

                <div className="bg-gray-50 rounded-xl p-4 border border-gray-200 text-sm space-y-2 relative">
                  {showConfirm && (
                    <div className="absolute -top-3 -right-2 bg-green-100 text-green-700 px-2 py-1 rounded-full text-xs font-semibold border border-green-200 flex items-center gap-1 shadow-sm animate-in zoom-in fade-in">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      Location Verified
                    </div>
                  )}
                  
                  <div className="flex justify-between">
                    <span className="text-gray-500">Latitude</span>
                    <span className="font-mono font-medium text-gray-900">{geocodedData?.latitude?.toFixed(6)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Longitude</span>
                    <span className="font-mono font-medium text-gray-900">{geocodedData?.longitude?.toFixed(6)}</span>
                  </div>
                  <div className="flex flex-col border-t border-gray-200 pt-2 mt-2 gap-1">
                    <span className="text-gray-500 text-xs uppercase tracking-wider">Formatted Address</span>
                    <span className="font-medium text-gray-900">{geocodedData?.display_name || geocodedData?.name}</span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 border-t border-gray-200 pt-2 mt-2">
                    <div>
                      <span className="text-gray-500 text-xs uppercase tracking-wider block">District</span>
                      <span className="font-medium text-gray-900">{geocodedData?.district || '-'}</span>
                    </div>
                    <div>
                      <span className="text-gray-500 text-xs uppercase tracking-wider block">State</span>
                      <span className="font-medium text-gray-900">{geocodedData?.state || '-'}</span>
                    </div>
                    <div>
                      <span className="text-gray-500 text-xs uppercase tracking-wider block">Pincode</span>
                      <span className="font-medium text-gray-900">{geocodedData?.pincode || '-'}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="px-6 py-4 border-t border-gray-100 bg-gray-50 flex justify-end gap-3 rounded-b-2xl">
            {step === 1 ? (
              <>
                <button
                  type="button"
                  onClick={onClose}
                  className="px-5 py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  form="geocode-form"
                  disabled={isLoading || !name || !address}
                  className="px-5 py-2.5 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                >
                  {isLoading ? 'Searching...' : 'Find Location'}
                </button>
              </>
            ) : (
              <>
                <button
                  type="button"
                  onClick={resetState}
                  className="px-5 py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors"
                >
                  Back
                </button>
                <button
                  type="button"
                  onClick={() => setShowConfirm(true)}
                  disabled={isLoading || !isLocationValid()}
                  className="px-5 py-2.5 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-xl hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Save Place
                </button>
              </>
            )}
          </div>
        </div>
      </div>
      
      <ConfirmationDialog
        isOpen={showConfirm}
        title="Confirm New Place"
        message={`Are you sure you want to add "${geocodedData?.name}" to the database at the chosen location?`}
        onConfirm={handleSubmit}
        onCancel={() => setShowConfirm(false)}
        isLoading={isLoading}
      />
    </>
  );
};
