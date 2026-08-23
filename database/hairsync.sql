-- ==========================================================
-- HairSync: Web-Based Hair Donor and Recipient Management Platform
-- Database Schema for Module 1 (SQLite Compatible)
-- ==========================================================

-- Enable Foreign Key support
PRAGMA foreign_keys = ON;

-- 1. USERS TABLE
-- Stores credentials and user role information
DROP TABLE IF EXISTS recipient_profiles;
DROP TABLE IF EXISTS ngo_profiles;
DROP TABLE IF EXISTS donor_profiles;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'ngo', 'donor', 'recipient')),
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'pending', 'suspended')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_user_role ON users(role);

-- 2. DONOR PROFILES TABLE
-- Stores donor-specific health and hair profile details
CREATE TABLE donor_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    address TEXT NOT NULL,
    district TEXT NOT NULL,
    hair_length REAL DEFAULT NULL,
    hair_type TEXT DEFAULT NULL,
    hair_condition TEXT DEFAULT NULL,
    photo TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- 3. NGO PROFILES TABLE
-- Stores verified organization profiles and administration approval states
CREATE TABLE ngo_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    organization_name TEXT NOT NULL,
    registration_number TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    address TEXT NOT NULL,
    district TEXT NOT NULL,
    description TEXT DEFAULT NULL,
    approval_status TEXT DEFAULT 'pending' CHECK(approval_status IN ('pending', 'approved', 'rejected')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_ngo_approval ON ngo_profiles(approval_status);

-- 4. RECIPIENT PROFILES TABLE
-- Stores recipient health/reason details for medical wig allocation
CREATE TABLE recipient_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    address TEXT NOT NULL,
    district TEXT NOT NULL,
    date_of_birth DATE NOT NULL,
    reason_for_wig TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- 5. DONATION CENTERS TABLE (Module 2)
-- Stores physical donation collection hubs managed by verified NGOs
CREATE TABLE IF NOT EXISTS donation_centers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ngo_id INTEGER NOT NULL,
    center_name TEXT NOT NULL,
    address TEXT NOT NULL,
    district TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'Kerala',
    pincode TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT DEFAULT NULL,
    opening_time TEXT NOT NULL,
    closing_time TEXT NOT NULL,
    working_days TEXT NOT NULL,
    description TEXT DEFAULT NULL,
    latitude REAL DEFAULT NULL,
    longitude REAL DEFAULT NULL,
    status TEXT DEFAULT 'Active' CHECK(status IN ('Active', 'Inactive', 'Pending', 'Rejected', 'Approved')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ngo_id) REFERENCES ngo_profiles (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_dc_ngo ON donation_centers(ngo_id);
CREATE INDEX IF NOT EXISTS idx_dc_district ON donation_centers(district);
CREATE INDEX IF NOT EXISTS idx_dc_status ON donation_centers(status);

-- ==========================================================
-- INITIAL SAMPLE DATA & DEFAULT SEEDS
-- Default accounts:
-- 1. Admin     : admin@hairsync.com      / Admin@123
-- 2. Approved NGO: contact@hopehair.org  / Password@123
-- 3. Pending NGO : info@gracecrown.org   / Password@123
-- 4. Donor     : donor@example.com       / Password@123
-- 5. Recipient : recipient@example.com   / Password@123
-- Note: Password hashes are generated dynamically by init_db.py
-- ==========================================================

-- 1. Default Admin (Password: Admin@123)
INSERT INTO users (id, name, email, password_hash, role, status) VALUES
(1, 'System Administrator', 'admin@hairsync.com', 'scrypt:32768:8:1$placeholder$admin', 'admin', 'active');

-- 2. Sample Approved NGO (Password: Password@123)
INSERT INTO users (id, name, email, password_hash, role, status) VALUES
(2, 'Hope Hair Foundation', 'contact@hopehair.org', 'scrypt:32768:8:1$placeholder$sample', 'ngo', 'active');

INSERT INTO ngo_profiles (user_id, organization_name, registration_number, phone, email, address, district, description, approval_status) VALUES
(2, 'Hope Hair Foundation', 'NGO-IND-2021-9874', '+91 9876543210', 'contact@hopehair.org', '45 Healthcare Boulevard, Near City Hospital', 'Ernakulam', 'Non-profit dedicated to manufacturing natural human-hair wigs for underprivileged cancer patients and medical hair loss survivors.', 'approved');

-- 3. Sample Pending NGO (Password: Password@123)
INSERT INTO users (id, name, email, password_hash, role, status) VALUES
(3, 'Grace Crown Care', 'info@gracecrown.org', 'scrypt:32768:8:1$placeholder$sample', 'ngo', 'pending');

INSERT INTO ngo_profiles (user_id, organization_name, registration_number, phone, email, address, district, description, approval_status) VALUES
(3, 'Grace Crown Care', 'REG-KL-88321-2023', '+91 9845012345', 'info@gracecrown.org', '12 Greenfield Road, West Wing', 'Kozhikode', 'Community initiative supporting young pediatric chemotherapy patients with customized cranial prostheses.', 'pending');

-- 4. Sample Donor (Password: Password@123)
INSERT INTO users (id, name, email, password_hash, role, status) VALUES
(4, 'Ananya Sharma', 'donor@example.com', 'scrypt:32768:8:1$placeholder$sample', 'donor', 'active');

INSERT INTO donor_profiles (user_id, phone, address, district, hair_length, hair_type, hair_condition, photo) VALUES
(4, '+91 9123456789', 'Apartment 4B, Silver Heights, Marine Drive', 'Ernakulam', 14.50, 'Wavy', 'Virgin/Untreated', NULL);

-- 5. Sample Recipient (Password: Password@123)
INSERT INTO users (id, name, email, password_hash, role, status) VALUES
(5, 'Meera Nair', 'recipient@example.com', 'scrypt:32768:8:1$placeholder$sample', 'recipient', 'active');

INSERT INTO recipient_profiles (user_id, phone, address, district, date_of_birth, reason_for_wig) VALUES
(5, '+91 9988776655', 'House No 23, Rose Gardens, Kowdiar', 'Thiruvananthapuram', '1998-05-14', 'Undergoing chemotherapy treatment for breast cancer. Requesting natural wig for emotional confidence.');

-- 6. Sample Donation Center for Hope Hair Foundation (ngo_id = 1)
INSERT INTO donation_centers (id, ngo_id, center_name, address, district, city, state, pincode, phone, email, opening_time, closing_time, working_days, description, latitude, longitude, status) VALUES
(1, 1, 'Kochi Central Hair Drop Center', '45 Healthcare Boulevard, Near City Hospital, Marine Drive', 'Ernakulam', 'Kochi', 'Kerala', '682031', '+91 9876543210', 'kochi.center@hopehair.org', '09:00', '17:00', 'Monday - Saturday', 'Primary collection hub accepting sanitized hair donations, measurements, and donor consultations.', 9.9816, 76.2799, 'Active');
