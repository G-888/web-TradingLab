import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { ShieldAlert, CheckCircle2, XCircle, Link as LinkIcon } from "lucide-react"
import { Badge } from "@/components/ui/badge"

export default async function SettingsPage() {
  const health = await api.getHealth();
  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

  return (
    <div className="space-y-8 max-w-4xl">
      <div className="flex flex-col gap-4 md:flex-row md:justify-between md:items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">System Settings</h2>
          <p className="text-muted-foreground mt-1">Configure dashboard and API connections.</p>
        </div>
      </div>

      <Alert className="border-primary/50 bg-primary/5 text-primary">
        <ShieldAlert className="h-5 w-5 !text-primary" />
        <AlertTitle className="font-bold">READ ONLY MODE ACTIVE</AlertTitle>
        <AlertDescription className="text-muted-foreground">
          The dashboard is currently running in safe local development mode. 
          Live trading, EA execution, and database modification controls are completely disabled.
        </AlertDescription>
      </Alert>

      <Card>
        <CardHeader>
          <CardTitle>API Connection</CardTitle>
          <CardDescription>Backend integration details and health status.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
             <div className="space-y-3">
               <label className="text-sm font-medium text-muted-foreground">Connection Status</label>
               <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg border">
                 {health?.status === 'ok' ? (
                   <CheckCircle2 className="h-5 w-5 text-green-500" />
                 ) : (
                   <XCircle className="h-5 w-5 text-red-500" />
                 )}
                 <span className="font-semibold">{health?.status === 'ok' ? 'Connected & Healthy' : 'Offline / Error'}</span>
               </div>
             </div>
             
             <div className="space-y-3">
               <label className="text-sm font-medium text-muted-foreground">FastAPI Base URL</label>
               <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg border font-mono text-sm">
                 <LinkIcon className="h-4 w-4 text-muted-foreground" />
                 {apiBase}
               </div>
             </div>
          </div>
          
          <div className="pt-4 border-t">
            <h4 className="text-sm font-medium mb-3">Permissions</h4>
            <div className="flex flex-wrap gap-2">
               <Badge variant="outline" className="text-green-500 border-green-500/30">Read Database</Badge>
               <Badge variant="outline" className="text-green-500 border-green-500/30">View Signals</Badge>
               <Badge variant="outline" className="text-red-500 border-red-500/30 line-through">Write Database</Badge>
               <Badge variant="outline" className="text-red-500 border-red-500/30 line-through">Execute Trades</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
