import { Activity, Clock, Cpu } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface Worker {
  id: string;
  status: 'active' | 'idle' | 'offline';
  lastHeartbeat: Date;
  tasksCompleted?: number;
}

interface WorkerDashboardProps {
  workers: Worker[];
}

export const WorkerDashboard = ({ workers }: WorkerDashboardProps) => {
  const getStatusColor = (status: Worker['status']) => {
    switch (status) {
      case 'active':
        return 'bg-success text-success-foreground';
      case 'idle':
        return 'bg-warning text-warning-foreground';
      case 'offline':
        return 'bg-destructive text-destructive-foreground';
      default:
        return 'bg-muted text-muted-foreground';
    }
  };

  const getTimeSinceHeartbeat = (lastHeartbeat: Date) => {
    const seconds = Math.floor((new Date().getTime() - lastHeartbeat.getTime()) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ago`;
  };

  const activeWorkers = workers.filter(w => w.status === 'active').length;
  const idleWorkers = workers.filter(w => w.status === 'idle').length;

  return (
    <div className="w-full space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-foreground">Worker Dashboard</h2>
        <div className="flex gap-2">
          <Badge variant="outline" className="bg-success/10 text-success border-success/20">
            {activeWorkers} Active
          </Badge>
          <Badge variant="outline" className="bg-warning/10 text-warning border-warning/20">
            {idleWorkers} Idle
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {workers.map((worker) => (
          <Card 
            key={worker.id}
            className="p-4 bg-gradient-card border-border shadow-sm hover:shadow-md transition-all"
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-primary" />
                  <span className="font-mono text-sm font-medium">
                    {worker.id}
                  </span>
                </div>
                <Badge className={getStatusColor(worker.status)}>
                  {worker.status === 'active' && (
                    <Activity className="w-3 h-3 mr-1 animate-pulse-glow" />
                  )}
                  {worker.status}
                </Badge>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Clock className="w-3.5 h-3.5" />
                  <span>Last seen: {getTimeSinceHeartbeat(worker.lastHeartbeat)}</span>
                </div>
                {worker.tasksCompleted !== undefined && (
                  <div className="text-muted-foreground">
                    Tasks completed: <span className="font-medium text-foreground">{worker.tasksCompleted}</span>
                  </div>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>

      {workers.length === 0 && (
        <div className="text-center py-12 bg-muted/50 rounded-lg border border-dashed border-border">
          <p className="text-muted-foreground">No workers connected</p>
        </div>
      )}
    </div>
  );
};
