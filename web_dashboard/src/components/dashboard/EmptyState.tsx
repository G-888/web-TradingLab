import { Card, CardContent } from "@/components/ui/card"
import { AlertCircle } from "lucide-react"

interface EmptyStateProps {
  message?: string;
}

export default function EmptyState({ message = "No data available." }: EmptyStateProps) {
  return (
    <Card className="border-dashed">
      <CardContent className="flex flex-col items-center justify-center py-12 text-center">
        <AlertCircle className="h-8 w-8 text-muted-foreground mb-4 opacity-50" />
        <p className="text-sm font-medium text-muted-foreground">{message}</p>
      </CardContent>
    </Card>
  )
}
