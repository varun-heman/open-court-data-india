-- Schema for Delhi High Court cause list data

-- Create database if it doesn't exist
-- Note: This needs to be run separately as CREATE DATABASE cannot be in a transaction
-- CREATE DATABASE ecourts;

-- Connect to the database
-- \c ecourts

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Court table
CREATE TABLE IF NOT EXISTS courts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    website VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Court bench table
CREATE TABLE IF NOT EXISTS court_benches (
    id SERIAL PRIMARY KEY,
    court_id INTEGER REFERENCES courts(id) ON DELETE CASCADE,
    bench_number VARCHAR(50) NOT NULL,
    judges TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(court_id, bench_number)
);

-- Cause list table
CREATE TABLE IF NOT EXISTS cause_lists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    court_id INTEGER REFERENCES courts(id) ON DELETE CASCADE,
    bench_id INTEGER REFERENCES court_benches(id) ON DELETE SET NULL,
    list_date DATE NOT NULL,
    list_type VARCHAR(100) DEFAULT 'Daily List',
    pdf_url TEXT,
    pdf_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(court_id, bench_id, list_date, list_type)
);

-- Case tags table
CREATE TABLE IF NOT EXISTS case_tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Cases table
CREATE TABLE IF NOT EXISTS cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cause_list_id UUID REFERENCES cause_lists(id) ON DELETE CASCADE,
    item_number VARCHAR(50),
    case_number VARCHAR(255) NOT NULL,
    title TEXT,
    file_number VARCHAR(255),
    petitioner_adv TEXT,
    respondent_adv TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Case tags mapping table
CREATE TABLE IF NOT EXISTS case_tag_mappings (
    case_id UUID REFERENCES cases(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES case_tags(id) ON DELETE CASCADE,
    PRIMARY KEY (case_id, tag_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert default court data
INSERT INTO courts (name, code, website)
VALUES ('Delhi High Court', 'delhi_hc', 'https://delhihighcourt.nic.in/')
ON CONFLICT (code) DO NOTHING;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_cause_lists_court_date ON cause_lists(court_id, list_date);
CREATE INDEX IF NOT EXISTS idx_cases_cause_list ON cases(cause_list_id);
CREATE INDEX IF NOT EXISTS idx_case_tag_mappings_case ON case_tag_mappings(case_id);
CREATE INDEX IF NOT EXISTS idx_case_tag_mappings_tag ON case_tag_mappings(tag_id);

-- Create or replace function to update timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at timestamps
CREATE TRIGGER update_courts_modtime
BEFORE UPDATE ON courts
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_court_benches_modtime
BEFORE UPDATE ON court_benches
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_cause_lists_modtime
BEFORE UPDATE ON cause_lists
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_cases_modtime
BEFORE UPDATE ON cases
FOR EACH ROW EXECUTE FUNCTION update_modified_column();
