import axios, { AxiosInstance } from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Upload document
  async uploadDocument(file: File): Promise<{
    success: boolean;
    document_id: string;
    filename: string;
    chunks: number;
    characters: number;
    message: string;
  }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  // List documents
  async listDocuments(): Promise<Array<{
    document_id: string;
    filename: string;
    file_type: string;
    size: number;
  }>> {
    const response = await this.client.get('/api/documents');
    return response.data;
  }

  // Delete document
  async deleteDocument(documentId: string): Promise<{
    success: boolean;
    document_id: string;
    chunks_deleted: number;
    message: string;
  }> {
    const response = await this.client.delete(`/api/documents/${documentId}`);
    return response.data;
  }

  // Chat (non-streaming)
  async chat(question: string, documentId?: string, topK: number = 5): Promise<{
    answer: string;
    sources: Array<{
      filename: string;
      chunk_id: number;
      score: number;
      text: string;
    }>;
  }> {
    const response = await this.client.post('/api/chat', {
      question,
      document_id: documentId,
      top_k: topK,
      stream: false,
    });

    return response.data;
  }

  // Chat streaming
  async chatStream(
    question: string,
    onChunk: (chunk: string) => void,
    onSources: (sources: any[]) => void,
    onError: (error: Error) => void,
    onComplete: () => void,
    documentId?: string,
    topK: number = 5
  ): Promise<void> {
    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question,
          document_id: documentId,
          top_k: topK,
          stream: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            
            if (data === '[DONE]') {
              onComplete();
              return;
            }

            try {
              const parsed = JSON.parse(data);
              if (parsed.type === 'sources') {
                onSources(parsed.data);
              } else if (parsed.type === 'answer') {
                onChunk(parsed.data);
              }
            } catch (e) {
              // Ignore parse errors
            }
          }
        }
      }

      onComplete();
    } catch (error) {
      onError(error as Error);
    }
  }

  // Health check
  async healthCheck(): Promise<{
    api: string;
    qdrant: string;
    ollama: string;
  }> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export default new ApiService();
