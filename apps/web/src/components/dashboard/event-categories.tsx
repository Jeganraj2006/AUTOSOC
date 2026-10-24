import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Info } from "lucide-react";

interface CategoryItem {
  category: string;
  count: number;
}

interface EventCategoriesProps {
  categories: CategoryItem[];
}

export function EventCategories({ categories }: EventCategoriesProps) {
  const isEmpty = categories.length === 0;

  // Find max count to calculate relative percentages
  const maxCount = categories.reduce((max, item) => (item.count > max ? item.count : max), 0);

  return (
    <Card className="bg-zinc-950 border-zinc-900 shadow-none">
      <CardHeader>
        <CardTitle className="text-sm font-semibold text-zinc-300 font-mono uppercase tracking-wider">
          Normalized Category Distribution
        </CardTitle>
        <CardDescription className="text-xs text-zinc-500 font-mono">
          Security event classification profile
        </CardDescription>
      </CardHeader>
      <CardContent>
        {isEmpty ? (
          <div className="flex h-[300px] flex-col items-center justify-center rounded-lg border border-dashed border-zinc-800 bg-zinc-950 p-6 text-center">
            <Info className="h-8 w-8 text-zinc-600 mb-3" />
            <p className="text-xs font-mono text-zinc-500 max-w-sm">
              No event categories available.
            </p>
          </div>
        ) : (
          <div className="space-y-4 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
            {categories.map((item, index) => {
              const percentage = maxCount > 0 ? (item.count / maxCount) * 100 : 0;
              return (
                <div key={index} className="space-y-1.5">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-mono text-zinc-300 font-medium">
                      {item.category || "UNKNOWN"}
                    </span>
                    <span className="font-mono text-zinc-500 text-[11px]">
                      {item.count.toLocaleString()} events
                    </span>
                  </div>
                  <Progress
                    value={percentage}
                    className={`h-1.5 bg-zinc-900 ${
                      index === 0 ? "[&>div]:bg-indigo-500" : "[&>div]:bg-indigo-600/50"
                    }`}
                  />
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
