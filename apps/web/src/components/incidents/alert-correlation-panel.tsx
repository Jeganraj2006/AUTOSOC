"use client"

import { useEffect, useState } from "react"
import { useSession } from "next-auth/react"
import { AlertCircle, Clock, ShieldAlert } from "lucide-react"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { fetchApi } from "@/lib/api"

interface AlertItem {
    id: string
    title: string
    description?: string | null
    severity: string
    status: string
    source_event_id?: string | null
    rule_id?: string | null
    indicators_json?: unknown
    incident_id?: string | null
    created_at: string
    updated_at: string
}

interface AlertCorrelationPanelProps {
    incidentId: string
}

export function AlertCorrelationPanel({
    incidentId,
}: AlertCorrelationPanelProps) {
    const { data: session, status: authStatus } = useSession()
    const [alerts, setAlerts] = useState<AlertItem[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        let cancelled = false

        async function loadAlerts() {
            if (authStatus !== "authenticated" || !session?.accessToken) {
                return
            }

            try {
                setLoading(true)
                setError(null)

                const data = await fetchApi<AlertItem[]>("/alerts/", {
                    headers: {
                        Authorization: `Bearer ${session.accessToken}`,
                    },
                })

                if (!cancelled) {
                    const incidentAlerts = data.filter(
                        (alert) => alert.incident_id === incidentId
                    )

                    setAlerts(incidentAlerts)
                }
            } catch (err) {
                console.error("Failed to load alerts:", err)

                if (!cancelled) {
                    setError("Unable to load correlated alerts.")
                }
            } finally {
                if (!cancelled) {
                    setLoading(false)
                }
            }
        }

        loadAlerts()

        return () => {
            cancelled = true
        }
    }, [incidentId, session, authStatus])

    if (loading) {
        return (
            <div className="space-y-3">
                <Skeleton className="h-20 w-full" />
                <Skeleton className="h-20 w-full" />
            </div>
        )
    }

    if (error) {
        return (
            <div className="rounded-lg border border-destructive/50 p-4">
                <div className="flex items-center gap-2">
                    <AlertCircle className="h-5 w-5 text-destructive" />
                    <p className="text-sm text-destructive">{error}</p>
                </div>
            </div>
        )
    }

    if (alerts.length === 0) {
        return (
            <div className="rounded-lg border p-6 text-center">
                <ShieldAlert className="mx-auto mb-3 h-8 w-8 text-muted-foreground" />
                <p className="font-medium">No correlated alerts</p>
                <p className="mt-1 text-sm text-muted-foreground">
                    No alerts are currently associated with this incident.
                </p>
            </div>
        )
    }

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <p className="text-sm text-muted-foreground">
                    {alerts.length} alert{alerts.length !== 1 ? "s" : ""} correlated
                    with this incident.
                </p>
            </div>

            <div className="space-y-3">
                {alerts.map((alert) => (
                    <Card key={alert.id}>
                        <CardHeader className="pb-3">
                            <div className="flex items-start justify-between gap-4">
                                <div>
                                    <CardTitle className="text-base">
                                        {alert.title}
                                    </CardTitle>

                                    {alert.description && (
                                        <p className="mt-1 text-sm text-muted-foreground">
                                            {alert.description}
                                        </p>
                                    )}
                                </div>

                                <Badge
                                    variant={
                                        alert.severity.toLowerCase() === "critical" ||
                                        alert.severity.toLowerCase() === "high"
                                            ? "destructive"
                                            : "secondary"
                                    }
                                >
                                    {alert.severity}
                                </Badge>
                            </div>
                        </CardHeader>

                        <CardContent>
                            <div className="grid gap-3 text-sm md:grid-cols-3">
                                <div>
                                    <p className="text-muted-foreground">Status</p>
                                    <p className="font-medium">{alert.status}</p>
                                </div>

                                <div>
                                    <p className="text-muted-foreground">Source Event</p>
                                    <p className="font-medium">
                                        {alert.source_event_id || "N/A"}
                                    </p>
                                </div>

                                <div>
                                    <p className="text-muted-foreground">Detected</p>
                                    <div className="flex items-center gap-1 font-medium">
                                        <Clock className="h-3.5 w-3.5" />
                                        {new Date(alert.created_at).toLocaleString()}
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    )
}
