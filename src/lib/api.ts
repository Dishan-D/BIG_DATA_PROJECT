// API integration layer for FastAPI backend
// Update these endpoints to match your FastAPI server

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface UploadResponse {
  job_id: string;
  status: string;
  total_tiles: number;
}

export interface JobStatus {
  job_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  tiles_processed: number;
  total_tiles: number;
  message?: string;
}

export interface WorkerStatus {
  id: string;
  status: 'active' | 'idle' | 'offline';
  last_heartbeat: string;
  tasks_completed?: number;
}

export const api = {
  // Upload image and start processing
  uploadImage: async (file: File, processingType: string): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('processing_type', processingType);

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to upload image');
    }

    return response.json();
  },

  // Poll job status
  getJobStatus: async (jobId: string): Promise<JobStatus> => {
    const response = await fetch(`${API_BASE_URL}/status/${jobId}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch job status');
    }

    return response.json();
  },

  // Get processed image result
  getResult: async (jobId: string): Promise<Blob> => {
    const response = await fetch(`${API_BASE_URL}/result/${jobId}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch result');
    }

    return response.blob();
  },

  // Get worker status
  getWorkers: async (): Promise<WorkerStatus[]> => {
    const response = await fetch(`${API_BASE_URL}/workers`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch worker status');
    }

    return response.json();
  },
};
