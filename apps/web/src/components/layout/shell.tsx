"use client";

import { type ReactNode, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { signOut } from "next-auth/react";
import {
  Activity,
  Bell,
  BrainCircuit,
  Braces,
  CircleDot,
  Cpu,
  Database,
  LayoutDashboard,
  ListOrdered,
  LogOut,
  Menu,
  Moon,
  PanelLeftClose,
  PanelLeftOpen,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Sun,
  User,
  X,
} from "lucide-react";
import { useMe } from "@/hooks/use-me";
import { useSystemHealth } from "@/hooks/use-system-health";
import { Skeleton } from "@/components/ui/skeleton";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

type RouteItem = {
  href: string;
  label: string;
  icon: typeof LayoutDashboard;
  adminOnly?: boolean;
};

const navigationGroups: Array<{ label: string; routes: RouteItem[] }> = [
  {
    label: "Monitoring",
    routes: [
      { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
      { href: "/events", label: "Log Explorer", icon: ListOrdered },
      { href: "/alerts", label: "Alerts", icon: Bell },
      { href: "/incidents", label: "Incidents", icon: ShieldAlert },
    ],
  },
  {
    label: "Intelligence",
    routes: [
      { href: "/detection", label: "Detection", icon: Shield },
      { href: "/predictions", label: "Predictions", icon: BrainCircuit },
      { href: "/agents", label: "AI Investigations", icon: Cpu },
      { href: "/responses", label: "Responses", icon: ShieldCheck },
    ],
  },
  {
    label: "Administration",
    routes: [
      { href: "/data-sources", label: "Data Sources", icon: Database },
      { href: "/rules", label: "Detection Rules", icon: Braces },
      { href: "/system-health", label: "System Health", icon: Activity },
      { href: "/audit", label: "Audit Activity", icon: ShieldCheck, adminOnly: true },
    ],
  },
];

function isActiveRoute(pathname: string, href: string) {
  return pathname === href || pathname.startsWith(`${href}/`);
}

function Brand({ compact = false }: { compact?: boolean }) {
  return (
    <Link href="/dashboard" className="flex items-center gap-3 rounded-lg focus-visible:outline-none">
      <span className="grid size-9 shrink-0 place-items-center rounded-xl bg-primary text-primary-foreground shadow-sm">
        <Shield className="size-5" aria-hidden="true" />
      </span>
      {!compact ? (
        <span className="min-w-0">
          <span className="block text-base font-semibold tracking-[-0.03em] text-[var(--sidebar-foreground)]">AutoSOC</span>
          <span className="block truncate text-[10px] font-medium uppercase tracking-[0.12em] text-[var(--sidebar-muted)]">Security operations</span>
        </span>
      ) : null}
    </Link>
  );
}

function Navigation({
  collapsed,
  pathname,
  isAdmin,
  onNavigate,
}: {
  collapsed?: boolean;
  pathname: string;
  isAdmin: boolean;
  onNavigate?: () => void;
}) {
  return (
    <nav className="space-y-5" aria-label="Primary navigation">
      {navigationGroups.map((group) => {
        const routes = group.routes.filter((route) => !route.adminOnly || isAdmin);
        if (routes.length === 0) return null;
        return (
          <section key={group.label} aria-label={group.label} className="space-y-1.5">
            <h2 className={collapsed ? "sr-only" : "px-2 text-[10px] font-semibold uppercase tracking-[0.14em] text-[var(--sidebar-muted)]"}>
              {group.label}
            </h2>
            {routes.map((route) => {
              const active = isActiveRoute(pathname, route.href);
              const Icon = route.icon;
              return (
                <Link
                  key={route.href}
                  href={route.href}
                  onClick={onNavigate}
                  aria-current={active ? "page" : undefined}
                  title={collapsed ? route.label : undefined}
                  className={`group flex min-h-10 items-center gap-3 rounded-lg px-3 text-sm font-medium transition-colors focus-visible:outline-none ${
                    active
                      ? "bg-[var(--sidebar-active)] text-white"
                      : "text-[var(--sidebar-foreground)] hover:bg-white/7 hover:text-white"
                  } ${collapsed ? "justify-center px-2" : ""}`}
                >
                  <Icon className="size-4 shrink-0 text-primary group-hover:text-primary" aria-hidden="true" />
                  {!collapsed ? <span>{route.label}</span> : <span className="sr-only">{route.label}</span>}
                </Link>
              );
            })}
          </section>
        );
      })}
    </nav>
  );
}

function UserMenu({ username, email }: { username?: string; email?: string }) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        aria-label="Open account menu"
        className="grid size-9 place-items-center rounded-lg border border-border bg-card text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:outline-none"
      >
        <User className="size-4" aria-hidden="true" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56 border-border bg-popover text-popover-foreground shadow-xl">
        <DropdownMenuGroup>
          <DropdownMenuLabel className="px-3 py-2.5 font-normal">
            <p className="truncate text-sm font-semibold text-foreground">{username ?? "Authenticated user"}</p>
            <p className="mt-0.5 truncate text-xs text-muted-foreground">{email ?? "Session loading"}</p>
          </DropdownMenuLabel>
          <DropdownMenuSeparator className="bg-border" />
          <Link href="/profile">
            <DropdownMenuItem className="cursor-pointer gap-2 text-foreground focus:bg-muted">
              <User className="size-4" aria-hidden="true" />
              Profile
            </DropdownMenuItem>
          </Link>
          <DropdownMenuItem
            onClick={() => void signOut({ callbackUrl: "/login" })}
            className="cursor-pointer gap-2 text-destructive focus:bg-destructive/10 focus:text-destructive"
          >
            <LogOut className="size-4" aria-hidden="true" />
            Sign out
          </DropdownMenuItem>
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const { data: user, isLoading: isUserLoading } = useMe();
  const { isSuccess: isHealthSuccess, isError: isHealthError } = useSystemHealth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [theme, setTheme] = useState<"light" | "dark">(() => {
    if (typeof window === "undefined") return "dark";
    return window.localStorage.getItem("autosoc_theme") === "light" ? "light" : "dark";
  });

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    window.localStorage.setItem("autosoc_theme", theme);
  }, [theme]);

  useEffect(() => {
    if (!isMobileMenuOpen) return;
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setIsMobileMenuOpen(false);
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [isMobileMenuOpen]);

  const isAdmin = Boolean(user?.is_superuser || user?.roles.includes("administrator"));
  const pageTitle = useMemo(() => {
    for (const group of navigationGroups) {
      const matched = group.routes.find((route) => isActiveRoute(pathname, route.href));
      if (matched) return matched.label;
    }
    return "AutoSOC";
  }, [pathname]);
  const healthLabel = isHealthSuccess ? "Connected" : isHealthError ? "Unavailable" : "Checking";

  return (
    <div className="soc-canvas min-h-screen text-foreground">
      <aside
        className={`fixed inset-y-0 left-0 z-40 hidden border-r border-white/8 bg-[var(--sidebar)] transition-[width] duration-200 md:flex md:flex-col ${
          isCollapsed ? "w-20" : "w-72"
        }`}
      >
        <div className="flex h-20 items-center justify-between border-b border-white/8 px-4">
          <Brand compact={isCollapsed} />
          <button
            type="button"
            onClick={() => setIsCollapsed((collapsed) => !collapsed)}
            aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            className="grid size-8 place-items-center rounded-md text-[var(--sidebar-muted)] transition-colors hover:bg-white/7 hover:text-white focus-visible:outline-none"
          >
            {isCollapsed ? <PanelLeftOpen className="size-4" aria-hidden="true" /> : <PanelLeftClose className="size-4" aria-hidden="true" />}
          </button>
        </div>
        <div className="flex-1 overflow-y-auto px-3 py-5">
          <Navigation collapsed={isCollapsed} pathname={pathname} isAdmin={isAdmin} />
        </div>
        <div className="border-t border-white/8 p-3">
          {isUserLoading ? (
            <div className="space-y-2 px-2">
              <Skeleton className="h-3 w-20 bg-white/10" />
              <Skeleton className="h-3 w-28 bg-white/10" />
            </div>
          ) : isCollapsed ? (
            <div className="flex justify-center"><UserMenu username={user?.username} email={user?.email} /></div>
          ) : (
            <div className="flex items-center gap-2 rounded-lg px-2 py-1.5 hover:bg-white/5">
              <span className="grid size-8 shrink-0 place-items-center rounded-full bg-white/8 text-primary"><User className="size-4" aria-hidden="true" /></span>
              <div className="min-w-0 flex-1">
                <p className="truncate text-xs font-semibold text-[var(--sidebar-foreground)]">{user?.username}</p>
                <p className="truncate text-[11px] text-[var(--sidebar-muted)]">{user?.roles.join(", ") || "Authenticated"}</p>
              </div>
              <UserMenu username={user?.username} email={user?.email} />
            </div>
          )}
        </div>
      </aside>

      <div className={`min-h-screen transition-[padding] duration-200 ${isCollapsed ? "md:pl-20" : "md:pl-72"}`}>
        <header className="sticky top-0 z-30 flex min-h-16 items-center justify-between gap-3 border-b border-border bg-background/94 px-4 backdrop-blur-sm sm:px-6">
          <div className="flex min-w-0 items-center gap-3">
            <button
              type="button"
              onClick={() => setIsMobileMenuOpen(true)}
              aria-label="Open navigation menu"
              className="grid size-9 place-items-center rounded-lg border border-border bg-card text-foreground md:hidden"
            >
              <Menu className="size-4" aria-hidden="true" />
            </button>
            <div className="min-w-0">
              <p className="hidden text-xs font-medium text-muted-foreground sm:block">Security operations</p>
              <p className="truncate text-sm font-semibold tracking-[-0.015em] text-foreground sm:text-base">{pageTitle}</p>
            </div>
          </div>

          <div className="flex shrink-0 items-center gap-2">
            <div className="hidden items-center gap-2 rounded-lg border border-border bg-card px-2.5 py-1.5 text-xs sm:flex" aria-live="polite">
              <CircleDot className={`size-3 ${isHealthSuccess ? "text-emerald-500" : isHealthError ? "text-destructive" : "text-amber-500"}`} aria-hidden="true" />
              <span className="text-muted-foreground">API</span>
              <span className="font-semibold text-foreground">{healthLabel}</span>
            </div>
            <button
              type="button"
              onClick={() => setTheme((value) => (value === "dark" ? "light" : "dark"))}
              aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
              className="grid size-9 place-items-center rounded-lg border border-border bg-card text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:outline-none"
            >
              {theme === "dark" ? <Sun className="size-4" aria-hidden="true" /> : <Moon className="size-4" aria-hidden="true" />}
            </button>
            <UserMenu username={user?.username} email={user?.email} />
          </div>
        </header>

        {isMobileMenuOpen ? (
          <div className="fixed inset-0 z-50 md:hidden" role="dialog" aria-modal="true" aria-label="Navigation menu">
            <button type="button" aria-label="Close navigation menu" className="absolute inset-0 bg-slate-950/55" onClick={() => setIsMobileMenuOpen(false)} />
            <div className="relative flex h-full w-[min(20rem,calc(100%-2rem))] flex-col bg-[var(--sidebar)] shadow-2xl">
              <div className="flex h-20 items-center justify-between border-b border-white/8 px-4">
                <Brand />
                <button type="button" aria-label="Close navigation menu" onClick={() => setIsMobileMenuOpen(false)} className="grid size-9 place-items-center rounded-lg text-[var(--sidebar-muted)] hover:bg-white/7 hover:text-white">
                  <X className="size-5" aria-hidden="true" />
                </button>
              </div>
              <div className="flex-1 overflow-y-auto px-3 py-5">
                <Navigation pathname={pathname} isAdmin={isAdmin} onNavigate={() => setIsMobileMenuOpen(false)} />
              </div>
            </div>
          </div>
        ) : null}

        <main className="min-w-0 px-4 py-6 sm:px-6 lg:px-8">
          <div className="mx-auto w-full max-w-[1600px]">{children}</div>
        </main>
      </div>
    </div>
  );
}
