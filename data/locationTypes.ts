/**
 * MDUMENI — Province Location Types
 * Shared types for the Zimbabwe agricultural services database.
 * Used by provinceIndex.ts and all province JSON files.
 */

// ── Service categories ────────────────────────────────────────────────────────

export type ServiceType =
  | 'agro_dealer'         // General agro input dealer
  | 'seed_company'        // Seed company branch or depot
  | 'gmb_depot'           // Grain Marketing Board depot / silo
  | 'fresh_market'        // Fresh produce market (vegetables, fruit)
  | 'livestock_market'    // Cattle / small livestock auction
  | 'cotton_depot'        // Cotton Marketing Board / Cottco buying point
  | 'tobacco_floor'       // Tobacco auction floor / buying station
  | 'agritex_office'      // AGRITEX district extension office
  | 'research_station'    // Agricultural research station
  | 'cooperative'         // Farmer cooperative or union office
  | 'financial_service'   // Agricultural bank, microfinance, insurance
  | 'irrigation_supplier' // Irrigation equipment / scheme office
  | 'equipment_dealer'    // Farm machinery and implements
  | 'processing_plant'    // Grain milling, oil pressing, juice processing
  | 'cold_storage'        // Cold chain / refrigerated storage
  | 'specialty_buyer';    // Specialty crop buyer (coffee, tea, macadamia etc.)

export type ProductCategory =
  | 'fertilisers'
  | 'seeds'
  | 'chemicals'           // Pesticides, herbicides, fungicides
  | 'equipment'           // Hand tools, sprayers, small equipment
  | 'machinery'           // Tractors, tillers, planters
  | 'irrigation'          // Pipes, drip kits, pumps
  | 'livestock_inputs'    // Dips, vaccines, feed
  | 'packaging'           // Bags, crates, packaging materials
  | 'grain_buying'        // Buying grain from farmers
  | 'produce_buying';     // Buying fresh produce from farmers

// ── Core location record ──────────────────────────────────────────────────────

export interface ServiceLocation {
  id:           string;           // e.g. "AGR_HAR_001" (type_province_sequence)
  name:         string;           // Display name
  type:         ServiceType;
  province:     string;           // Zimbabwe province name
  district:     string;           // District within province
  town:         string;           // Town / area name
  address:      string;           // Street address (approximate if unverified)
  phone:        string | null;    // Primary phone number
  phone_alt:    string | null;    // Alternative / WhatsApp number
  lat:          number;           // Latitude (negative for southern hemisphere)
  lng:          number;           // Longitude
  products:     ProductCategory[];
  seed_brands:  string[];         // e.g. ["Seed Co", "Pannar", "Syngenta"]
  crops_served: string[];         // Crop IDs from dataset, or [] for general
  open_hours:   string | null;    // Human-readable hours
  notes:        string | null;    // Important notes for farmer
  verified:     boolean;          // true = confirmed from official source
  last_verified: string;          // "YYYY-MM" — when record was last checked
}

// ── Specialised sub-types ─────────────────────────────────────────────────────

export interface GmbDepot extends ServiceLocation {
  type: 'gmb_depot';
  silo_capacity_tonnes: number | null;
  crops_accepted: string[];        // Crop names accepted e.g. ["Maize", "Wheat"]
  buying_seasons: string[];        // e.g. ["April–July", "Feb–April"]
  current_price_usd_t: number | null; // Latest GMB price per tonne (update seasonally)
}

export interface AgroDealer extends ServiceLocation {
  type: 'agro_dealer';
  zfc_franchise: boolean;          // Is this a ZFC franchise outlet?
  delivers: boolean;               // Offers delivery to farm?
  credit_available: boolean;       // Offers input credit?
}

export interface FinancialService extends ServiceLocation {
  type: 'financial_service';
  institution:    string;          // e.g. "Agribank", "AFC Holdings", "CBZ"
  services:       string[];        // e.g. ["crop loans", "equipment finance", "insurance"]
  min_loan_usd:   number | null;
  requires_title_deed: boolean;
}

export interface SpecialtyBuyer extends ServiceLocation {
  type: 'specialty_buyer';
  crops_bought:   string[];        // e.g. ["Coffee", "Macadamia", "Tea"]
  buying_price_usd_kg: number | null;
  quality_standard: string | null; // e.g. "Zimbabwe AA", "Grade 1"
  contract_farming: boolean;
}

// ── Province data file shape ──────────────────────────────────────────────────

export interface DistrictInfo {
  name:        string;
  agro_region: 1 | 2 | 3 | 4 | 5;
  area_km2:    number;
  population:  number | null;        // approx, from last census
  main_crops:  string[];             // primary crops grown in district
  rainfall_mm: number;               // average annual rainfall
  altitude_m:  number | null;        // average altitude
  headquarters: string;              // district administrative centre
}

export interface ProvinceData {
  province:     string;
  code:         string;             // 2-letter code e.g. "HA", "BU", "MA"
  agro_regions: (1 | 2 | 3 | 4 | 5)[];  // regions present in this province
  districts:    DistrictInfo[];
  services:     ServiceLocation[];
  last_updated: string;             // "YYYY-MM"
}

// ── App-facing query types ────────────────────────────────────────────────────

export interface NearbyQuery {
  lat:        number;
  lng:        number;
  province:   string;
  type?:      ServiceType | ServiceType[];
  crop_id?:   string;               // filter to services relevant to this crop
  radius_km?: number;               // default 50
  limit?:     number;               // default 10
}

export interface NearbyResult extends ServiceLocation {
  distance_km: number;              // calculated from query lat/lng
}
