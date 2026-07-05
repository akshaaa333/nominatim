import React, { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { Focus, RotateCcw } from 'lucide-react';

interface GeocodePreviewMapProps {
  initialLat: number;
  initialLon: number;
  onLocationChanged: (lat: number, lon: number) => void;
}

export const GeocodePreviewMap: React.FC<GeocodePreviewMapProps> = ({ 
  initialLat, 
  initialLon, 
  onLocationChanged 
}) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const marker = useRef<maplibregl.Marker | null>(null);
  const [currentLat, setCurrentLat] = useState(initialLat);
  const [currentLon, setCurrentLon] = useState(initialLon);

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
      center: [initialLon, initialLat],
      zoom: 15
    });

    const el = document.createElement('div');
    el.innerHTML = `
      <div style="cursor: grab;">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#ef4444" style="width: 32px; height: 32px; filter: drop-shadow(0 4px 3px rgb(0 0 0 / 0.07));">
          <path fill-rule="evenodd" d="M11.54 22.351l.07.04.028.016a.76.76 0 00.723 0l.028-.015.071-.041a16.975 16.975 0 001.144-.742 19.58 19.58 0 002.683-2.282c1.944-1.99 3.963-4.98 3.963-8.827a8.25 8.25 0 00-16.5 0c0 3.846 2.02 6.837 3.963 8.827a19.58 19.58 0 002.682 2.282 16.975 16.975 0 001.145.742zM12 13.5a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd" />
        </svg>
      </div>
    `;

    marker.current = new maplibregl.Marker({ element: el, draggable: true })
      .setLngLat([initialLon, initialLat])
      .addTo(map.current);

    marker.current.on('dragend', () => {
      const lngLat = marker.current?.getLngLat();
      if (lngLat) {
        setCurrentLat(lngLat.lat);
        setCurrentLon(lngLat.lng);
        onLocationChanged(lngLat.lat, lngLat.lng);
      }
    });

    // Add navigation controls (zoom/pan)
    map.current.addControl(new maplibregl.NavigationControl(), 'top-right');

    setTimeout(() => {
      if (map.current) map.current.resize();
    }, 100);
  }, []);

  const handleRecenter = () => {
    if (map.current && marker.current) {
      const lngLat = marker.current.getLngLat();
      map.current.flyTo({ center: lngLat, zoom: 15 });
    }
  };

  const handleReset = () => {
    if (map.current && marker.current) {
      marker.current.setLngLat([initialLon, initialLat]);
      setCurrentLat(initialLat);
      setCurrentLon(initialLon);
      onLocationChanged(initialLat, initialLon);
      map.current.flyTo({ center: [initialLon, initialLat], zoom: 15 });
    }
  };

  return (
    <div className="w-full h-[400px] rounded-xl overflow-hidden shadow-sm border border-gray-200 relative mb-4">
      <div ref={mapContainer} className="absolute inset-0" />
      <div className="absolute top-2 left-2 flex flex-col gap-2 z-10">
        <button
          onClick={handleRecenter}
          type="button"
          className="bg-white p-2 rounded-lg shadow border border-gray-200 hover:bg-gray-50 text-gray-700 tooltip"
          title="Recenter on marker"
        >
          <Focus className="w-5 h-5" />
        </button>
        <button
          onClick={handleReset}
          type="button"
          className="bg-white p-2 rounded-lg shadow border border-gray-200 hover:bg-gray-50 text-gray-700 tooltip"
          title="Reset to original location"
        >
          <RotateCcw className="w-5 h-5" />
        </button>
      </div>
      <div className="absolute bottom-2 left-2 bg-white/90 backdrop-blur px-3 py-1.5 rounded-lg shadow text-xs font-medium text-gray-700 z-10">
        Drag marker to adjust location
      </div>
    </div>
  );
};
