import axios from 'axios';
import type { Place } from '../types/place';

const apiClient = axios.create({
  // Using Vite proxy to avoid CORS issues
  baseURL: '/api', 
  headers: {
    'Content-Type': 'application/json',
  },
});

export const searchPlaces = async (query: string, lat?: number, lon?: number): Promise<Place[]> => {
  if (!query || query.length < 2) return [];
  const params: Record<string, string | number> = { q: query };
  if (lat !== undefined) params.lat = lat;
  if (lon !== undefined) params.lon = lon;
  
  const response = await apiClient.get<Place[]>('/search', { params });
  return response.data;
};

export const geocodeAddress = async (address: string) => {
  const response = await apiClient.post('/places/geocode', { address });
  return response.data;
};

export const checkDuplicatePlace = async (latitude: number, longitude: number, name: string) => {
  const response = await apiClient.post('/places/check-duplicate', { latitude, longitude, name });
  return response.data;
};

export const addManualPlace = async (placeData: any) => {
  const response = await apiClient.post('/places/manual', placeData);
  return response.data;
};
