-- ==========================================================
-- HairSync: Web-Based Hair Donor and Recipient Management Platform
-- Database Schema for Module 1 (Authentication & User Profile)
-- ==========================================================

CREATE DATABASE IF NOT EXISTS `hairsync_db` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE `hairsync_db`;

-- 1. USERS TABLE
-- Stores credentials and user role information
DROP TABLE IF EXISTS `recipient_profiles`;
DROP TABLE IF EXISTS `ngo_profiles`;
DROP TABLE IF EXISTS `donor_profiles`;
DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(120) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `role` ENUM('admin', 'ngo', 'donor', 'recipient') NOT NULL,
    `status` ENUM('active', 'inactive', 'pending', 'suspended') DEFAULT 'active',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_user_email` (`email`),
    INDEX `idx_user_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. DONOR PROFILES TABLE
-- Stores donor-specific health and hair profile details
CREATE TABLE `donor_profiles` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL UNIQUE,
    `phone` VARCHAR(20) NOT NULL,
    `address` TEXT NOT NULL,
    `district` VARCHAR(80) NOT NULL,
    `hair_length` DECIMAL(5, 2) DEFAULT NULL COMMENT 'Length in inches',
    `hair_type` VARCHAR(50) DEFAULT NULL COMMENT 'Straight, Wavy, Curly, Coily',
    `hair_condition` VARCHAR(100) DEFAULT NULL COMMENT 'Virgin/Untreated, Colored, Gray, Chemically Treated',
    `photo` VARCHAR(255) DEFAULT NULL COMMENT 'File name of uploaded photo',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_donor_user` FOREIGN KEY (`user_id`) 
        REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. NGO PROFILES TABLE
-- Stores verified organization profiles and administration approval states
CREATE TABLE `ngo_profiles` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL UNIQUE,
    `organization_name` VARCHAR(150) NOT NULL,
    `registration_number` VARCHAR(100) NOT NULL UNIQUE,
    `phone` VARCHAR(20) NOT NULL,
    `email` VARCHAR(120) NOT NULL,
    `address` TEXT NOT NULL,
    `district` VARCHAR(80) NOT NULL,
    `description` TEXT DEFAULT NULL,
    `approval_status` ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_ngo_user` FOREIGN KEY (`user_id`) 
        REFERENCES `users` (`id`) ON DELETE CASCADE,
    INDEX `idx_ngo_approval` (`approval_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. RECIPIENT PROFILES TABLE
-- Stores recipient health/reason details for medical wig allocation
CREATE TABLE `recipient_profiles` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL UNIQUE,
    `phone` VARCHAR(20) NOT NULL,
    `address` TEXT NOT NULL,
    `district` VARCHAR(80) NOT NULL,
    `date_of_birth` DATE NOT NULL,
    `reason_for_wig` TEXT NOT NULL COMMENT 'e.g. Cancer Chemotherapy, Alopecia, Burn recovery',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_recipient_user` FOREIGN KEY (`user_id`) 
        REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================================
-- INITIAL SAMPLE DATA & DEFAULT SEEDS
-- All passwords below are: 'Password@123' (except Admin which is 'Admin@123')
-- Generated via Werkzeug generate_password_hash (compatible with Werkzeug 3.x)
-- ==========================================================

-- 1. Default Admin (Password: Admin@123)
-- Hash generated via werkzeug.security.generate_password_hash('Admin@123')
INSERT INTO `users` (`id`, `name`, `email`, `password_hash`, `role`, `status`) VALUES
(1, 'System Administrator', 'admin@hairsync.com', 'scrypt:32768:8:1$kYgqXv4F9w9B$9ff36c2e39ea7c265691079d86a608ce2a6a68f6bf7976e3d2319fcbba07e5c545300fbf5b07223e7f41ba8dfad9da6396e98418a0027137f8da52125211e4c7', 'admin', 'active');

-- 2. Sample Approved NGO (Password: Password@123)
INSERT INTO `users` (`id`, `name`, `email`, `password_hash`, `role`, `status`) VALUES
(2, 'Hope Hair Foundation', 'contact@hopehair.org', 'scrypt:32768:8:1$sN92bK7zL10A$a48e7e174b1262d103328ce78ebf899db4901f43a99bb843075c2e17ff987cb3be5d12ef2c93817f0e0df6cbe841103c8b4efcb70e7e1f5f3e9e116bc35aa833', 'ngo', 'active');

INSERT INTO `ngo_profiles` (`user_id`, `organization_name`, `registration_number`, `phone`, `email`, `address`, `district`, `description`, `approval_status`) VALUES
(2, 'Hope Hair Foundation', 'NGO-IND-2021-9874', '+91 9876543210', 'contact@hopehair.org', '45 Healthcare Boulevard, Near City Hospital', 'Ernakulam', 'Non-profit dedicated to manufacturing natural human-hair wigs for underprivileged cancer patients and medical hair loss survivors.', 'approved');

-- 3. Sample Pending NGO (Password: Password@123)
INSERT INTO `users` (`id`, `name`, `email`, `password_hash`, `role`, `status`) VALUES
(3, 'Grace Crown Care', 'info@gracecrown.org', 'scrypt:32768:8:1$sN92bK7zL10A$a48e7e174b1262d103328ce78ebf899db4901f43a99bb843075c2e17ff987cb3be5d12ef2c93817f0e0df6cbe841103c8b4efcb70e7e1f5f3e9e116bc35aa833', 'ngo', 'pending');

INSERT INTO `ngo_profiles` (`user_id`, `organization_name`, `registration_number`, `phone`, `email`, `address`, `district`, `description`, `approval_status`) VALUES
(3, 'Grace Crown Care', 'REG-KL-88321-2023', '+91 9845012345', 'info@gracecrown.org', '12 Greenfield Road, West Wing', 'Kozhikode', 'Community initiative supporting young pediatric chemotherapy patients with customized cranial prostheses.', 'pending');

-- 4. Sample Donor (Password: Password@123)
INSERT INTO `users` (`id`, `name`, `email`, `password_hash`, `role`, `status`) VALUES
(4, 'Ananya Sharma', 'donor@example.com', 'scrypt:32768:8:1$sN92bK7zL10A$a48e7e174b1262d103328ce78ebf899db4901f43a99bb843075c2e17ff987cb3be5d12ef2c93817f0e0df6cbe841103c8b4efcb70e7e1f5f3e9e116bc35aa833', 'donor', 'active');

INSERT INTO `donor_profiles` (`user_id`, `phone`, `address`, `district`, `hair_length`, `hair_type`, `hair_condition`, `photo`) VALUES
(4, '+91 9123456789', 'Apartment 4B, Silver Heights, Marine Drive', 'Ernakulam', 14.50, 'Wavy', 'Virgin/Untreated', NULL);

-- 5. Sample Recipient (Password: Password@123)
INSERT INTO `users` (`id`, `name`, `email`, `password_hash`, `role`, `status`) VALUES
(5, 'Meera Nair', 'recipient@example.com', 'scrypt:32768:8:1$sN92bK7zL10A$a48e7e174b1262d103328ce78ebf899db4901f43a99bb843075c2e17ff987cb3be5d12ef2c93817f0e0df6cbe841103c8b4efcb70e7e1f5f3e9e116bc35aa833', 'recipient', 'active');

INSERT INTO `recipient_profiles` (`user_id`, `phone`, `address`, `district`, `date_of_birth`, `reason_for_wig`) VALUES
(5, '+91 9988776655', 'House No 23, Rose Gardens, Kowdiar', 'Thiruvananthapuram', '1998-05-14', 'Undergoing chemotherapy treatment for breast cancer. Requesting natural wig for emotional confidence.');
