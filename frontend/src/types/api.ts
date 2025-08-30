export interface Token {
  surface: string;
  reading: string;
  mora_count: number;
  pos: string;
}

export interface SenryuPhrase {
  tokens: Token[];
  mora_count: number;
  text: string;
  reading: string;
}

export interface DetectionResult {
  pattern: "5-7-5" | "5-8-5" | "6-7-5" | "5-7-6";
  upper_phrase: SenryuPhrase | null;
  middle_phrase: SenryuPhrase | null;
  lower_phrase: SenryuPhrase | null;
  start_position: number;
  end_position: number;
  original_text: string;
  is_valid: boolean;
  mora_pattern?: [number, number, number] | null;
  full_reading?: string | null;
  is_standard_pattern?: boolean;
}

export interface DetectRequest {
  text: string;
  only_valid?: boolean;
  details?: boolean;
}

export interface DetectResponse {
  success: boolean;
  results: DetectionResult[];
  count: number;
}

export interface HealthResponse {
  status: string;
  message: string;
  version: string;
}

export interface ErrorResponse {
  success: false;
  error: string;
  detail?: string;
}
