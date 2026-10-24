"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useMe } from "@/hooks/use-me";
import { useSystemHealth } from "@/hooks/use-system-health";
import { signOut } from "next-auth/react";
import {
  LayoutDashboard,
  ListOrdered,
  Bell,
  ShieldAlert,
  BrainCircuit,
  Shield,
  Database,
  Cpu,
  Braces,
  Activity,
  ShieldCheck,
  User,
  LogOut,
  Menu,
  X,
  Settings,
  Sun,
  Moon,
} from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuGroup,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const routes = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/events", label: "Log Explorer", icon: ListOrdered },
  { href: "/alerts", label: "Alerts", icon: Bell },
  { href: "/incidents", label: "Incidents", icon: ShieldAlert },
  { href: "/predictions", label: "Predictions", icon: BrainCircuit },
  { href: "/detection", label: "Detection", icon: Shield },
  { href: "/data-sources", label: "Data Sources", icon: Database },
  { href: "/agents", label: "Agents", icon: Cpu },
  { href: "/rules", label: "Rules", icon: Braces },
  { href: "/system-health", label: "System Health", icon: Activity },
];

const adminRoutes = [
  { href: "/audit", label: "Audit Activity", icon: ShieldCheck },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { data: user, isLoading: isUserLoading } = useMe();
  const { isSuccess: isHealthSuccess, isError: isHealthError } = useSystemHealth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [theme, setTheme] = useState<"light" | "dark">("dark");

  useEffect(() => {
    const savedTheme = localStorage.getItem("autosoc_theme") as "light" | "dark" | null;
    if (savedTheme) {
      setTheme(savedTheme);
      if (savedTheme === "dark") {
        document.documentElement.classList.add("dark");
      } else {
        document.documentElement.classList.remove("dark");
      }
    } else {
      document.documentElement.classList.add("dark");
    }
  }, []);

  const toggleTheme = () => {
    const nextTheme = theme === "light" ? "dark" : "light";
    setTheme(nextTheme);
    localStorage.setItem("autosoc_theme", nextTheme);
    if (nextTheme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  };

  const isSuperuser = user?.is_superuser || false;
  const navRoutes = isSuperuser ? [...routes, ...adminRoutes] : routes;

  // Determine current page title
  const currentRoute = navRoutes.find((r) => pathname.startsWith(r.href));
  const pageTitle = currentRoute ? currentRoute.label : "AutoSOC Page";

  return (
    <div className="flex min-h-screen bg-slate-100 dark:bg-zinc-950 font-sans text-slate-900 dark:text-zinc-100 transition-colors duration-200">
      {/* Desktop Sidebar */}
      <aside className="hidden w-64 shrink-0 flex-col border-r border-slate-200 dark:border-zinc-900 bg-white dark:bg-zinc-950 md:flex shadow-sm">
        {/* Title logo block */}
        <div className="flex flex-col justify-center h-20 border-b border-slate-200 dark:border-zinc-900 px-6 bg-slate-50/50 dark:bg-zinc-950">
          <div className="flex items-center gap-2.5">
            <Shield className="h-6 w-6 text-indigo-600 dark:text-indigo-500" />
            <span className="font-sans text-xl font-extrabold tracking-tight text-slate-900 dark:text-zinc-100">
              AutoSOC
            </span>
          </div>
          <span className="text-[11px] text-slate-500 dark:text-zinc-400 font-medium tracking-tight mt-0.5">
            Autonomous Security Operations Center
          </span>
        </div>

        {/* Sidebar Nav */}
        <nav className="flex-1 space-y-1 p-4 overflow-y-auto">
          {navRoutes.map((route, index) => {
            const isActive = pathname.startsWith(route.href);
            return (
              <React.Fragment key={route.href}>
              {(index === 0 || index === 4 || index === 8 || index === 10) && (
                <div className="px-3 pt-4 pb-1 text-[10px] font-bold uppercase tracking-widest text-slate-400 dark:text-zinc-500">
                  {index === 0 ? "Monitoring" : index === 4 ? "Threat Intelligence" : index === 8 ? "Platform" : "Administration"}
                </div>
              )}
              <Link
                key={route.href}
                href={route.href}
                className={`flex items-center gap-3.5 rounded-lg px-3.5 py-2.5 text-sm font-semibold transition-all ${
                  isActive
                    ? "bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-400 border-l-4 border-indigo-600 dark:border-indigo-500 pl-3 shadow-xs"
                    : "text-slate-600 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-zinc-900 hover:text-slate-900 dark:hover:text-zinc-200"
                }`}
              >
                <route.icon className="h-5 w-5 shrink-0" />
                {route.label}
              </Link>
              </React.Fragment>
            );
          })}
        </nav>

        {/* Sidebar User Profile Section */}
        <div className="border-t border-slate-200 dark:border-zinc-900 p-4 bg-slate-50 dark:bg-zinc-950/60">
          {isUserLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-4 w-24 bg-slate-200 dark:bg-zinc-900" />
              <Skeleton className="h-3 w-32 bg-slate-200 dark:bg-zinc-900" />
            </div>
          ) : (
            <div className="flex items-center justify-between gap-2 text-xs">
              <div className="min-w-0 flex-1">
                <p className="font-semibold truncate text-slate-900 dark:text-zinc-200">{user?.username}</p>
                <p className="text-[11px] truncate text-slate-500 dark:text-zinc-400">{user?.email}</p>
              </div>
              <DropdownMenu>
                <DropdownMenuTrigger className="rounded-md p-1.5 hover:bg-slate-200 dark:hover:bg-zinc-900 text-slate-500 hover:text-slate-800 dark:text-zinc-400 dark:hover:text-zinc-200 cursor-pointer outline-hidden">
                  <Settings className="h-4 w-4" />
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48 bg-white dark:bg-zinc-950 border-slate-200 dark:border-zinc-900 text-xs shadow-lg">
                  <Link href="/profile">
                    <DropdownMenuItem className="cursor-pointer focus:bg-slate-100 dark:focus:bg-zinc-900 text-slate-700 dark:text-zinc-200">
                      <User className="mr-2 h-4 w-4" />
                      <span>Profile</span>
                    </DropdownMenuItem>
                  </Link>
                  <DropdownMenuSeparator className="bg-slate-200 dark:bg-zinc-900" />
                  <DropdownMenuItem
                    onClick={async () => {
                      await signOut({ callbackUrl: "/login" });
                    }}
                    className="text-red-600 dark:text-red-400 cursor-pointer focus:bg-red-50 dark:focus:bg-red-950/30"
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>Log out</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          )}
        </div>
      </aside>

      {/* Main Container */}
      <div className="flex flex-1 flex-col min-w-0">
        {/* Header */}
        <header className="flex h-16 items-center justify-between border-b border-slate-200 dark:border-zinc-900 bg-white/90 dark:bg-zinc-950/60 px-6 backdrop-blur-md sticky top-0 z-30 shadow-xs">
          <div className="flex items-center gap-4">
            {/* Mobile Menu Trigger */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="rounded p-1.5 text-slate-600 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-zinc-900 md:hidden"
            >
              {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>

            {/* Current Section Title */}
            <h1 className="hidden md:block text-base font-bold tracking-tight text-slate-800 dark:text-zinc-200 uppercase">
              {pageTitle}
            </h1>

            <div className="flex items-center md:hidden">
              <Shield className="h-6 w-6 text-indigo-600 dark:text-indigo-500 mr-2" />
              <span className="font-extrabold text-base tracking-tight text-slate-900 dark:text-zinc-100">AutoSOC</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Theme Toggle Button */}
            <button
              onClick={toggleTheme}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-300 dark:border-zinc-800 bg-slate-50 dark:bg-zinc-900 hover:bg-slate-100 dark:hover:bg-zinc-800 text-slate-800 dark:text-zinc-200 text-xs font-bold shadow-2xs transition-colors cursor-pointer"
              title="Switch between Light and Dark themes"
            >
              {theme === "light" ? (
                <>
                  <Sun className="h-4 w-4 text-amber-500 shrink-0" />
                  <span>Light Theme</span>
                </>
              ) : (
                <>
                  <Moon className="h-4 w-4 text-indigo-400 shrink-0" />
                  <span>Dark Theme</span>
                </>
              )}
            </button>

            {/* Real System Connection Status Indicator */}
            <div className="flex items-center gap-1.5 border border-slate-200 dark:border-zinc-900 bg-slate-50 dark:bg-zinc-950 px-2.5 py-1 rounded-md text-xs font-medium">
              <span
                className={`h-2 w-2 rounded-full ${
                  isHealthSuccess
                    ? "bg-emerald-500"
                    : isHealthError
                    ? "bg-red-500"
                    : "bg-slate-400 animate-pulse"
                }`}
              />
              <span className="text-slate-500 dark:text-zinc-500">API Status:</span>
              <span
                className={`font-semibold ${
                  isHealthSuccess
                    ? "text-emerald-600 dark:text-emerald-500"
                    : isHealthError
                    ? "text-red-600 dark:text-red-500"
                    : "text-slate-500"
                }`}
              >
                {isHealthSuccess ? "ONLINE" : isHealthError ? "OFFLINE" : "CHECKING"}
              </span>
            </div>

            {/* Environment Indicator */}
            <div className="hidden sm:inline-flex items-center border border-slate-200 dark:border-zinc-900 bg-slate-50 dark:bg-zinc-950 px-2.5 py-1 rounded-md text-xs font-bold text-slate-600 dark:text-zinc-400 uppercase tracking-wider">
              {process.env.NODE_ENV === "production" ? "PRODUCTION" : "DEVELOPMENT"}
            </div>

            {/* User Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-300 dark:border-zinc-800 bg-slate-50 dark:bg-zinc-950 hover:bg-slate-100 dark:hover:bg-zinc-900 transition-colors cursor-pointer outline-hidden shadow-2xs">
                <User className="h-4 w-4 text-slate-600 dark:text-zinc-400" />
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-52 bg-white dark:bg-zinc-950 border-slate-200 dark:border-zinc-900 text-xs shadow-lg">
                <DropdownMenuGroup>
                  <DropdownMenuLabel className="font-normal px-3 py-2">
                    <p className="truncate font-bold text-slate-800 dark:text-zinc-200">{user?.username}</p>
                    <p className="truncate text-[11px] text-slate-500 dark:text-zinc-400 mt-0.5">{user?.email}</p>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator className="bg-slate-200 dark:bg-zinc-900" />
                  <Link href="/profile">
                    <DropdownMenuItem className="cursor-pointer focus:bg-slate-100 dark:focus:bg-zinc-900 text-slate-700 dark:text-zinc-200">
                      <User className="mr-2 h-4 w-4" />
                      <span>Profile</span>
                    </DropdownMenuItem>
                  </Link>
                  <DropdownMenuItem
                    onClick={async () => {
                      await signOut({ callbackUrl: "/login" });
                    }}
                    className="text-red-600 dark:text-red-400 cursor-pointer focus:bg-red-50 dark:focus:bg-red-950/30"
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>Log out</span>
                  </DropdownMenuItem>
                </DropdownMenuGroup>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        {/* Mobile Navigation Drawer */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-b border-slate-200 dark:border-zinc-900 bg-white dark:bg-zinc-950 px-4 py-3 space-y-1">
            {navRoutes.map((route) => {
              const isActive = pathname.startsWith(route.href);
              return (
                <Link
                  key={route.href}
                  href={route.href}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={`flex items-center gap-3.5 rounded-lg px-3.5 py-2.5 text-sm font-semibold transition-colors ${
                    isActive
                      ? "bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-400 border-l-4 border-indigo-600 dark:border-indigo-500 pl-3"
                      : "text-slate-600 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-zinc-900 hover:text-slate-900 dark:hover:text-zinc-200"
                  }`}
                >
                  <route.icon className="h-5 w-5 shrink-0" />
                  {route.label}
                </Link>
              );
            })}
          </div>
        )}

        {/* Page Content Container */}
        <main className="flex-1 p-6 overflow-y-auto">
          <div className="mx-auto max-w-7xl animate-fade-in">{children}</div>
        </main>
      </div>
    </div>
  );
}
