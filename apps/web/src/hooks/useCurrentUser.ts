"use client";

import { useEffect, useState } from "react";

interface JwtPayload {
  sub: string;
  email: string;
  full_name: string;
  role: string;
  type: string;
  exp: number;
}

function parseJwt(token: string): JwtPayload | null {
  try {
    const [, payload] = token.split(".");
    const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(json) as JwtPayload;
  } catch {
    return null;
  }
}

export interface CurrentUser {
  id: string;
  email: string;
  fullName: string;
  role: string;
}

export function useCurrentUser(): CurrentUser | null {
  const [user, setUser] = useState<CurrentUser | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("pulse_access_token");
    if (!token) return;
    const payload = parseJwt(token);
    if (!payload || payload.type !== "access") return;
    setUser({
      id: payload.sub,
      email: payload.email,
      fullName: payload.full_name,
      role: payload.role,
    });
  }, []);

  return user;
}
