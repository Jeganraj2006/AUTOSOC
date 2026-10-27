"use client";

import React, { useEffect, useState } from "react";
import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  dataSourceTypes,
  DataSource,
  useCreateDataSource,
  useUpdateDataSource,
} from "@/hooks/use-data-sources";
import { Loader2 } from "lucide-react";

const formSchema = z.object({
  name: z.string().min(3, "Name must be at least 3 characters").max(255),
  source_type: z.enum(dataSourceTypes),
  environment: z.string().min(2, "Environment must be at least 2 characters").max(50),
  description: z.string().max(1000).optional(),
  enabled: z.boolean(),
  secret_reference: z.string().max(255).optional(),
});

interface DataSourceDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  dataSource?: DataSource | null;
}

export function DataSourceDialog({
  open,
  onOpenChange,
  dataSource,
}: DataSourceDialogProps) {
  const createMutation = useCreateDataSource();
  const updateMutation = useUpdateDataSource();
  const [provisionedKey, setProvisionedKey] = useState<string | null>(null);

  const isEditMode = !!dataSource;

  const {
    register,
    handleSubmit,
    control,
    setValue,
    reset,
    formState: { errors },
  } = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      source_type: "synthetic",
      environment: "production",
      description: "",
      enabled: true,
      secret_reference: "",
    },
  });

  const selectedType = useWatch({ control, name: "source_type" });
  const isEnabled = useWatch({ control, name: "enabled" });

  const handleOpenChange = (nextOpen: boolean) => {
    if (!nextOpen) setProvisionedKey(null);
    onOpenChange(nextOpen);
  };

  // Load default values when in edit mode
  useEffect(() => {
    if (open) {
      if (dataSource) {
        reset({
          name: dataSource.name,
          source_type: dataSource.source_type,
          environment: dataSource.environment,
          description: dataSource.description || "",
          enabled: dataSource.enabled,
          secret_reference: dataSource.secret_reference || "",
        });
      } else {
        reset({
          name: "",
          source_type: "synthetic",
          environment: "production",
          description: "",
          enabled: true,
          secret_reference: "",
        });
      }
    }
  }, [open, dataSource, reset]);

  const onSubmit = (values: z.infer<typeof formSchema>) => {
    if (isEditMode && dataSource) {
      updateMutation.mutate(
        {
          id: dataSource.id,
          updates: {
            name: values.name,
            description: values.description || null,
            enabled: values.enabled,
            environment: values.environment,
            secret_reference: values.secret_reference || null,
          },
        },
        {
          onSuccess: () => {
            onOpenChange(false);
          },
        }
      );
    } else {
      createMutation.mutate(values, {
        onSuccess: (createdSource) => setProvisionedKey(createdSource.api_key),
      });
    }
  };

  const isPending = createMutation.isPending || updateMutation.isPending;

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="bg-zinc-950 border-zinc-900 text-zinc-100 sm:max-w-[450px] font-mono">
        <DialogHeader className="border-b border-zinc-900 pb-3">
          <DialogTitle className="text-sm font-bold uppercase tracking-wider text-zinc-300">
            {isEditMode ? "Edit Data Source" : "Add Data Source"}
          </DialogTitle>
          <DialogDescription className="text-xs text-zinc-500 mt-1">
            {isEditMode
              ? "Update the configuration parameters of this security source."
              : "Register a new telemetry stream to ingest normalized SOC events."}
          </DialogDescription>
        </DialogHeader>

        {provisionedKey ? (
          <section className="rounded-md border border-amber-800/60 bg-amber-950/25 p-3" aria-live="polite">
            <p className="text-xs font-semibold text-amber-200">Store this ingestion API key now</p>
            <p className="mt-1 text-[10px] leading-4 text-amber-100/80">For security, AutoSOC will not show this key again. It is never stored in the browser or returned by source-list APIs.</p>
            <Input readOnly value={provisionedKey} aria-label="New ingestion API key" className="mt-2 font-mono text-[11px]" />
            <Button type="button" variant="outline" className="mt-2 h-8 text-xs" onClick={() => handleOpenChange(false)}>I stored the key</Button>
          </section>
        ) : null}

        {!provisionedKey ? <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 pt-4 text-xs">
          {/* Source Name */}
          <div className="space-y-1.5">
            <Label htmlFor="name" className="text-[10px] text-zinc-500 uppercase font-semibold">
              Source Name
            </Label>
            <Input
              id="name"
              {...register("name")}
              placeholder="e.g. Core Firewall logs"
              className="bg-zinc-950 border-zinc-900 text-xs focus:border-zinc-800"
            />
            {errors.name && (
              <p className="text-[10px] text-red-500 mt-0.5">{errors.name.message}</p>
            )}
          </div>

          {/* Source Type (Disabled in edit mode to preserve OCSF structure) */}
          <div className="space-y-1.5">
            <Label htmlFor="source_type" className="text-[10px] text-zinc-500 uppercase font-semibold">
              Source Type
            </Label>
            <Select
              disabled={isEditMode}
              value={selectedType}
              onValueChange={(val) => setValue("source_type", val as z.infer<typeof formSchema>["source_type"])}
            >
              <SelectTrigger className="bg-zinc-950 border-zinc-900 text-xs capitalize">
                <SelectValue placeholder="Select type" />
              </SelectTrigger>
              <SelectContent className="bg-zinc-950 border-zinc-900 text-xs text-zinc-300">
                <SelectItem value="synthetic">Synthetic</SelectItem>
                <SelectItem value="http_json">HTTP JSON</SelectItem>
                <SelectItem value="linux_syslog">Linux Syslog</SelectItem>
                <SelectItem value="network_flow">Network Flow</SelectItem>
                <SelectItem value="windows_event">Windows Event</SelectItem>
                <SelectItem value="kubernetes_audit">Kubernetes Audit</SelectItem>
                <SelectItem value="aws_cloudtrail">AWS CloudTrail</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Environment */}
          <div className="space-y-1.5">
            <Label htmlFor="environment" className="text-[10px] text-zinc-500 uppercase font-semibold">
              Environment
            </Label>
            <Input
              id="environment"
              {...register("environment")}
              placeholder="e.g. production, staging, development"
              className="bg-zinc-950 border-zinc-900 text-xs focus:border-zinc-800"
            />
            {errors.environment && (
              <p className="text-[10px] text-red-500 mt-0.5">{errors.environment.message}</p>
            )}
          </div>

          {/* Description */}
          <div className="space-y-1.5">
            <Label htmlFor="description" className="text-[10px] text-zinc-500 uppercase font-semibold">
              Description
            </Label>
            <textarea
              id="description"
              {...register("description")}
              placeholder="Optional source metadata details..."
              className="flex min-h-[60px] w-full rounded-md border border-zinc-900 bg-zinc-950 px-3 py-2 text-xs focus:border-zinc-800 focus:outline-none"
            />
          </div>

          {/* Secret Reference */}
          <div className="space-y-1.5">
            <Label htmlFor="secret_reference" className="text-[10px] text-zinc-500 uppercase font-semibold">
              Secret Reference ID
            </Label>
            <Input
              id="secret_reference"
              {...register("secret_reference")}
              placeholder="e.g. vault/firewall-token"
              className="bg-zinc-950 border-zinc-900 text-xs focus:border-zinc-800"
            />
          </div>

          {/* Enabled Switch */}
          <div className="flex items-center justify-between rounded-md border border-zinc-900 bg-zinc-950/20 p-3 mt-2">
            <div className="space-y-0.5">
              <Label className="text-[10px] text-zinc-400 uppercase font-semibold">
                Enabled State
              </Label>
              <p className="text-[9px] text-zinc-500">
                Turn on to permit ingestion of security events.
              </p>
            </div>
            <input
              type="checkbox"
              checked={isEnabled}
              onChange={(e) => setValue("enabled", e.target.checked)}
              className="h-4 w-4 rounded border-zinc-900 bg-zinc-950 text-indigo-650 focus:ring-zinc-800 cursor-pointer"
            />
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-3 border-t border-zinc-900">
            <Button
              type="button"
              variant="ghost"
              onClick={() => handleOpenChange(false)}
              className="h-8 hover:bg-zinc-900 text-zinc-400 hover:text-zinc-200"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isPending}
              className="h-8 bg-indigo-650 hover:bg-indigo-700 text-zinc-150 text-xs font-semibold px-4"
            >
              {isPending ? (
                <>
                  <Loader2 className="mr-2 h-3.5 w-3.5 animate-spin" />
                  Saving...
                </>
              ) : isEditMode ? (
                "Save Changes"
              ) : (
                "Create Source"
              )}
            </Button>
          </div>
        </form> : null}
      </DialogContent>
    </Dialog>
  );
}
