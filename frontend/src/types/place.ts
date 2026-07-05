export interface Place {
  id: number;
  place_id?: number;
  name: string;
  category: string;
  type?: string;
  district?: string;
  state?: string;
  latitude: number;
  longitude: number;
  source: string;
  match_type: string;
  score: number;
  
  // Future compatibility fields
  phone?: string;
  website?: string;
  opening_hours?: string;
  rating?: number;
  reviews_count?: number;
  
  // Existing advanced scoring
  matched_by?: string;
  base_score?: number;
  token_bonus?: number;
  category_bonus?: number;
  admin_bonus?: number;
  pincode_bonus?: number;
  provider_bonus?: number;
  importance_bonus?: number;
  popularity_bonus?: number;
  distance_bonus?: number;
  final_score?: number;
  distance_meters?: number;
  pincode?: string;
  country?: string;
}

export interface UserLocation {
  latitude: number;
  longitude: number;
  accuracy: number;
  timestamp: number;
}
