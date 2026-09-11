import { useCallback, useEffect, useState } from "react"
import { RefreshCw } from "lucide-react"
import { toast, Toaster } from "sonner"

import { RequestLog } from "@/components/request-log"
import { ScenarioList } from "@/components/scenario-list"
import { TokenCard } from "@/components/token-card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { call, onRequest, type LogEntry } from "@/lib/api"

type Tokens = { access: string | null; refresh: string | null }
type TokenResponse = { access_token: string; refresh_token: string }

const INBOX_KEY = "devconsole.inbox"

/** Sinh địa chỉ test.
 *
 * Có hộp thư thật thì dùng plus-addressing (ban+dev_xx@gmail.com) để mail về
 * đúng inbox đó. Không có thì rơi về example.com — tên miền này không có MX
 * nên Gmail trả lại ngay, chỉ hợp khi không cần đọc mail. */
function makeEmail(inbox: string) {
  const tag = `dev_${Date.now().toString(36)}`
  const at = inbox.indexOf("@")
  if (at <= 0) return `${tag}@example.com`
  return `${inbox.slice(0, at)}+${tag}${inbox.slice(at)}`
}

/** status 0 nghĩa là fetch không tới được server, không phải mã HTTP. */
function failureText(status: number) {
  if (status === 0) return "Không gọi được API — kiểm tra uvicorn còn chạy không"
  return `Thất bại (${status})`
}

