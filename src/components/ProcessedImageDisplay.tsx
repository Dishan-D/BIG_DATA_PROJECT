import { Download, ZoomIn } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";

interface ProcessedImageDisplayProps {
  imageUrl: string;
  originalFileName: string;
}

export const ProcessedImageDisplay = ({ 
  imageUrl, 
  originalFileName 
}: ProcessedImageDisplayProps) => {
  const [isZoomed, setIsZoomed] = useState(false);

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = `processed_${originalFileName}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="w-full bg-card border border-border rounded-lg p-6 shadow-md animate-slide-in">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-foreground">
            Processed Image
          </h3>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsZoomed(!isZoomed)}
            >
              <ZoomIn className="w-4 h-4 mr-2" />
              {isZoomed ? 'Fit' : 'Zoom'}
            </Button>
            <Button
              variant="default"
              size="sm"
              onClick={handleDownload}
              className="bg-gradient-primary shadow-glow"
            >
              <Download className="w-4 h-4 mr-2" />
              Download
            </Button>
          </div>
        </div>

        <div 
          className={`
            relative bg-muted rounded-lg overflow-hidden
            ${isZoomed ? 'max-h-none' : 'max-h-[600px]'}
          `}
        >
          <img
            src={imageUrl}
            alt="Processed result"
            className={`
              w-full h-auto
              ${isZoomed ? 'object-contain' : 'object-cover'}
            `}
          />
        </div>

        <p className="text-sm text-muted-foreground text-center">
          Click download to save your processed image
        </p>
      </div>
    </div>
  );
};
