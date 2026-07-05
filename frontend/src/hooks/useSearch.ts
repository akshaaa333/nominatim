import { useState, useCallback, useRef, useEffect } from 'react';
import debounce from 'lodash.debounce';
import { searchPlaces } from '../services/api';
import type { Place, UserLocation } from '../types/place';

export type LocationStatus = 'idle' | 'acquiring' | 'active' | 'denied' | 'error';

export const useSearch = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Place[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Location states
  const [userLocation, setUserLocation] = useState<UserLocation | null>(null);
  const [locationStatus, setLocationStatus] = useState<LocationStatus>('idle');
  const [isSearchingContext, setIsSearchingContext] = useState(false);
  
  // Keep refs for latest location to use in debounced function without recreation
  const locationRef = useRef<UserLocation | null>(null);
  
  useEffect(() => {
    locationRef.current = userLocation;
  }, [userLocation]);

  // Debounce the actual API call
  const debouncedSearch = useRef(
    debounce(async (q: string) => {
      if (!q || q.length < 2) {
        setResults([]);
        setIsLoading(false);
        setIsSearchingContext(false);
        return;
      }
      
      try {
        setIsLoading(true);
        setIsSearchingContext(true);
        setError(null);
        
        const loc = locationRef.current;
        const data = await searchPlaces(q, loc?.latitude, loc?.longitude);
        setResults(data);
      } catch (err: any) {
        setResults([]);
        if (err.message === 'Network Error' || err.code === 'ECONNABORTED') {
          setError('Unable to reach backend.');
        } else {
          setError('An error occurred while fetching results.');
        }
      } finally {
        setIsLoading(false);
        setIsSearchingContext(false);
      }
    }, 300)
  ).current;

  // Cleanup debounce on unmount
  useEffect(() => {
    return () => {
      debouncedSearch.cancel();
    };
  }, [debouncedSearch]);

  const handleSearch = useCallback((newQuery: string) => {
    setQuery(newQuery);
    if (newQuery.length >= 2) {
      setIsLoading(true); // Immediate visual feedback
    } else {
      setIsLoading(false);
      setResults([]);
    }
    debouncedSearch(newQuery);
  }, [debouncedSearch]);

  const acquireLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setLocationStatus('error');
      return;
    }
    
    setLocationStatus('acquiring');
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const newLocation = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          timestamp: position.timestamp,
        };
        setUserLocation(newLocation);
        setLocationStatus('active');
        
        // Immediately re-trigger search if query exists
        if (query.length >= 2) {
          debouncedSearch(query);
        }
      },
      (geoError) => {
        if (geoError.code === geoError.PERMISSION_DENIED) {
          setLocationStatus('denied');
        } else {
          setLocationStatus('error');
        }
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    );
  }, [query, debouncedSearch]);

  return {
    query,
    results,
    isLoading,
    isSearchingContext,
    error,
    userLocation,
    locationStatus,
    handleSearch,
    acquireLocation
  };
};
