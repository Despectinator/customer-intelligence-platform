-- Customer Intelligence Platform — database schema
-- Run this in the Supabase SQL editor (Project > SQL Editor > New query)
--
-- Design principle: RFM (Recency, Frequency, Monetary) values are never stored.
-- They are always calculated on demand from the `transactions` table.
-- Only the clustering RESULT (segment assignment) is persisted, since that's
-- the expensive computation worth caching. See docs/architecture/Database-Schema.md.

create extension if not exists "uuid-ossp";

-- Projects: each represents a store/brand/client owned by a user
create table if not exists projects (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid not null references auth.users(id) on delete cascade,
    name text not null,
    description text,
    created_at timestamptz not null default now()
);

-- Customers: belong to a project
create table if not exists customers (
    id uuid primary key default uuid_generate_v4(),
    project_id uuid not null references projects(id) on delete cascade,
    customer_name text not null,
    email text,
    phone text,
    created_at timestamptz not null default now()
);

-- Transactions: the single source of truth RFM is calculated from
create table if not exists transactions (
    id uuid primary key default uuid_generate_v4(),
    customer_id uuid not null references customers(id) on delete cascade,
    order_date date not null,
    order_amount numeric(12, 2) not null,
    payment_method text,
    created_at timestamptz not null default now()
);

-- Segments: current clustering RESULT per customer (not RFM values)
create table if not exists segments (
    id uuid primary key default uuid_generate_v4(),
    project_id uuid not null references projects(id) on delete cascade,
    customer_id uuid not null unique references customers(id) on delete cascade,
    cluster_number integer,
    segment_name text,
    generated_at timestamptz not null default now()
);
-- Note: recommendation text is NOT stored here — it's resolved in application
-- code from a segment_name -> recommendation lookup, since it's identical for
-- every customer in a given segment.

-- Segment history: append-only log of segment changes (powers the real-time migration feed)
create table if not exists segment_history (
    id uuid primary key default uuid_generate_v4(),
    customer_id uuid not null references customers(id) on delete cascade,
    old_segment text,
    new_segment text not null,
    changed_at timestamptz not null default now()
);

create index if not exists idx_customers_project on customers(project_id);
create index if not exists idx_transactions_customer on transactions(customer_id);
create index if not exists idx_segments_project on segments(project_id);
create index if not exists idx_segment_history_customer on segment_history(customer_id);

-- Row Level Security: a user can only ever see their own projects and everything under them
alter table projects enable row level security;
alter table customers enable row level security;
alter table transactions enable row level security;
alter table segments enable row level security;
alter table segment_history enable row level security;

create policy "Users manage their own projects"
    on projects for all
    using (auth.uid() = user_id)
    with check (auth.uid() = user_id);

create policy "Users manage customers in their own projects"
    on customers for all
    using (project_id in (select id from projects where user_id = auth.uid()))
    with check (project_id in (select id from projects where user_id = auth.uid()));

create policy "Users manage transactions in their own projects"
    on transactions for all
    using (customer_id in (
        select c.id from customers c
        join projects p on p.id = c.project_id
        where p.user_id = auth.uid()
    ))
    with check (customer_id in (
        select c.id from customers c
        join projects p on p.id = c.project_id
        where p.user_id = auth.uid()
    ));

create policy "Users manage segments in their own projects"
    on segments for all
    using (project_id in (select id from projects where user_id = auth.uid()))
    with check (project_id in (select id from projects where user_id = auth.uid()));

create policy "Users view segment history in their own projects"
    on segment_history for select
    using (customer_id in (
        select c.id from customers c
        join projects p on p.id = c.project_id
        where p.user_id = auth.uid()
    ));
