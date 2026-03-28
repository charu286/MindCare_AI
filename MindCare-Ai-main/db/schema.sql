-- MindCare AI - MySQL 8+ Schema
-- Run this to create the database and tables.

CREATE DATABASE IF NOT EXISTS mindcare_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE mindcare_ai;

-- Users: anonymous (is_anonymous=TRUE) or registered (email, password_hash, is_anonymous=FALSE)
CREATE TABLE IF NOT EXISTS users (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_uuid CHAR(36) NOT NULL UNIQUE,
    email VARCHAR(255) UNIQUE NULL,
    password_hash VARCHAR(255) NULL,
    is_anonymous BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_uuid (user_uuid),
    INDEX idx_email (email),
    INDEX idx_created (created_at)
) ENGINE=InnoDB;

-- Sessions per user
CREATE TABLE IF NOT EXISTS sessions (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED NOT NULL,
    session_uuid CHAR(36) NOT NULL UNIQUE,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_session_uuid (session_uuid),
    INDEX idx_started (started_at)
) ENGINE=INNODB;

-- Conversation history (chat and test submissions)
CREATE TABLE IF NOT EXISTS conversation_history (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    session_id INT UNSIGNED NOT NULL,
    role ENUM('user','assistant') NOT NULL,
    content TEXT NOT NULL,
    meta JSON NULL COMMENT 'risk_score, emotion, tone, etc.',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    INDEX idx_session_id (session_id),
    INDEX idx_created (created_at)
) ENGINE=INNODB;

-- Daily aggregates for dashboard (last 7 days)
CREATE TABLE IF NOT EXISTS daily_trends (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED NOT NULL,
    date DATE NOT NULL,
    avg_stress DECIMAL(5,2) NOT NULL DEFAULT 0,
    peak_stress DECIMAL(5,2) NOT NULL DEFAULT 0,
    session_count INT UNSIGNED NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_user_date (user_id, date),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_date (user_id, date)
) ENGINE=INNODB;

-- Mental health terms for dictionary
CREATE TABLE IF NOT EXISTS mental_health_terms (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    term VARCHAR(255) NOT NULL,
    definition TEXT NOT NULL,
    category VARCHAR(100) NULL,
    sort_order INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_sort (sort_order)
) ENGINE=INNODB;

-- Coping strategies (for advice and resources)
CREATE TABLE IF NOT EXISTS coping_strategies (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100) NULL,
    steps JSON NULL COMMENT 'Array of step strings',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category)
) ENGINE=INNODB;

-- External/resources (helplines, when to seek help)
CREATE TABLE IF NOT EXISTS resources (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    url VARCHAR(512) NULL,
    description TEXT NULL,
    resource_type ENUM('helpline','article','org','other') NOT NULL DEFAULT 'other',
    region VARCHAR(100) NULL,
    sort_order INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_type (resource_type),
    INDEX idx_region (region),
    INDEX idx_sort (sort_order)
) ENGINE=INNODB;

-- Contact form submissions
CREATE TABLE IF NOT EXISTS contact_submissions (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    topic VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created (created_at)
) ENGINE=INNODB;

-- Fear & Phobia Explorer (extensible)
CREATE TABLE IF NOT EXISTS fears_phobias (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    meaning VARCHAR(255) NULL,
    description TEXT NOT NULL,
    emoji_or_icon VARCHAR(20) NULL,
    sort_order INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sort (sort_order)
) ENGINE=INNODB;

-- MCQ-based assessment results (stress/anxiety/depression)
CREATE TABLE IF NOT EXISTS assessment_results (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED NULL,
    assessment_type ENUM('stress','anxiety','depression') NOT NULL,
    total_score INT UNSIGNED NOT NULL,
    severity ENUM('minimal','mild','moderate','severe') NOT NULL,
    answers_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_type (user_id, assessment_type),
    INDEX idx_created (created_at)
) ENGINE=INNODB;
