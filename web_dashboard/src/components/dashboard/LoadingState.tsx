import { Skeleton } from "@/components/ui/skeleton"

export default function LoadingState() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-8 w-1/4" />
      <Skeleton className="h-32 w-full" />
      <Skeleton className="h-32 w-full" />
    </div>
  )
}
