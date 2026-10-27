import NextAuth, { type DefaultSession } from "next-auth";
import KeycloakProvider from "next-auth/providers/keycloak";

type RefreshTokenResponse = {
  access_token: string;
  expires_in: number;
  refresh_token?: string;
};

declare module "next-auth" {
  interface Session {
    user: {
      roles?: string[];
    } & DefaultSession["user"];
    accessToken?: string;
    error?: "RefreshAccessTokenError";
  }
}

function requiredAuthEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing required authentication setting: ${name}`);
  }
  return value;
}

const authSecret = process.env.AUTH_SECRET ?? process.env.NEXTAUTH_SECRET;
if (!authSecret) {
  throw new Error("Missing required authentication setting: AUTH_SECRET");
}
const authUrl = requiredAuthEnv("AUTH_URL").replace(/\/$/, "");
const keycloakIssuer = requiredAuthEnv("KEYCLOAK_ISSUER").replace(/\/$/, "");
const keycloakClientId = requiredAuthEnv("KEYCLOAK_CLIENT_ID");
const keycloakClientSecret = requiredAuthEnv("KEYCLOAK_CLIENT_SECRET");

async function refreshAccessToken(token: Record<string, unknown>) {
  const refreshToken = token.refreshToken;
  if (typeof refreshToken !== "string" || refreshToken.length === 0) {
    return { ...token, accessToken: undefined, error: "RefreshAccessTokenError" as const };
  }

  try {
    const response = await fetch(`${keycloakIssuer}/protocol/openid-connect/token`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        client_id: keycloakClientId,
        client_secret: keycloakClientSecret,
        grant_type: "refresh_token",
        refresh_token: refreshToken,
      }),
    });

    if (!response.ok) {
      throw new Error("Keycloak refresh-token exchange failed");
    }

    const refreshed = (await response.json()) as RefreshTokenResponse;
    if (!refreshed.access_token || !Number.isFinite(refreshed.expires_in)) {
      throw new Error("Keycloak refresh-token response was incomplete");
    }

    return {
      ...token,
      accessToken: refreshed.access_token,
      accessTokenExpires: Date.now() + refreshed.expires_in * 1000,
      // Keycloak can rotate refresh tokens. Keep the old one only if it did not.
      refreshToken: refreshed.refresh_token ?? refreshToken,
      error: undefined,
    };
  } catch (error) {
    // Do not expose the refresh token or provider response to the browser.
    console.error("Unable to refresh Keycloak access token", error);
    return { ...token, accessToken: undefined, error: "RefreshAccessTokenError" as const };
  }
}

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    KeycloakProvider({
      clientId: keycloakClientId,
      clientSecret: keycloakClientSecret,
      issuer: keycloakIssuer,
      // Keep the authorization request and callback on the same local host so
      // the HTTP-only PKCE verifier cookie is returned to the callback route.
      redirectProxyUrl: `${authUrl}/api/auth`,
      authorization: {
        params: {
          scope: "openid profile email roles",
        },
      },
    }),
  ],

  callbacks: {
    async redirect({ url }) {
      if (url.startsWith("/")) {
        return `${authUrl}${url}`;
      }

      return new URL(url).origin === authUrl ? url : authUrl;
    },

    async jwt({ token, account, profile }) {
      if (account?.access_token) {
        const accountWithExpiry = account as typeof account & { expires_in?: number };
        token.accessToken = account.access_token;
        // Some Keycloak/Auth.js combinations omit ``expires_at`` on the
        // initial authorization-code exchange but do provide ``expires_in``.
        // Treating the omission as epoch zero immediately attempted a refresh
        // and discarded an otherwise valid new session.
        const advertisedLifetime = accountWithExpiry.expires_in;
        token.accessTokenExpires = Date.now() +
          (typeof advertisedLifetime === "number" && advertisedLifetime > 0
            ? advertisedLifetime
            : 300) * 1000;
        // Kept only in the encrypted Auth.js JWT; it is never added to Session.
        token.refreshToken = account.refresh_token;
      }

      if (profile) {
        token.roles =
          (
            profile as {
              realm_access?: {
                roles?: string[];
              };
            }
          )?.realm_access?.roles || [];
      }

      const accessTokenExpires = token.accessTokenExpires;
      if (typeof accessTokenExpires === "number" && Date.now() < accessTokenExpires) {
        return token;
      }

      return refreshAccessToken(token);
    },

    async session({ session, token }) {
      // Expose the backend access token to the client session
      session.accessToken = token.accessToken as string | undefined;
      session.error = token.error as "RefreshAccessTokenError" | undefined;

      // Expose roles to the client session
      session.user.roles =
        (token.roles as string[]) || [];

      return session;
    },
  },

  session: {
    strategy: "jwt",
  },

  secret: authSecret,

  pages: {
    signIn: "/login",
  },
});
