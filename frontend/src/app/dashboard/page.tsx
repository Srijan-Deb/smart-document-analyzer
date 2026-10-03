"use client";

import { useState, useEffect, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import { UploadCloud, FileText, Loader2, Calendar, Trash2 } from "lucide-react";
import api from "@/services/api";

interface Document {
  id: number;
  file_name: string;
  upload_date: string;
}

export default function DashboardPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoadingDocs, setIsLoadingDocs] = useState(true);
  const [isDeleting, setIsDeleting] = useState<number | null>(null);

  const deleteDocument = async (id: number) => {
    if (!confirm("Are you sure you want to delete this document?")) return;
    setIsDeleting(id);
    try {
      await api.delete(`/documents/${id}`);
      setDocuments(prev => prev.filter(doc => doc.id !== id));
    } catch (err) {
      console.error("Failed to delete document", err);
      alert("Failed to delete document.");
    } finally {
      setIsDeleting(null);
    }
  };

  const fetchDocuments = useCallback(async () => {
    try {
      const res = await api.get("/documents/");
      setDocuments(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoadingDocs(false);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchDocuments();
  }, [fetchDocuments]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      await api.post("/documents/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      await fetchDocuments();
    } catch (err) {
      console.error("Upload failed", err);
    } finally {
      setIsUploading(false);
    }
  }, [fetchDocuments]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "text/plain": [".txt"],
    },
    maxFiles: 1,
  });

  return (
    <div className="space-y-8 h-full flex flex-col">
      <div>
        <h1 className="text-3xl font-bold">Your Documents</h1>
        <p className="text-zinc-400 mt-1">Upload and manage your files for analysis</p>
      </div>

      {/* Upload Zone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-3xl p-12 text-center transition-all cursor-pointer ${
          isDragActive ? "border-indigo-500 bg-indigo-500/5" : "border-zinc-800 bg-zinc-900/30 hover:border-zinc-700 hover:bg-zinc-900/50"
        }`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center justify-center gap-4">
          <div className={`w-16 h-16 rounded-full flex items-center justify-center ${isDragActive ? "bg-indigo-500/20 text-indigo-400" : "bg-zinc-800 text-zinc-400"}`}>
            {isUploading ? <Loader2 className="w-8 h-8 animate-spin" /> : <UploadCloud className="w-8 h-8" />}
          </div>
          <div>
            <p className="text-lg font-medium text-zinc-200">
              {isUploading ? "Uploading & Processing..." : isDragActive ? "Drop the file here" : "Drag & drop a file here, or click to select"}
            </p>
            <p className="text-sm text-zinc-500 mt-1">Supports PDF, TXT up to 50MB</p>
          </div>
        </div>
      </div>

      {/* Document List */}
      <div className="flex-1">
        <h2 className="text-xl font-semibold mb-4">Recent Files</h2>
        {isLoadingDocs ? (
          <div className="flex items-center justify-center h-40">
            <Loader2 className="w-8 h-8 animate-spin text-zinc-500" />
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center py-12 border border-zinc-800/50 rounded-2xl bg-zinc-900/20">
            <FileText className="w-12 h-12 text-zinc-700 mx-auto mb-3" />
            <p className="text-zinc-400 font-medium">No documents yet</p>
            <p className="text-zinc-500 text-sm mt-1">Upload your first file to get started</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <AnimatePresence>
              {documents.map((doc) => (
                <motion.div
                  key={doc.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="p-5 rounded-2xl border border-zinc-800/50 bg-zinc-900/30 backdrop-blur-sm hover:border-indigo-500/50 hover:bg-zinc-900/80 transition-all group"
                >
                  <div className="flex items-start gap-4">
                    <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400 group-hover:scale-110 transition-transform shrink-0">
                      <FileText className="w-5 h-5" />
                    </div>
                    <div className="flex-1 min-w-0 pr-8 relative">
                      <h3 className="text-sm font-semibold text-zinc-200 truncate pr-2" title={doc.file_name}>
                        {doc.file_name}
                      </h3>
                      <div className="flex items-center gap-1.5 text-xs text-zinc-500 mt-1">
                        <Calendar className="w-3.5 h-3.5" />
                        {new Date(doc.upload_date).toLocaleDateString()}
                      </div>
                      
                      <button
                        onClick={() => deleteDocument(doc.id)}
                        disabled={isDeleting === doc.id}
                        className="absolute right-0 top-1/2 -translate-y-1/2 p-2 rounded-lg text-zinc-500 hover:text-red-400 hover:bg-red-400/10 transition-colors opacity-0 group-hover:opacity-100 disabled:opacity-50"
                        title="Delete document"
                      >
                        {isDeleting === doc.id ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <Trash2 className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </div>
  );
}
