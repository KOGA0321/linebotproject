-- membersテーブルに stripe_customer_id という新しい列を追加
ALTER TABLE members ADD COLUMN stripe_customer_id TEXT;
