-- Aligns the customers table with the current SQLAlchemy model
-- (first_name / last_name / company instead of customer_name).
-- Safe to run: no successful customer inserts exist yet.

alter table customers
    add column if not exists first_name text,
    add column if not exists last_name text,
    add column if not exists company text;

-- If any rows exist from earlier partial attempts, put their old
-- customer_name into first_name so nothing is silently dropped.
update customers
set first_name = coalesce(first_name, customer_name)
where customer_name is not null;

alter table customers alter column first_name set not null;
alter table customers alter column last_name set not null;
alter table customers alter column email set not null;

alter table customers drop column if exists customer_name;

alter table customers
    add constraint uq_customer_project_email unique (project_id, email);

create index if not exists ix_customer_project_id on customers(project_id);
create index if not exists ix_customer_email on customers(email);
