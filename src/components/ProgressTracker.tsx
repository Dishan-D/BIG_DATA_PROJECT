import { Progress } from "@/components/ui/progress";
import { CheckCircle2, Loader2, AlertCircle } from "lucide-react";

interface ProgressTrackerProps {
  status: 'idle' | 'processing' | 'completed' | 'error';
  progress: number;
  tilesProcessed: number;
  totalTiles: number;
  message?: string;
}

export const ProgressTracker = ({
  status,
  progress,
  tilesProcessed,
  totalTiles,
  message = ''
}: ProgressTrackerProps) => {
  if (status === 'idle') return null;

  const getStatusColor = () => {
    switch (status) {
      case 'processing':
        return 'text-processing';
      case 'completed':
        return 'text-success';
      case 'error':
        return 'text-destructive';
      default:
        return 'text-muted-foreground';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'processing':
        return <Loader2 className="w-5 h-5 animate-spin text-processing" />;
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-success" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-destructive" />;
      default:
        return null;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'processing':
        return 'Processing image...';
      case 'completed':
        return 'Processing complete!';
      case 'error':
        return 'Processing failed';
      default:
        return '';
    }
  };

  return (
    <div className="w-full bg-card border border-border rounded-lg p-6 shadow-md animate-slide-in">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getStatusIcon()}
            <h3 className={`font-semibold ${getStatusColor()}`}>
              {getStatusText()}
            </h3>
          </div>
          <span className="text-sm font-medium text-muted-foreground">
            {tilesProcessed} / {totalTiles} tiles
          </span>
        </div>

        <Progress 
          value={progress} 
          className="h-2"
        />

        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">
            {progress.toFixed(1)}% complete
          </span>
          {message && (
            <span className="text-muted-foreground italic">
              {message}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
