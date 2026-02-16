"use client";

import { useState } from "react";
import { api } from "@/lib/api";

interface Props {
  onAuthenticated: (token: string) => void;
}

export default function AuthPanel({ onAuthenticated }: Props) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    try {
      if (mode === "register") {
        await api.register(email, password);
      }
      const login = await api.login(email, password);
      onAuthenticated(login.access_token);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unexpected error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card w-full max-w-md">
      <h1 className="text-xl font-semibold">Finance Tracker</h1>
      <p className="mt-1 text-sm text-slate-600">Track spending and savings with real data.</p>

      <form onSubmit={submit} className="mt-4 space-y-3">
        <input
          className="input"
          type="email"
          placeholder="Email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          className="input"
          type="password"
          placeholder="Password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button className="btn-primary w-full" disabled={loading}>
          {loading ? "Please wait..." : mode === "login" ? "Login" : "Create Account"}
        </button>
      </form>

      <button
        className="mt-3 text-sm text-slate-700 underline"
        onClick={() => setMode(mode === "login" ? "register" : "login")}
        type="button"
      >
        {mode === "login" ? "Need an account? Register" : "Already have an account? Login"}
      </button>

      {message && <p className="mt-3 text-sm text-red-600">{message}</p>}
    </div>
  );
}
