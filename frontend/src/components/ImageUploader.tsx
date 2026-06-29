"use client";

import { useCallback, useState } from "react";
import { Upload } from "lucide-react";

interface Props {
  label: string;
  onFileSelect: (file: File) => void;
  preview?: string | null;
}

export default function ImageUploader({ label, onFileSelect, preview }: Props) {
  const [dragOver, setDragOver] = useState(false);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file && file.type.startsWith("image/")) {
        onFileSelect(file);
      }
    },
    [onFileSelect]
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        onFileSelect(file);
      }
    },
    [onFileSelect]
  );

  return (
    <div
      className={`relative border-2 border-dashed rounded-xl p-6 text-center transition-colors cursor-pointer ${
        dragOver
          ? "border-[var(--primary)] bg-[var(--primary)]/5"
          : "border-[var(--card-border)] hover:border-[var(--muted)]"
      }`}
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      onClick={() => document.getElementById(`upload-${label}`)?.click()}
    >
      <input
        id={`upload-${label}`}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleChange}
      />
      {preview ? (
        <img
          src={preview}
          alt="Preview"
          className="mx-auto max-h-64 rounded-lg object-contain"
        />
      ) : (
        <div className="flex flex-col items-center gap-3 py-8">
          <Upload className="w-10 h-10 text-[var(--muted)]" />
          <p className="text-[var(--muted)]">{label}</p>
          <p className="text-xs text-[var(--muted)]">
            支持 JPG, PNG, TIFF (最大 20MB)
          </p>
        </div>
      )}
    </div>
  );
}
