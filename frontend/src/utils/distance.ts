export function formatDistance(meters?: number | null): string | null {
  if (meters === undefined || meters === null) {
    return null;
  }
  
  if (meters < 1000) {
    return `${Math.round(meters)} m`;
  }
  
  const km = (meters / 1000).toFixed(1);
  return `${km} km`;
}
