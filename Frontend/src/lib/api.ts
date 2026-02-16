import { Summary, Transaction, TransactionType } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000";

async function request<T>(path: string, token?: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || "Request failed");
  }
  return data as T;
}

export const api = {
  register: (email: string, password: string) =>
    request<{ message: string }>("/auth/register", undefined, {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  login: (email: string, password: string) =>
    request<{ access_token: string }>("/auth/login", undefined, {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  getTransactions: (token: string, query = "") => request<Transaction[]>(`/transactions${query}`, token),

  createTransaction: (
    token: string,
    payload: {
      amount: number;
      category: string;
      type: TransactionType;
      note?: string;
      occurred_on?: string;
    }
  ) =>
    request<{ message: string; transaction: Transaction }>("/transactions", token, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  updateTransaction: (
    token: string,
    id: number,
    payload: Partial<{ amount: number; category: string; type: TransactionType; note: string; occurred_on: string }>
  ) =>
    request<{ message: string; transaction: Transaction }>(`/transactions/${id}`, token, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),

  deleteTransaction: (token: string, id: number) =>
    request<{ message: string }>(`/transactions/${id}`, token, {
      method: "DELETE",
    }),

  updateSavingsGoal: (token: string, savings_goal: number) =>
    request<{ message: string; savings_goal: number }>("/me/savings-goal", token, {
      method: "PATCH",
      body: JSON.stringify({ savings_goal }),
    }),

  getSummary: (token: string) => request<Summary>("/me/summary", token),
};
