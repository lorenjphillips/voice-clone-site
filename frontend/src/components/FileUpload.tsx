import { useState, useRef } from 'react';
import { Upload } from 'lucide-react';

interface FileUploadProps {
  onFileSelect: (file: File | null) => void;
}

const FileUploadComponent = ({ onFileSelect }: FileUploadProps) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const supportedFormats = ['WAV', 'MP3', 'FLAC', 'M4A', 'OGG'];

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileSelect = (file: File) => {
    const fileExtension = file.name.split('.').pop()?.toLowerCase();
    const supportedExtensions = ['wav', 'mp3', 'flac', 'm4a', 'ogg'];
    
    if (supportedExtensions.includes(fileExtension || '')) {
      setSelectedFile(file);
      onFileSelect(file);
    } else {
      alert('Please select a supported audio file format (WAV, MP3, FLAC, M4A, OGG)');
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const clearFile = () => {
    setSelectedFile(null);
    onFileSelect(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="glass-card p-4 space-y-3">
      <h3 className="text-lg font-semibold text-foreground">
        Voice Cloning - Optional
      </h3>
      
      <p className="text-sm text-muted-foreground">
        Upload a sample of the voice you want to clone
      </p>

      <div
        className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-all duration-300 ${
          isDragOver
            ? 'border-red-500 bg-red-500/10'
            : 'border-border hover:border-red-400 hover:bg-red-400/5'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".wav,.mp3,.flac,.m4a,.ogg"
          onChange={handleInputChange}
          className="hidden"
        />
        
        <div className="space-y-2">
          <Upload className="w-8 h-8 mx-auto text-muted-foreground" />
          
          {selectedFile ? (
            <div className="space-y-1">
              <p className="text-sm font-medium text-foreground">
                {selectedFile.name}
              </p>
              <p className="text-xs text-muted-foreground">
                Size: {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
              </p>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  clearFile();
                }}
                className="mt-1 px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-xs rounded transition-colors"
              >
                Remove
              </button>
            </div>
          ) : (
            <div className="space-y-1">
              <p className="text-sm font-medium text-foreground">
                Choose audio file or drag & drop
              </p>
              <p className="text-xs text-muted-foreground">
                Supported formats: {supportedFormats.join(', ')}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FileUploadComponent;