export default function App() {
  const [base, setBase] = useState("http://localhost:8000")
  const [inbox, setInbox] = useState(() => localStorage.getItem(INBOX_KEY) ?? "")
  const [email, setEmail] = useState(() => makeEmail(localStorage.getItem(INBOX_KEY) ?? ""))
  const [password, setPassword] = useState("TestPassword123!")
  const [verifyToken, setVerifyToken] = useState("")
  const [tokens, setTokens] = useState<Tokens>({ access: null, refresh: null })
  const [log, setLog] = useState<LogEntry[]>([])
  const [online, setOnline] = useState<boolean | null>(null)

  useEffect(() => onRequest((entry) => setLog((prev) => [entry, ...prev].slice(0, 60))), [])

  useEffect(() => {
    localStorage.setItem(INBOX_KEY, inbox)
  }, [inbox])

  const ping = useCallback(async () => {
    const res = await call(base, "GET", "/health", { quiet: true })
    setOnline(res.status === 200)
  }, [base])

  useEffect(() => {
    void ping()
    const id = setInterval(() => void ping(), 10_000)
    return () => clearInterval(id)
  }, [ping])

  const body = { email, password, confirm_password: password, full_name: "Dev Console" }

  const register = async () => {
    const res = await call(base, "POST", "/auth/register", { json: body })
    if (res.status === 201) toast.success("Đã đăng ký, kiểm tra email")
    else toast.error(`Đăng ký: ${failureText(res.status)}`)
  }

  const login = async () => {
    const res = await call<TokenResponse>(base, "POST", "/auth/login", {
      form: { username: email, password },
    })
    if (res.status === 200 && res.data) {
      setTokens({ access: res.data.access_token, refresh: res.data.refresh_token })
      toast.success("Đăng nhập thành công")
    } else {
      toast.error(`Đăng nhập: ${failureText(res.status)}`)
    }
  }

  const refresh = async () => {
    const res = await call<TokenResponse>(base, "POST", "/auth/refresh", {
      json: { refresh_token: tokens.refresh },
    })
    if (res.status === 200 && res.data) {
      setTokens({ access: res.data.access_token, refresh: res.data.refresh_token })
      toast.success("Đã xoay token")
    } else {
      toast.error(`Refresh: ${failureText(res.status)}`)
    }
  }

  const verify = async () => {
    const raw = verifyToken.trim()
    const token = raw.includes("token=") ? raw.split("token=")[1].split("&")[0] : raw
    const res = await call(base, "GET", `/auth/verify-email?token=${encodeURIComponent(token)}`)
    if (res.status === 200) toast.success("Email đã xác thực")
    else toast.error(`Xác thực: ${failureText(res.status)}`)
  }

  const logout = async () => {
    await call(base, "POST", "/auth/logout", {
      json: { refresh_token: tokens.refresh },
      bearer: tokens.access,
    })
    setTokens({ access: null, refresh: null })
  }

  return (
    <div className="bg-muted/30 min-h-screen">
      <Toaster position="top-right" />

      <header className="bg-background/80 sticky top-0 z-10 border-b backdrop-blur">
        <div className="mx-auto flex max-w-[1400px] items-center gap-3 px-6 py-3">
          <h1 className="text-sm font-semibold tracking-tight">AuthProject — Dev Console</h1>
          <Badge variant={online ? "secondary" : online === false ? "destructive" : "outline"}>
            {online === null ? "đang kiểm tra" : online ? "API online" : "API offline"}
          </Badge>
          <Button
            size="sm"
            variant="ghost"
            className="ml-auto"
            onClick={() => window.open(`${base}/docs`)}
          >
            Mở /docs
          </Button>
        </div>
      </header>

      <main className="mx-auto grid max-w-[1400px] gap-4 px-6 py-5 lg:grid-cols-[minmax(320px,380px)_1fr]">
        <div className="flex flex-col gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Phiên làm việc</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="space-y-1.5">
                <Label htmlFor="base">Base URL</Label>
                <Input id="base" value={base} onChange={(e) => setBase(e.target.value)} />
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="inbox">Hộp thư nhận</Label>
                <Input
                  id="inbox"
                  placeholder="ban@gmail.com — để trống thì mail sẽ bị trả lại"
                  value={inbox}
                  onChange={(e) => setInbox(e.target.value)}
                />
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="email">Email test</Label>
                <div className="flex gap-2">
                  <Input id="email" value={email} onChange={(e) => setEmail(e.target.value)} />
                  <Button
                    size="icon"
                    variant="outline"
                    className="shrink-0"
                    onClick={() => setEmail(makeEmail(inbox))}
                  >
                    <RefreshCw />
                    <span className="sr-only">Email mới</span>
                  </Button>
                </div>
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="pw">Mật khẩu</Label>
                <Input id="pw" value={password} onChange={(e) => setPassword(e.target.value)} />
              </div>

              <Separator />

              <div className="grid grid-cols-2 gap-2">
                <Button onClick={() => void register()}>1. Đăng ký</Button>
                <Button variant="outline" onClick={() => void call(base, "POST", "/auth/resend-verification", { json: { email } })}>
                  Gửi lại mail
                </Button>
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="vt">Token xác thực</Label>
                <div className="flex gap-2">
                  <Input
                    id="vt"
                    placeholder="dán link trong email"
                    value={verifyToken}
                    onChange={(e) => setVerifyToken(e.target.value)}
                  />
                  <Button variant="outline" className="shrink-0" onClick={() => void verify()}>
                    2. Verify
                  </Button>
                </div>
              </div>

              <Button className="w-full" onClick={() => void login()}>
                3. Đăng nhập
              </Button>

              <div className="grid grid-cols-2 gap-2">
                <Button variant="outline" onClick={() => void call(base, "GET", "/users/me", { bearer: tokens.access })}>
                  /users/me
                </Button>
                <Button variant="outline" onClick={() => void refresh()}>
                  Refresh
                </Button>
                <Button variant="outline" onClick={() => void logout()}>
                  Logout
                </Button>
                <Button variant="outline" onClick={() => void call(base, "POST", "/auth/logout-all", { bearer: tokens.access })}>
                  Logout all
                </Button>
              </div>

              <Button
                variant="ghost"
                className="w-full"
                onClick={() => void call(base, "POST", "/auth/forgot-password", { json: { email } })}
              >
                Quên mật khẩu
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Token đang giữ</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <TokenCard kind="access" token={tokens.access} />
              <TokenCard kind="refresh" token={tokens.refresh} />
            </CardContent>
          </Card>
        </div>

        <Card className="lg:h-[calc(100vh-7.5rem)]">
          <CardContent className="flex h-full flex-col pt-0">
            <Tabs defaultValue="scenarios" className="flex h-full flex-col">
              <TabsList className="self-start">
                <TabsTrigger value="scenarios">Kịch bản bảo mật</TabsTrigger>
                <TabsTrigger value="log">
                  Nhật ký{log.length > 0 ? ` (${log.length})` : ""}
                </TabsTrigger>
              </TabsList>

              <TabsContent value="scenarios" className="mt-3 min-h-0 flex-1">
                <ScenarioList ctx={{ base, access: tokens.access, refresh: tokens.refresh }} />
              </TabsContent>

              <TabsContent value="log" className="mt-3 min-h-0 flex-1">
                <RequestLog entries={log} />
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}
