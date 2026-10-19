-- Run this in the Supabase SQL Editor to create the required tables.

create table resumes (
  id uuid primary key default gen_random_uuid(),
  original_filename text not null,
  storage_path text not null,
  extracted_text text,
  parsed_data jsonb,
  created_at timestamptz default now()
);

create table job_descriptions (
  id uuid primary key default gen_random_uuid(),
  title text,
  original_filename text,
  storage_path text,
  raw_text text,
  extracted_text text,
  parsed_data jsonb,
  created_at timestamptz default now(),

  constraint jd_input_required check (
    raw_text is not null
    or storage_path is not null
  )
);

create table match_results (
  id uuid primary key default gen_random_uuid(),
  resume_id uuid references resumes(id),
  jd_id uuid references job_descriptions(id),
  overall_score integer,
  skill_score integer,
  experience_score integer,
  qualification_score integer,
  soft_skill_score integer,
  result_data jsonb,
  created_at timestamptz default now()
);
