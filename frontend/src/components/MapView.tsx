import { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import type { Place, UserLocation } from '../types/place';

interface MapViewProps {
  results: Place[];
  selectedId: number | null;
  userLocation?: UserLocation | null;
  onSelect?: (place: Place) => void;
}

export const MapView = ({ results, selectedId, userLocation, onSelect }: MapViewProps) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const markers = useRef<{ [id: number]: maplibregl.Marker }>({});
  const userMarker = useRef<maplibregl.Marker | null>(null);
  const hasCenteredOnUser = useRef(false);

  useEffect(() => {
    if (map.current || !mapContainer.current) return;
    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          osm: {
            type: 'raster',
            tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
            tileSize: 256,
            attribution: '&copy; OpenStreetMap Contributors'
          }
        },
        layers: [
          {
            id: 'osm',
            type: 'raster',
            source: 'osm',
            minzoom: 0,
            maxzoom: 19
          }
        ]
      },
      center: [80.2707, 13.0827], // Default to Chennai center
      zoom: 10
    });
    
    // Ensure map resizes correctly if container dimensions change
    setTimeout(() => {
      if (map.current) map.current.resize();
    }, 100);
  }, []);

  // Handle User Location Marker
  useEffect(() => {
    if (!map.current || !userLocation) return;
    
    if (userMarker.current) {
      userMarker.current.remove();
    }
    
    const el = document.createElement('div');
    el.innerHTML = `
      <div class="relative flex items-center justify-center">
        <div class="absolute w-12 h-12 bg-blue-500 rounded-full opacity-20 animate-ping"></div>
        <div class="absolute w-4 h-4 bg-white rounded-full shadow-md z-10 flex items-center justify-center">
          <div class="w-2.5 h-2.5 bg-blue-600 rounded-full"></div>
        </div>
      </div>
    `;
    
    userMarker.current = new maplibregl.Marker({ element: el })
      .setLngLat([userLocation.longitude, userLocation.latitude])
      .addTo(map.current);
      
    if (!hasCenteredOnUser.current) {
      map.current.flyTo({
        center: [userLocation.longitude, userLocation.latitude],
        zoom: 14,
        duration: 2000
      });
      hasCenteredOnUser.current = true;
    }
  }, [userLocation]);

  // Handle Search Result Markers
  useEffect(() => {
    if (!map.current) return;

    // Clear existing markers
    Object.values(markers.current).forEach(marker => marker.remove());
    markers.current = {};

    results.forEach(place => {
      const el = document.createElement('div');
      el.className = 'cursor-pointer transition-all duration-300';
      const isSelected = place.id === selectedId;
      el.innerHTML = `
        <div style="transform: scale(${isSelected ? 1.25 : 1}); opacity: ${isSelected ? 1 : 0.8}; z-index: ${isSelected ? 10 : 1};">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="${place.source === 'goride.places' ? '#2563eb' : '#16a34a'}" style="width: 32px; height: 32px; filter: drop-shadow(0 4px 3px rgb(0 0 0 / 0.07));">
            <path fill-rule="evenodd" d="M11.54 22.351l.07.04.028.016a.76.76 0 00.723 0l.028-.015.071-.041a16.975 16.975 0 001.144-.742 19.58 19.58 0 002.683-2.282c1.944-1.99 3.963-4.98 3.963-8.827a8.25 8.25 0 00-16.5 0c0 3.846 2.02 6.837 3.963 8.827a19.58 19.58 0 002.682 2.282 16.975 16.975 0 001.145.742zM12 13.5a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd" />
          </svg>
        </div>
      `;

      if (onSelect) {
        el.addEventListener('click', (e) => {
          e.stopPropagation();
          onSelect(place);
        });
      }

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat([place.longitude, place.latitude])
        .addTo(map.current!);

      markers.current[place.id] = marker;
    });

    if (results.length > 0 && selectedId) {
      let targetPlace = results.find(p => p.id === selectedId);
      if (targetPlace) {
        map.current.flyTo({
          center: [targetPlace.longitude, targetPlace.latitude],
          zoom: 15,
          essential: true,
          duration: 1500
        });
      }
    } else if (results.length > 0 && !hasCenteredOnUser.current) {
      let targetPlace = results[0];
      map.current.flyTo({
        center: [targetPlace.longitude, targetPlace.latitude],
        zoom: 14,
        essential: true,
        duration: 1500
      });
    }
  }, [results, selectedId, onSelect]);

  return (
    <div className="w-full h-full rounded-2xl overflow-hidden shadow-lg border border-gray-100 relative">
      <div ref={mapContainer} className="absolute inset-0" />
    </div>
  );
};
