export interface DetectionResult {
  text: string;
  pattern: string;
  mora_counts: number[];
  is_valid: boolean;
  confidence: number;
  segments: Array<{
    text: string;
    mora_count: number;
  }>;
}

export interface DetectRequest {
  text: string;
  only_valid?: boolean;
}

export interface DetectResponse {
  success: boolean;
  text: string;
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
