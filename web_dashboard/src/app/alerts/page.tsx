import { api } from '@/lib/api';
import EmptyState from '@/components/dashboard/EmptyState';
import StatusBadge from '@/components/dashboard/StatusBadge';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from '@/components/ui/badge';

export default async function AlertsPage() {
  const alerts = await api.getAlerts() || [];
  
  const activeCount = alerts.filter((a: any) => a.triggered === 0).length;

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 md:flex-row md:justify-between md:items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Alerts</h2>
          <p className="text-muted-foreground mt-1">Manage and review price threshold alerts.</p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
         <Card>
           <CardHeader className="pb-2">
             <CardTitle className="text-sm font-medium text-muted-foreground">Active Alerts</CardTitle>
           </CardHeader>
           <CardContent>
             <div className="text-3xl font-bold text-primary">{activeCount}</div>
           </CardContent>
         </Card>
         <Card>
           <CardHeader className="pb-2">
             <CardTitle className="text-sm font-medium text-muted-foreground">Triggered</CardTitle>
           </CardHeader>
           <CardContent>
             <div className="text-3xl font-bold">{alerts.length - activeCount}</div>
           </CardContent>
         </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Alert Log</CardTitle>
          <CardDescription>A list of recent active and triggered system alerts.</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          {alerts.length === 0 ? (
            <div className="p-8">
              <EmptyState message="No alerts found." />
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Alert ID</TableHead>
                  <TableHead>Direction</TableHead>
                  <TableHead className="text-right">Price Target</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right w-[200px]">Created At</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {alerts.map((alert: any, i: number) => (
                  <TableRow key={i}>
                    <TableCell className="font-mono text-muted-foreground">#{alert.id}</TableCell>
                    <TableCell><StatusBadge status={alert.direction} /></TableCell>
                    <TableCell className="text-right font-mono font-medium">{alert.price ? alert.price.toFixed(2) : '-'}</TableCell>
                    <TableCell><Badge variant="outline">{alert.alert_type}</Badge></TableCell>
                    <TableCell>
                      {alert.triggered === 1 ? (
                         <Badge variant="secondary" className="bg-muted text-muted-foreground">Triggered</Badge>
                      ) : (
                         <Badge className="bg-blue-500/15 text-blue-500 hover:bg-blue-500/25 border-none shadow-none">Active</Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-right text-muted-foreground">{alert.created_at}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
