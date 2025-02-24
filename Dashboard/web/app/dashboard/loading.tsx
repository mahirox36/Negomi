import { Skeleton } from "@/components/ui/skeleton"

export default function DashboardLoading() {
  return (
    <div className="container mx-auto p-8">
      <div className="space-y-6">
        <Skeleton className="h-12 w-[250px] mx-auto" />
        <Skeleton className="h-4 w-[300px] mx-auto" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
          {Array(6).fill(0).map((_, i) => (
            <Skeleton key={i} className="h-[200px] rounded-xl" />
          ))}
        </div>
      </div>
    </div>
  )
}
