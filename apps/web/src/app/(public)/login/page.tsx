import { signIn } from "@/auth";
import { Button } from "@/components/ui/button";
import { ShieldAlert } from "lucide-react";

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-950 p-4">
      <div className="w-full max-w-md space-y-8 rounded-xl border border-zinc-800 bg-zinc-900 p-10 shadow-2xl">
        <div className="flex flex-col items-center justify-center space-y-3 text-center">
          <div className="rounded-full bg-zinc-800 p-3 ring-1 ring-zinc-700">
            <ShieldAlert className="h-8 w-8 text-primary" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-zinc-100">
            AutoSOC
          </h1>
          <p className="text-sm text-zinc-400">
            Autonomous Security Operations Center for Zero-Day Threat Detection
          </p>
          <div className="mt-2 inline-flex items-center rounded-full border border-blue-900 bg-blue-950/50 px-2.5 py-0.5 text-xs font-semibold text-blue-400">
            Development Environment
          </div>
        </div>

        <form
          action={async () => {
            "use server";
            await signIn("keycloak", { redirectTo: "/dashboard" });
          }}
          className="mt-8 space-y-4"
        >
          <Button type="submit" className="w-full py-6 text-base shadow-sm">
            Sign in with AutoSOC Identity
          </Button>
        </form>

        <p className="text-center text-xs text-zinc-500">
          Ethical Use Only. By logging in, you agree to the acceptable use policy.
        </p>
      </div>
    </div>
  );
}
