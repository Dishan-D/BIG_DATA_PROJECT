import { useState, useEffect } from "react";
import { ImageUpload } from "@/components/ImageUpload";
import { ProcessingTypeSelector } from "@/components/ProcessingTypeSelector";
import { ProgressTracker } from "@/components/ProgressTracker";
import { ProcessedImageDisplay } from "@/components/ProcessedImageDisplay";
import { WorkerDashboard } from "@/components/WorkerDashboard";
import { Button } from "@/components/ui/button";
import { toast } from "@/hooks/use-toast";
import { Layers } from "lucide-react";

// Mock data for development - replace with actual API calls
const mockWorkers = [
  {
    id: "worker-001",
    status: "active" as const,
    lastHeartbeat: new Date(Date.now() - 5000),
    tasksCompleted: 42,
  },
  {
    id: "worker-002",
    status: "active" as const,
    lastHeartbeat: new Date(Date.now() - 3000),
    tasksCompleted: 38,
  },
  {
    id: "worker-003",
    status: "idle" as const,
    lastHeartbeat: new Date(Date.now() - 15000),
    tasksCompleted: 51,
  },
];

const Index = () => {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [processingType, setProcessingType] = useState<string>("");
  const [jobStatus, setJobStatus] = useState<'idle' | 'processing' | 'completed' | 'error'>('idle');
  const [progress, setProgress] = useState(0);
  const [tilesProcessed, setTilesProcessed] = useState(0);
  const [totalTiles, setTotalTiles] = useState(0);
  const [processedImageUrl, setProcessedImageUrl] = useState<string | null>(null);
  const [workers] = useState(mockWorkers);

  // Simulate processing for demo purposes
  const simulateProcessing = () => {
    if (!selectedImage || !processingType) {
      toast({
        title: "Missing information",
        description: "Please select an image and processing type",
        variant: "destructive",
      });
      return;
    }

    setJobStatus('processing');
    setProgress(0);
    setTilesProcessed(0);
    setTotalTiles(16); // Mock total tiles

    // Simulate progress
    let currentProgress = 0;
    const interval = setInterval(() => {
      currentProgress += Math.random() * 15;
      if (currentProgress >= 100) {
        currentProgress = 100;
        setJobStatus('completed');
        setProgress(100);
        setTilesProcessed(16);
        
        // Create a mock processed image (same as original for demo)
        setProcessedImageUrl(URL.createObjectURL(selectedImage));
        
        toast({
          title: "Processing complete!",
          description: "Your image has been processed successfully",
        });
        clearInterval(interval);
      } else {
        setProgress(currentProgress);
        setTilesProcessed(Math.floor((currentProgress / 100) * 16));
      }
    }, 500);
  };

  const handleStartProcessing = () => {
    // In production, replace simulateProcessing with actual API call:
    // try {
    //   const response = await api.uploadImage(selectedImage, processingType);
    //   // Then poll for status using response.job_id
    // } catch (error) {
    //   toast({ title: "Error", description: error.message, variant: "destructive" });
    // }
    
    simulateProcessing();
  };

  const handleReset = () => {
    setSelectedImage(null);
    setProcessingType("");
    setJobStatus('idle');
    setProgress(0);
    setTilesProcessed(0);
    setTotalTiles(0);
    if (processedImageUrl) {
      URL.revokeObjectURL(processedImageUrl);
    }
    setProcessedImageUrl(null);
  };

  return (
    <div className="min-h-screen bg-gradient-bg">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-40 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-primary rounded-lg shadow-glow">
              <Layers className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">
                Distributed Image Processor
              </h1>
              <p className="text-sm text-muted-foreground">
                High-performance tile-based image processing
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Upload & Controls */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-card border border-border rounded-lg p-6 shadow-md">
              <h2 className="text-xl font-bold text-foreground mb-6">
                Upload & Configure
              </h2>
              
              <div className="space-y-6">
                <ImageUpload
                  onImageSelect={setSelectedImage}
                  selectedImage={selectedImage}
                  onClear={() => setSelectedImage(null)}
                />

                <ProcessingTypeSelector
                  value={processingType}
                  onChange={setProcessingType}
                />

                <div className="flex gap-3">
                  <Button
                    onClick={handleStartProcessing}
                    disabled={!selectedImage || !processingType || jobStatus === 'processing'}
                    className="flex-1 bg-gradient-primary shadow-glow hover:shadow-lg"
                    size="lg"
                  >
                    {jobStatus === 'processing' ? 'Processing...' : 'Start Processing'}
                  </Button>
                  
                  {(jobStatus === 'completed' || jobStatus === 'error') && (
                    <Button
                      onClick={handleReset}
                      variant="outline"
                      size="lg"
                    >
                      Reset
                    </Button>
                  )}
                </div>
              </div>
            </div>

            {/* Progress */}
            <ProgressTracker
              status={jobStatus}
              progress={progress}
              tilesProcessed={tilesProcessed}
              totalTiles={totalTiles}
            />

            {/* Result */}
            {processedImageUrl && jobStatus === 'completed' && (
              <ProcessedImageDisplay
                imageUrl={processedImageUrl}
                originalFileName={selectedImage?.name || 'image'}
              />
            )}
          </div>

          {/* Right Column - Worker Dashboard */}
          <div className="lg:col-span-1">
            <div className="sticky top-24">
              <WorkerDashboard workers={workers} />
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-card/50 backdrop-blur-sm mt-16">
        <div className="container mx-auto px-4 py-6">
          <p className="text-sm text-muted-foreground text-center">
            Ready to connect to your FastAPI backend. Update API endpoints in{" "}
            <code className="px-2 py-1 bg-muted rounded text-xs">src/lib/api.ts</code>
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
