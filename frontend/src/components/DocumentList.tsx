import React from 'react';

interface Document {
  document_id: string;
  filename: string;
  file_type: string;
  size: number;
}

interface DocumentListProps {
  documents: Document[];
  selectedDocument?: string;
  onSelectDocument: (documentId: string | undefined) => void;
  onDeleteDocument: (documentId: string) => void;
  loading: boolean;
}

const DocumentList: React.FC<DocumentListProps> = ({
  documents,
  selectedDocument,
  onSelectDocument,
  onDeleteDocument,
  loading,
}) => {
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const getFileIcon = (fileType: string): string => {
    const type = fileType.toLowerCase();
    if (type.includes('pdf')) return '📄';
    if (type.includes('doc')) return '📝';
    if (type.includes('xls') || type.includes('csv')) return '📊';
    if (type.includes('ppt')) return '📑';
    if (type.includes('txt') || type.includes('md')) return '📃';
    if (type.includes('html')) return '🌐';
    if (type.includes('json')) return '🔧';
    return '📁';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-pulse text-gray-400">Loading...</div>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p className="text-sm">No documents uploaded yet</p>
        <p className="text-xs mt-1">Upload a document to get started</p>
      </div>
    );
  }

  return (
    <div className="space-y-2 max-h-96 overflow-y-auto">
      {/* All Documents Option */}
      <button
        onClick={() => onSelectDocument(undefined)}
        className={`
          w-full text-left p-3 rounded-lg transition-all
          ${!selectedDocument
            ? 'bg-blue-50 border-2 border-blue-500'
            : 'bg-gray-50 border-2 border-transparent hover:border-gray-300'
          }
        `}
      >
        <div className="flex items-center">
          <span className="text-2xl mr-3">📚</span>
          <div className="flex-1">
            <p className="font-medium text-sm text-gray-900">All Documents</p>
            <p className="text-xs text-gray-500">Search across all files</p>
          </div>
        </div>
      </button>

      {/* Individual Documents */}
      {documents.map((doc) => (
        <div
          key={doc.document_id}
          className={`
            p-3 rounded-lg border-2 transition-all
            ${selectedDocument === doc.document_id
              ? 'bg-blue-50 border-blue-500'
              : 'bg-gray-50 border-transparent hover:border-gray-300'
            }
          `}
        >
          <div className="flex items-start">
            <button
              onClick={() => onSelectDocument(doc.document_id)}
              className="flex-1 text-left flex items-start"
            >
              <span className="text-2xl mr-3">{getFileIcon(doc.file_type)}</span>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm text-gray-900 truncate">
                  {doc.filename}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {doc.file_type} • {formatFileSize(doc.size)}
                </p>
              </div>
            </button>
            
            <button
              onClick={(e) => {
                e.stopPropagation();
                if (window.confirm(`Delete ${doc.filename}?`)) {
                  onDeleteDocument(doc.document_id);
                }
              }}
              className="ml-2 p-1 text-red-500 hover:bg-red-50 rounded transition-colors"
              title="Delete document"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default DocumentList;
