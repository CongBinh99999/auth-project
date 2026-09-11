import { useState } from "react"
import { Loader2, Play } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { SCENARIOS, type ScenarioContext, type ScenarioResult } from "@/lib/scenarios"

type State = Record<string, { running?: boolean; result?: ScenarioResult }>

export function ScenarioList({ ctx }: { ctx: ScenarioContext }) {
  const [state, setState] = useState<State>({})
  const [runningAll, setRunningAll] = useState(false)

  const runOne = async (id: string) => {
    const scenario = SCENARIOS.find((s) => s.id === id)
    if (!scenario) return
    setState((prev) => ({ ...prev, [id]: { running: true } }))
    const result = await scenario.run(ctx)
    setState((prev) => ({ ...prev, [id]: { result } }))
    return result
  }

  const runAll = async () => {
    setRunningAll(true)
    setState({})
    for (const scenario of SCENARIOS) {
      await runOne(scenario.id)
    }
    setRunningAll(false)
  }

  const done = Object.values(state).filter((s) => s.result).length
  const passed = Object.values(state).filter((s) => s.result?.ok).length

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-3 pb-3">
        <Button size="sm" onClick={runAll} disabled={runningAll}>
          {runningAll ? <Loader2 className="animate-spin" /> : <Play />}
          Chạy tất cả
        </Button>
        {done > 0 ? (
          <span className="text-muted-foreground text-xs tabular-nums">
            {passed}/{done} đúng
          </span>
        ) : null}
        <span className="text-muted-foreground ml-auto text-right text-[11px] leading-tight">
          Kịch bản cuối tiêu hết hạn mức đăng ký của IP trong 60 phút
        </span>
      </div>

      <ScrollArea className="-mx-1 flex-1">
        <div className="divide-y px-1">
          {SCENARIOS.map((s) => {
            const entry = state[s.id]
            return (
              <div key={s.id} className="py-3">
                <div className="flex items-start gap-3">
                  <div className="min-w-0 flex-1">
                    <p className="text-sm leading-snug font-medium">{s.name}</p>
                    <p className="text-muted-foreground mt-0.5 text-xs">
                      mong đợi <span className="text-foreground/80">{s.expect}</span> · {s.why}
                    </p>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    className="shrink-0"
                    disabled={entry?.running || runningAll}
                    onClick={() => void runOne(s.id)}
                  >
                    {entry?.running ? <Loader2 className="animate-spin" /> : "Chạy"}
                  </Button>
                </div>

                {entry?.result ? (
                  <div className="mt-2 flex items-center gap-2">
                    <Badge variant={entry.result.ok ? "secondary" : "destructive"}>
                      {entry.result.ok ? "ĐÚNG" : "SAI"}
                    </Badge>
                    <span className="text-muted-foreground font-mono text-[11px]">
                      {entry.result.detail}
                    </span>
                  </div>
                ) : null}
              </div>
            )
          })}
        </div>
      </ScrollArea>
    </div>
  )
}
