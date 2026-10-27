import { signIn } from "@/auth";
import { Button } from "@/components/ui/button";
import { ArrowRight, CheckCircle2, LockKeyhole, ShieldCheck } from "lucide-react";

type LoginPageProps = {
  searchParams: Promise<{ error?: string; callbackUrl?: string }>;
};

function getErrorMessage(error?: string) {
  if (!error) return null;
  if (error === "Configuration") {
    return "The identity connection is unavailable. Check the server configuration or try again shortly.";
  }
  if (error === "AccessDenied") {
    return "Your identity provider did not grant access to AutoSOC.";
  }
  return "Your sign-in session could not be completed. Start a new secure sign-in attempt.";
}

export default async function LoginPage({ searchParams }: LoginPageProps) {
  const { error, callbackUrl } = await searchParams;
  const errorMessage = getErrorMessage(error);
  const redirectTo = callbackUrl?.startsWith("/") ? callbackUrl : "/dashboard";

  return (
    <main className="soc-canvas grid min-h-screen place-items-center px-4 py-8">
      <div className="grid w-full max-w-5xl overflow-hidden rounded-2xl border border-border bg-card shadow-2xl lg:grid-cols-[1.1fr_0.9fr]">
        <section className="relative overflow-hidden border-b border-border bg-[var(--sidebar)] px-7 py-10 text-[var(--sidebar-foreground)] sm:px-10 lg:border-r lg:border-b-0 lg:px-12 lg:py-14">
          <div className="absolute inset-0 opacity-70 [background-image:linear-gradient(rgba(68,196,234,0.08)_1px,transparent_1px),linear-gradient(90deg,rgba(68,196,234,0.08)_1px,transparent_1px)] [background-size:40px_40px]" aria-hidden="true" />
          <div className="relative flex h-full flex-col justify-between gap-12">
            <div>
              <div className="flex items-center gap-3">
                <span className="grid size-11 place-items-center rounded-xl bg-primary text-primary-foreground shadow-lg"><ShieldCheck className="size-6" aria-hidden="true" /></span>
                <div>
                  <p className="text-xl font-semibold tracking-[-0.035em]">AutoSOC</p>
                  <p className="text-xs font-medium uppercase tracking-[0.14em] text-[var(--sidebar-muted)]">Security operations</p>
                </div>
              </div>
              <h1 className="mt-12 max-w-md text-3xl font-semibold tracking-[-0.04em] text-white sm:text-4xl">
                Investigate with evidence. Respond with control.
              </h1>
              <p className="mt-4 max-w-md text-sm leading-6 text-[var(--sidebar-muted)]">
                Access the authenticated workspace for security telemetry, incident investigation, and human-reviewed response validation.
              </p>
            </div>
            <ul className="space-y-3 text-sm text-[var(--sidebar-foreground)]">
              {[
                "Federated Keycloak identity",
                "Role-aware investigation workflows",
                "Audited, validated-only response execution",
              ].map((item) => (
                <li key={item} className="flex items-center gap-2"><CheckCircle2 className="size-4 text-primary" aria-hidden="true" />{item}</li>
              ))}
            </ul>
          </div>
        </section>

        <section className="flex items-center px-7 py-10 sm:px-10 lg:px-12">
          <div className="w-full">
            <div className="flex size-10 items-center justify-center rounded-lg bg-accent text-accent-foreground"><LockKeyhole className="size-5" aria-hidden="true" /></div>
            <h2 className="mt-6 text-2xl font-semibold tracking-[-0.03em] text-foreground">Sign in to AutoSOC</h2>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">
              Continue with your organization’s AutoSOC Identity account. AutoSOC does not collect or store your password.
            </p>

            {errorMessage ? (
              <div className="mt-6 rounded-lg border border-destructive/35 bg-destructive/10 p-3 text-sm leading-6 text-foreground" role="alert">
                <p className="font-semibold text-destructive">Sign-in needs attention</p>
                <p className="mt-1 text-muted-foreground">{errorMessage}</p>
              </div>
            ) : null}

            <form
              action={async () => {
                "use server";
                await signIn("keycloak", { redirectTo });
              }}
              className="mt-8"
            >
              <Button type="submit" size="lg" className="h-11 w-full justify-between px-4 text-sm font-semibold">
                <span>Sign in with AutoSOC Identity</span>
                <ArrowRight className="size-4" aria-hidden="true" />
              </Button>
            </form>

            <p className="mt-5 text-xs leading-5 text-muted-foreground">
              Your session uses secure OpenID Connect authentication. If your session expires, return here to sign in again.
            </p>
          </div>
        </section>
      </div>
    </main>
  );
}
