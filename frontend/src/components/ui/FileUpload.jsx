import React, { useRef, useState } from "react";
import { cn } from "../../lib/utils";
import { UploadCloud } from "lucide-react";

export function FileUpload({ onUpload, accept, maxBytes = 10 * 1024 * 1024, className }) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragging(true);
    } else if (e.type === "dragleave") {
      setIsDragging(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files[0]);
    }
  };

  const handleFiles = (file) => {
    if (file.size > maxBytes) {
      alert(`File is too large. Maximum size is ${maxBytes / (1024 * 1024)}MB.`);
      return;
    }
    onUpload?.(file);
  };

  return (
    <div
      className={cn(
        "relative flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-xl cursor-pointer transition-colors bg-surface",
        isDragging ? "border-brand-500 bg-brand-500/5" : "border-border hover:bg-surfaceHover",
        className
      )}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current?.click()}
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleChange}
        accept={accept}
        className="hidden"
      />
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-brand-500/10 mb-4">
        <UploadCloud className="h-6 w-6 text-brand-500" />
      </div>
      <p className="text-sm font-medium text-gray-200 mb-1">Click or drag file to this area to upload</p>
      <p className="text-xs text-gray-400">Supports {accept} up to {maxBytes / (1024 * 1024)}MB</p>
    </div>
  );
}
