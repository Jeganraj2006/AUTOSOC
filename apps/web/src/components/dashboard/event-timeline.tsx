import React from "react";
import ReactECharts from "echarts-for-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { format, parseISO } from "date-fns";
import { AlertCircle } from "lucide-react";

interface TimelineItem {
  time: string;
  count: number;
}

interface EventTimelineProps {
  timeline: TimelineItem[];
}

export function EventTimeline({ timeline }: EventTimelineProps) {
  const isEmpty = timeline.length === 0;

  const chartOptions = {
    backgroundColor: "transparent",
    tooltip: {
      trigger: "axis",
      backgroundColor: "rgba(9, 9, 11, 0.95)",
      borderColor: "rgba(39, 39, 42, 0.8)",
      borderWidth: 1,
      textStyle: { color: "#e4e4e7", fontFamily: "monospace", fontSize: 11 },
      padding: [8, 12],
    },
    grid: {
      left: "4%",
      right: "4%",
      bottom: "8%",
      top: "10%",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      data: timeline.map((t) => {
        try {
          return format(parseISO(t.time), "HH:mm");
        } catch {
          return t.time;
        }
      }),
      axisLabel: { color: "#71717a", fontSize: 10, fontFamily: "monospace" },
      axisLine: { lineStyle: { color: "#27272a" } },
      axisTick: { lineStyle: { color: "#27272a" } },
    },
    yAxis: {
      type: "value",
      axisLabel: { color: "#71717a", fontSize: 10, fontFamily: "monospace" },
      splitLine: { lineStyle: { color: "rgba(39, 39, 42, 0.4)", type: "dashed" } },
    },
    series: [
      {
        data: timeline.map((t) => t.count),
        type: "line",
        smooth: 0.2,
        symbol: "circle",
        symbolSize: 4,
        showSymbol: false,
        lineStyle: { color: "#6366f1", width: 2 },
        itemStyle: { color: "#6366f1" },
        areaStyle: {
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: "rgba(99, 102, 241, 0.15)" },
              { offset: 1, color: "rgba(99, 102, 241, 0.0)" },
            ],
          },
        },
      },
    ],
  };

  return (
    <Card className="bg-zinc-950 border-zinc-900 shadow-none">
      <CardHeader>
        <CardTitle className="text-sm font-semibold text-zinc-300 font-mono uppercase tracking-wider">
          Log Ingestion Timeline (24h)
        </CardTitle>
        <CardDescription className="text-xs text-zinc-500 font-mono">
          Security event volume aggregated hourly
        </CardDescription>
      </CardHeader>
      <CardContent>
        {isEmpty ? (
          <div className="flex h-[300px] flex-col items-center justify-center rounded-lg border border-dashed border-zinc-800 bg-zinc-950 p-6 text-center">
            <AlertCircle className="h-8 w-8 text-zinc-600 mb-3" />
            <p className="text-xs font-mono text-zinc-500 max-w-sm">
              No security events recorded in the selected period.
            </p>
          </div>
        ) : (
          <div className="h-[300px]">
            <ReactECharts
              option={chartOptions}
              style={{ height: "100%", width: "100%" }}
              theme="dark"
              opts={{ renderer: "svg" }}
            />
          </div>
        )}
      </CardContent>
    </Card>
  );
}
