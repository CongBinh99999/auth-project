import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import type { LogEntry } from "@/lib/api"

function tone(status: number) {
  if (status === 0) return "destructive" as const
  if (status < 300) return "secondary" as const
  if (status < 500) return "outline" as const
  return "destructive" as const
}

export function RequestLog({ entries }: { entries: LogEntry[] }) {
  if (entries.length === 0) {
    return (
      <div className="text-muted-foreground flex h-full items-center justify-center text-sm">
        Chưa có request nào.
      </div>
    )
  }

  return (
    <ScrollArea className="h-full">
      <div className="divide-y">
        {entries.map((e) => (
          <div key={e.id} className="px-1 py-2.5">
            <div className="flex items-baseline gap-2">
              <Badge variant={tone(e.status)} className="font-mono tabular-nums">
                {e.status || "ERR"}
              </Badge>
              <code className="truncate text-xs">
                {e.method} {e.path}
              </code>
              <span className="text-muted-foreground ml-auto shrink-0 font-mono text-[11px] tabular-nums">
                {e.ms} ms
              </span>
            </div>
            {e.body ? (
              <pre className="bg-muted/50 mt-1.5 max-h-28 overflow-auto rounded-md p-2 text-[11px] leading-relaxed whitespace-pre-wrap">
                {e.body.slice(0, 800)}
              </pre>
            ) : null}
          </div>
        ))}
      </div>
    </ScrollArea>
  )
}
