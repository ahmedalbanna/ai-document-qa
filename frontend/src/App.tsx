import React, { useState, useEffect } from 'react';
import FileUpload from './components/FileUpload';
import DocumentList from './components/DocumentList';
import ChatInterface from './components/ChatInterface';
import apiService from './services/api';

interface Document {
  document_id: string;
  filename: string;
  file_type: string;
  size: number;
}

function App() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<string | undefined>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load documents on mount
  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const docs = await apiService.listDocuments();
      setDocuments(docs);
      setError(null);
    } catch (err) {
      setError('Failed to load documents');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSuccess = () => {
    loadDocuments();
  };

  const handleDeleteDocument = async (documentId: string) => {
    try {
      await apiService.deleteDocument(documentId);
      if (selectedDocument === documentId) {
        setSelectedDocument(undefined);
      }
      loadDocuments();
    } catch (err) {
      setError('Failed to delete document');
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                🤖 AI Document QA System
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                Upload documents and ask questions using RAG-powered AI
              </p>
            </div>
            <div className="flex items-center space-x-2 text-sm">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                <span className="w-2 h-2 mr-2 bg-green-500 rounded-full animate-pulse"></span>
                Online
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Sidebar - Upload & Documents */}
          <div className="lg:col-span-1 space-y-6">
            {/* Upload Section */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                📁 Upload Documents
              </h2>
              <FileUpload onUploadSuccess={handleUploadSuccess} />
            </div>

            {/* Documents List */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                📚 My Documents ({documents.length})
              </h2>
              <DocumentList
                documents={documents}
                selectedDocument={selectedDocument}
                onSelectDocument={setSelectedDocument}
                onDeleteDocument={handleDeleteDocument}
                loading={loading}
              />
            </div>
          </div>

          {/* Right Section - Chat Interface */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md h-[calc(100vh-12rem)]">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-xl font-semibold text-gray-900">
                  💬 Ask Questions
                </h2>
                <p className="mt-1 text-sm text-gray-600">
                  {selectedDocument
                    ? `Asking about: ${documents.find(d => d.document_id === selectedDocument)?.filename}`
                    : 'Ask questions about all uploaded documents'}
                </p>
              </div>
              <ChatInterface
                documentId={selectedDocument}
                hasDocuments={documents.length > 0}
              />
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-8 bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            Powered by Ollama + Qdrant + React | RAG-based Document QA System
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
