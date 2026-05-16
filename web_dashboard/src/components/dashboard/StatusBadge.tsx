import { Badge } from "@/components/ui/badge"

interface StatusBadgeProps {
  status: string;
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const normalized = status.toUpperCase();
  
  if (normalized === 'BUY' || normalized === 'LONG' || normalized === 'WIN') {
    return <Badge className="bg-green-500/15 text-green-700 dark:text-green-400 hover:bg-green-500/25 border-green-500/20">{normalized}</Badge>;
  } else if (normalized === 'SELL' || normalized === 'SHORT' || normalized === 'LOSS') {
    return <Badge className="bg-red-500/15 text-red-700 dark:text-red-400 hover:bg-red-500/25 border-red-500/20">{normalized}</Badge>;
  } else if (normalized === 'ACTIVE') {
    return <Badge className="bg-blue-500/15 text-blue-700 dark:text-blue-400 hover:bg-blue-500/25 border-blue-500/20">{normalized}</Badge>;
  }

  return <Badge variant="outline" className="text-muted-foreground">{normalized}</Badge>;
}
