import { useEffect, useState } from "react"
import { Check, Copy } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { decodeJwt } from "@/lib/api"

/** Nhịp đồng hồ mỗi giây; giá trị hiển thị được tính lúc render. */
function useNow(active: boolean) {
  const [now, setNow] = useState(() => Date.now())

  useEffect(() => {
    if (!active) return
    const id = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(id)
  }, [active])

  return now
}

function formatLeft(seconds: number) {
  if (seconds <= 0) return "đã hết hạn"
  if (seconds < 120) return `còn ${seconds}s`
  if (seconds < 7200) return `còn ${Math.floor(seconds / 60)} phút`
  return `còn ${Math.floor(seconds / 3600)} giờ`
}

export function TokenCard({ kind, token }: { kind: "access" | "refresh"; token: string | null }) {
  const claims = decodeJwt(token)
  const now = useNow(Boolean(claims?.exp))
  const left = claims?.exp ? Math.round(claims.exp - now / 1000) : null
  const [copied, setCopied] = useState(false)

  if (!token || !claims) {
    return (
      <div className="rounded-lg border border-dashed p-3">
        <p className="text-muted-foreground text-xs">Chưa có {kind} token</p>
      </div>
    )
  }

  const expired = left !== null && left <= 0
  const mismatch = claims.type !== kind

  const copy = () => {
    void navigator.clipboard.writeText(token)
    setCopied(true)
    setTimeout(() => setCopied(false), 1200)
  }

  return (
    <div className="rounded-lg border p-3">
      <div className="flex items-center gap-2">
        <Badge variant={expired || mismatch ? "destructive" : "secondary"} className="font-mono">
          {claims.type ?? kind}
        </Badge>
        <span className="text-muted-foreground text-xs tabular-nums">
          {left === null ? "" : formatLeft(left)}
        </span>
        <Button size="icon" variant="ghost" className="ml-auto size-7" onClick={copy}>
          {copied ? <Check className="size-3.5" /> : <Copy className="size-3.5" />}
          <span className="sr-only">Chép token</span>
        </Button>
      </div>

      <dl className="mt-2 grid grid-cols-[4rem_1fr] gap-x-3 gap-y-0.5 font-mono text-[11px]">
        <dt className="text-muted-foreground">jti</dt>
        <dd className="truncate">{claims.jti ?? "—"}</dd>
        <dt className="text-muted-foreground">family</dt>
        <dd className="truncate">{claims.family_id ?? "—"}</dd>
        <dt className="text-muted-foreground">sub</dt>
        <dd className="truncate">{claims.sub ?? "—"}</dd>
      </dl>
    </div>
  )
}
