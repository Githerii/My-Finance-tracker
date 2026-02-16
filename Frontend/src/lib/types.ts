export type TransactionType = "income" | "expense";

export interface Transaction {
  id: number;
  amount: number;
  category: string;
  type: TransactionType;
  note?: string | null;
  occurred_on: string;
  created_at: string;
  user_id: number;
}

export interface Summary {
  total_income: number;
  total_expense: number;
  balance: number;
  savings_goal: number;
  savings_progress: number;
  remaining_to_goal: number;
  transaction_count: number;
  expenses_by_category: Record<string, number>;
}
