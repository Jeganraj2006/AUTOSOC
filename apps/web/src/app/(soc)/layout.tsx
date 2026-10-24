import { AppShell } from "@/components/layout/shell";

export default function SocLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AppShell>{children}</AppShell>;
}
