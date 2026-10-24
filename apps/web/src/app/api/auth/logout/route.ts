import { cookies } from "next/headers";
import { NextResponse } from "next/server";

export async function GET(request: Request) {
  const cookieStore = await cookies();
  
  // Delete all next-auth and authjs session/csrf cookies
  const allCookies = cookieStore.getAll();
  for (const c of allCookies) {
    if (
      c.name.includes("session") ||
      c.name.includes("csrf") ||
      c.name.includes("auth") ||
      c.name.includes("callback")
    ) {
      cookieStore.delete(c.name);
    }
  }

  const loginUrl = new URL("/login", request.url);
  return NextResponse.redirect(loginUrl);
}

export async function POST(request: Request) {
  const cookieStore = await cookies();
  
  // Delete all next-auth and authjs session/csrf cookies
  const allCookies = cookieStore.getAll();
  for (const c of allCookies) {
    if (
      c.name.includes("session") ||
      c.name.includes("csrf") ||
      c.name.includes("auth") ||
      c.name.includes("callback")
    ) {
      cookieStore.delete(c.name);
    }
  }

  const loginUrl = new URL("/login", request.url);
  return NextResponse.redirect(loginUrl);
}
