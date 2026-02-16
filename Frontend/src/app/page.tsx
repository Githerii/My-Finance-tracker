"use client";

import { useEffect, useState } from "react";
import AuthPanel from "@/components/AuthPanel";
import Dashboard from "@/components/Dashboard";

const TOKEN_KEY = "finance_tracker_token";

export default function Home() {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const saved = localStorage.getItem(TOKEN_KEY);
    if (saved) setToken(saved);
  }, []);

  const onAuthenticated = (newToken: string) => {
    localStorage.setItem(TOKEN_KEY, newToken);
    setToken(newToken);
  };

  const onLogout = () => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
  };

  if (!token) {
    return (
      <main className="flex min-h-screen items-center justify-center p-4">
        <AuthPanel onAuthenticated={onAuthenticated} />
      </main>
    );
  }

  return <Dashboard token={token} onLogout={onLogout} />;
}
