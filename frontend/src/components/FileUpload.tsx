import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import apiService from '../services/api';

interface FileUploadProps {
  onUploadSuccess: () => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploading(true);
    setError(null);
    setProgress(`Uploading ${file.name}...`);

    try {
      const result = await apiService.uploadDocument(file);
      setProgress(`✓ ${result.message} (${result.chunks} chunks created)`);
      
      setTimeout(() => {
        setProgress('');
        onUploadSuccess();
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload file');
      setProgress('');
    } finally {
      setUploading(false);
    }
  }, [onUploadSuccess]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/markdown': ['.md'],
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'application/vnd.ms-powerpoint': ['.ppt'],
      'text/html': ['.html', '.htm'],
      'application/json': ['.json'],
    },
    disabled: uploading,
  });

  return (
    <div>
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-all duration-200
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'}
          ${uploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="space-y-2">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
            aria-hidden="true"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          
          {uploading ? (
            <p className="text-sm text-gray-600">Uploading...</p>
          ) : (
            <>
              <p className="text-sm text-gray-600">
                {isDragActive ? (
                  <span className="font-semibold text-blue-600">Drop file here</span>
                ) : (
                  <>
                    <span className="font-semibold text-blue-600">Click to upload</span> or drag and drop
                  </>
                )}
              </p>
              <p className="text-xs text-gray-500">
                PDF, DOCX, TXT, MD, CSV, XLSX, PPTX, HTML, JSON
              </p>
            </>
          )}
        </div>
      </div>

      {/* Progress */}
      {progress && (
        <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-800">{progress}</p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Supported formats info */}
      <div className="mt-4 text-xs text-gray-500">
        <p className="font-medium mb-1">Supported formats:</p>
        <div className="flex flex-wrap gap-1">
          {['PDF', 'DOCX', 'TXT', 'MD', 'CSV', 'XLSX', 'PPTX', 'HTML', 'JSON'].map(format => (
            <span key={format} className="px-2 py-1 bg-gray-100 rounded">
              {format}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FileUpload;
