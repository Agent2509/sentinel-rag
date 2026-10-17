"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import type { Strategy } from "@/lib/types";

export const STRATEGIES: Strategy[] = ["fixed", "hierarchical", "semantic"];

export function StrategySelector({
  strategy,
  onStrategy,
  correction,
  onCorrection,
  disabled,
}: {
  strategy: Strategy;
  onStrategy: (s: Strategy) => void;
  correction: boolean;
  onCorrection: (c: boolean) => void;
  disabled?: boolean;
}) {
  return (
    <div className="flex flex-wrap items-center gap-4">
      <div className="flex items-center gap-2">
        <Label htmlFor="strategy" className="text-xs text-muted-foreground">
          Chunking
        </Label>
        <Select
          value={strategy}
          onValueChange={(v) => onStrategy(v as Strategy)}
          disabled={disabled}
        >
          <SelectTrigger id="strategy" className="h-8 w-[150px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {STRATEGIES.map((s) => (
              <SelectItem key={s} value={s}>
                {s}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="flex items-center gap-2">
        <Switch
          id="correction"
          checked={correction}
          onCheckedChange={onCorrection}
          disabled={disabled}
        />
        <Label htmlFor="correction" className="text-xs text-muted-foreground">
          Self-correction (HyDE)
        </Label>
      </div>
    </div>
  );
}
