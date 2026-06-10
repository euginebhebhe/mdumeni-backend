/**
 * MDUMENI — Province Index (Master)
 * ===================================
 * The single entry point for all agricultural services data.
 * The app ONLY imports from this file — never from individual province files.
 *
 * Architecture:
 *   - Province JSON files are bundled in the app for offline access
 *   - This index lazy-loads only the active farmer's province on startup
 *   - Online: POST /services/nearby returns GPS-sorted results from Supabase
 *   - Offline: falls back to bundled JSON + Haversine distance sort
 *
 * Adding a new province:
 *   1. Create src/data/provinces/province_NAME.json following the ProvinceData schema
 *   2. Add one entry to PROVINCE_REGISTRY below
 *   3. Done — all query functions work automatically
 */

import type {
  ProvinceData, ServiceLocation, ServiceType,
  NearbyQuery, NearbyResult, DistrictInfo,
} from './locationTypes';

// ── Province registry ─────────────────────────────────────────────────────────
// Maps province name to its lazy loader. Only the active province is ever loaded
// into memory. React Native's Metro bundler includes all JSON in the app bundle
// for offline access, but JS heap only holds the one the farmer is in.

const PROVINCE_REGISTRY: Record<string, () => ProvinceData> = {
  'Harare':              () => require('./provinces/province_harare.json'),
  'Bulawayo':            () => require('./provinces/province_bulawayo.json'),
  'Manicaland':          () => require('./provinces/province_manicaland.json'),
  'Mashonaland Central': () => require('./provinces/province_mashonaland_central.json'),
  'Mashonaland East':    () => require('./provinces/province_mashonaland_east.json'),
  'Mashonaland West':    () => require('./provinces/province_mashonaland_west.json'),
  'Masvingo':            () => require('./provinces/province_masvingo.json'),
  'Matabeleland North':  () => require('./provinces/province_matabeleland_north.json'),
  'Matabeleland South':  () => require('./provinces/province_matabeleland_south.json'),
  'Midlands':            () => require('./provinces/province_midlands.json'),
};

// ── In-memory cache — one province at a time ──────────────────────────────────
let _cached_province: string | null = null;
let _cached_data: ProvinceData | null = null;

