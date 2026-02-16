"use client";

import { useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";
import { Summary, Transaction, TransactionType } from "@/lib/types";

interface Props {
  token: string;
  onLogout: () => void;
}

const defaultSummary: Summary = {
  total_income: 0,
  total_expense: 0,
  balance: 0,
  savings_goal: 0,
  savings_progress: 0,
  remaining_to_goal: 0,
  transaction_count: 0,
  expenses_by_category: {},
};

export default function Dashboard({ token, onLogout }: Props) {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [summary, setSummary] = useState<Summary>(defaultSummary);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("");
  const [type, setType] = useState<TransactionType>("expense");
  const [note, setNote] = useState("");
  const [occurredOn, setOccurredOn] = useState("");
  const [goal, setGoal] = useState("");

  const [filterType, setFilterType] = useState<"" | TransactionType>("");
  const [filterCategory, setFilterCategory] = useState("");

  const query = useMemo(() => {
    const params = new URLSearchParams();
    if (filterType) params.set("type", filterType);
    if (filterCategory) params.set("category", filterCategory);
    const q = params.toString();
    return q ? `?${q}` : "";
  }, [filterType, filterCategory]);

  const loadData = async () => {
    setLoading(true);
    setMessage(null);
    try {
      const [txs, sum] = await Promise.all([
        api.getTransactions(token, query),
        api.getSummary(token),
      ]);
      setTransactions(txs);
      setSummary(sum);
      setGoal(sum.savings_goal ? String(sum.savings_goal) : "");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [query]);

  const addTransaction = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    try {
      await api.createTransaction(token, {
        amount: Number(amount),
        category,
        type,
        note,
        occurred_on: occurredOn || undefined,
      });
      setAmount("");
      setCategory("");
      setType("expense");
      setNote("");
      setOccurredOn("");
      await loadData();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to create transaction");
    }
  };

  const removeTransaction = async (id: number) => {
    setMessage(null);
    try {
      await api.deleteTransaction(token, id);
      await loadData();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to delete transaction");
    }
  };

  const toggleType = async (tx: Transaction) => {
    setMessage(null);
    try {
      await api.updateTransaction(token, tx.id, {
        type: tx.type === "income" ? "expense" : "income",
      });
      await loadData();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to update transaction");
    }
  };

  const updateGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    try {
      await api.updateSavingsGoal(token, Number(goal));
      await loadData();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to update savings goal");
    }
  };

  return (
    <main className="mx-auto max-w-6xl p-4 md:p-6">
      <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold">My Finance Tracker</h1>
        <button className="btn-secondary w-full sm:w-auto" onClick={onLogout}>
          Logout
        </button>
      </div>

      {message && <p className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{message}</p>}

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Income" value={summary.total_income} positive />
        <StatCard label="Expenses" value={summary.total_expense} />
        <StatCard label="Balance" value={summary.balance} positive={summary.balance >= 0} />
        <StatCard label="To Savings Goal" value={summary.remaining_to_goal} />
      </section>

      <section className="mt-6 grid gap-4 lg:grid-cols-2">
        <form className="card space-y-3" onSubmit={addTransaction}>
          <h2 className="text-lg font-semibold">Add Transaction</h2>
          <div className="grid gap-3 sm:grid-cols-2">
            <input className="input" type="number" step="0.01" placeholder="Amount" value={amount} onChange={(e) => setAmount(e.target.value)} required />
            <input className="input" type="text" placeholder="Category (e.g. food)" value={category} onChange={(e) => setCategory(e.target.value)} required />
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <select className="input" value={type} onChange={(e) => setType(e.target.value as TransactionType)}>
              <option value="expense">Expense</option>
              <option value="income">Income</option>
            </select>
            <input className="input" type="date" value={occurredOn} onChange={(e) => setOccurredOn(e.target.value)} />
          </div>
          <input className="input" type="text" placeholder="Note (optional)" value={note} onChange={(e) => setNote(e.target.value)} />
          <button className="btn-primary w-full">Add</button>
        </form>

        <form className="card space-y-3" onSubmit={updateGoal}>
          <h2 className="text-lg font-semibold">Savings Goal</h2>
          <p className="text-sm text-slate-600">Set your target and track how close your current balance is.</p>
          <input className="input" type="number" step="0.01" placeholder="Savings goal" value={goal} onChange={(e) => setGoal(e.target.value)} required />
          <button className="btn-primary w-full">Update Goal</button>
          <div className="rounded-lg bg-slate-100 p-3 text-sm">
            <p>Current Goal: <span className="font-semibold">${summary.savings_goal.toFixed(2)}</span></p>
            <p>Progress: <span className="font-semibold">${summary.savings_progress.toFixed(2)}</span></p>
          </div>
        </form>
      </section>

      <section className="card mt-6">
        <div className="mb-3 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <h2 className="text-lg font-semibold">Transactions</h2>
          <div className="grid gap-2 sm:grid-cols-2">
            <select className="input" value={filterType} onChange={(e) => setFilterType(e.target.value as "" | TransactionType)}>
              <option value="">All types</option>
              <option value="income">Income</option>
              <option value="expense">Expense</option>
            </select>
            <input className="input" placeholder="Filter category" value={filterCategory} onChange={(e) => setFilterCategory(e.target.value)} />
          </div>
        </div>

        {loading ? (
          <p className="text-sm text-slate-600">Loading...</p>
        ) : transactions.length === 0 ? (
          <p className="text-sm text-slate-600">No transactions yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead>
                <tr className="border-b">
                  <th className="px-2 py-2">Date</th>
                  <th className="px-2 py-2">Category</th>
                  <th className="px-2 py-2">Type</th>
                  <th className="px-2 py-2">Amount</th>
                  <th className="px-2 py-2">Note</th>
                  <th className="px-2 py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((tx) => (
                  <tr key={tx.id} className="border-b last:border-0">
                    <td className="px-2 py-2">{tx.occurred_on}</td>
                    <td className="px-2 py-2">{tx.category}</td>
                    <td className="px-2 py-2">
                      <span className={`rounded px-2 py-1 text-xs ${tx.type === "income" ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"}`}>
                        {tx.type}
                      </span>
                    </td>
                    <td className="px-2 py-2">${tx.amount.toFixed(2)}</td>
                    <td className="px-2 py-2">{tx.note || "-"}</td>
                    <td className="px-2 py-2">
                      <div className="flex flex-wrap gap-2">
                        <button className="btn-secondary" onClick={() => toggleType(tx)}>
                          Switch Type
                        </button>
                        <button className="btn-secondary" onClick={() => removeTransaction(tx.id)}>
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}

function StatCard({ label, value, positive }: { label: string; value: number; positive?: boolean }) {
  return (
    <div className="card">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className={`mt-1 text-2xl font-semibold ${positive ? "text-emerald-600" : "text-slate-900"}`}>
        ${value.toFixed(2)}
      </p>
    </div>
  );
}
