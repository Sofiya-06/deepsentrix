import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({ baseURL: API_BASE });

export interface AnalysisResult {
  result_id: string;
  filename: string;
  is_fake: boolean;
  confidence: number;
  detection_type: 'real' | 'fake';
  details: Record<string, unknown>;
  protected_image?: string;
  protection_technique?: string;
  created_at: string;
}

export interface ProtectionResult {
  protected_image: string;
  technique: string;
  protection_level: string;
  details: Record<string, unknown>;
}

export interface StoredResult {
  result_id: string;
  filename: string;
  is_fake: boolean;
  confidence: number;
  detection_type: string;
  created_at: string;
}

export const analyzeImage = async (
  file: File,
  protectionTechnique = 'pixelate',
  protectionLevel = 'medium',
): Promise<AnalysisResult> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('protection_technique', protectionTechnique);
  formData.append('protection_level', protectionLevel);

  const response = await api.post<AnalysisResult>('/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const protectImage = async (
  file: File,
  technique = 'pixelate',
  level = 'medium',
): Promise<ProtectionResult> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('technique', technique);
  formData.append('level', level);

  const response = await api.post<ProtectionResult>('/protect', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const getResult = async (resultId: string): Promise<StoredResult> => {
  const response = await api.get<StoredResult>(`/results/${resultId}`);
  return response.data;
};

export const listResults = async (limit = 20): Promise<StoredResult[]> => {
  const response = await api.get<StoredResult[]>('/results', { params: { limit } });
  return response.data;
};