// ── Haversine distance (km) between two lat/lng points ───────────────────────
function haversine(lat1: number, lng1: number, lat2: number, lng2: number): number {
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
    Math.cos((lat2 * Math.PI) / 180) *
    Math.sin(dLng / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

// ── Core loader ───────────────────────────────────────────────────────────────

/**
 * Load province data — returns cached version if same province.
 * Synchronous (require() is sync in Metro bundler with bundled JSON).
 */
export function loadProvince(province: string): ProvinceData | null {
  if (!PROVINCE_REGISTRY[province]) {
    console.warn(`[ProvinceIndex] Unknown province: "${province}"`);
    return null;
  }
  if (_cached_province === province && _cached_data) return _cached_data;
  try {
    _cached_data     = PROVINCE_REGISTRY[province]();
    _cached_province = province;
    return _cached_data;
  } catch (e) {
    console.error(`[ProvinceIndex] Failed to load province "${province}":`, e);
    return null;
  }
}

/**
 * Preload a province into cache — call in background after onboarding.
 * No-op if already cached.
 */
export function preloadProvince(province: string): void {
  loadProvince(province);
}

// ── Public query API ──────────────────────────────────────────────────────────

/**
 * Get all services in a province, optionally filtered by type.
 */
export function getServices(
  province: string,
  types?: ServiceType | ServiceType[],
): ServiceLocation[] {
  const data = loadProvince(province);
  if (!data) return [];
  const typeFilter = types ? (Array.isArray(types) ? types : [types]) : null;
  if (!typeFilter) return data.services;
  return data.services.filter(s => typeFilter.includes(s.type));
}

/**
 * Find services near a GPS point, sorted by distance.
 * Filters by province for offline safety — GPS-accurate sorting when online.
 */
export function findNearby(query: NearbyQuery): NearbyResult[] {
  const { lat, lng, province, type, crop_id, radius_km = 100, limit = 15 } = query;
  const data = loadProvince(province);
  if (!data) return [];

  let services = data.services;

  // Type filter
  if (type) {
    const types = Array.isArray(type) ? type : [type];
    services = services.filter(s => types.includes(s.type));
  }

  // Crop filter — services with crops_served: [] serve all crops
  if (crop_id) {
    services = services.filter(
      s => s.crops_served.length === 0 || s.crops_served.includes(crop_id),
    );
  }

  // Distance sort and radius filter
  const results: NearbyResult[] = services
    .map(s => ({
      ...s,
      distance_km: haversine(lat, lng, s.lat, s.lng),
    }))
    .filter(s => s.distance_km <= radius_km)
    .sort((a, b) => a.distance_km - b.distance_km)
    .slice(0, limit);

  return results;
}

/**
 * Get all agro dealers in a province.
 * If crop_id is supplied, prioritises dealers that stock inputs for that crop.
 */
export function getAgroDealers(province: string, crop_id?: string): ServiceLocation[] {
  return getServices(province, 'agro_dealer').filter(
    s => !crop_id || s.crops_served.length === 0 || s.crops_served.includes(crop_id),
  );
}

/**
 * Get all GMB depots in a province with their accepted crops.
 */
export function getGmbDepots(province: string): ServiceLocation[] {
  return getServices(province, 'gmb_depot');
}

/**
 * Get seed companies / outlets in a province, optionally for a specific crop.
 */
export function getSeedOutlets(province: string, crop_id?: string): ServiceLocation[] {
  return getServices(province, 'seed_company').filter(
    s => !crop_id || s.crops_served.length === 0 || s.crops_served.includes(crop_id),
  );
}

/**
 * Get all fresh produce and livestock markets in a province.
 */
export function getMarkets(province: string): ServiceLocation[] {
  return getServices(province, ['fresh_market', 'livestock_market']);
}

/**
 * Get the AGRITEX office for a specific district.
 * Returns null if no office data found for that district.
 */
export function getExtensionOffice(province: string, district: string): ServiceLocation | null {
  const offices = getServices(province, 'agritex_office');
  return offices.find(o => o.district.toLowerCase() === district.toLowerCase()) ?? null;
}

/**
 * Get financial services (agricultural banks, AFC, microfinance) in a province.
 */
export function getFinancialServices(province: string): ServiceLocation[] {
  return getServices(province, 'financial_service');
}

/**
 * Get specialty buyers for a specific crop in a province.
 * Critical for new crops: coffee, tea, macadamia, passion fruit.
 */
export function getSpecialtyBuyers(province: string, crop_id: string): ServiceLocation[] {
  return getServices(province, 'specialty_buyer').filter(
    s => s.crops_served.includes(crop_id),
  );
}

/**
 * Get district metadata for a province (agro-region, rainfall, main crops).
 */
export function getDistrictInfo(province: string, district?: string): DistrictInfo[] {
  const data = loadProvince(province);
  if (!data) return [];
  if (district) {
    return data.districts.filter(d => d.name.toLowerCase() === district.toLowerCase());
  }
  return data.districts;
}

/**
 * Get all province names — used to populate province picker in onboarding.
 */
export function getAllProvinceNames(): string[] {
  return Object.keys(PROVINCE_REGISTRY);
}

/**
 * Get all districts for a province — used in onboarding district picker.
 */
export function getDistrictNames(province: string): string[] {
  const data = loadProvince(province);
  if (!data) return [];
  return data.districts.map(d => d.name);
}

/**
 * Build a farmer-facing summary of available services in their district.
 * Returns counts by category for the Settings "nearby services" card.
 */
export function getServiceSummary(province: string, district: string): Record<string, number> {
  const data = loadProvince(province);
  if (!data) return {};

  const districtServices = data.services.filter(
    s => s.district.toLowerCase() === district.toLowerCase(),
  );

  const summary: Record<string, number> = {};
  for (const s of districtServices) {
    summary[s.type] = (summary[s.type] ?? 0) + 1;
  }
  return summary;
}

// ── Backend sync helper ───────────────────────────────────────────────────────
// When online, the app calls POST /services/nearby which does a proper
// PostGIS ST_DWithin query and returns GPS-accurate results from Supabase.
// This function formats the local query to match the API request body
// so the caller code is identical whether online or offline.

export function buildApiQuery(query: NearbyQuery): object {
  return {
    lat:       query.lat,
    lng:       query.lng,
    province:  query.province,
    types:     query.type ? (Array.isArray(query.type) ? query.type : [query.type]) : null,
    crop_id:   query.crop_id ?? null,
    radius_km: query.radius_km ?? 100,
    limit:     query.limit ?? 15,
  };
}
