
DROP DATABASE IF EXISTS ourapp_db;
CREATE DATABASE IF NOT EXISTS ourapp_db;

USE ourapp_db;

CREATE TABLE users (

    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    header_image_url VARCHAR(255), 
    profile_image_url VARCHAR(255), 
    name VARCHAR(255),
    surname VARCHAR(255), 
    date_of_birth DATE, 
    phone_number VARCHAR(255), 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    gender VARCHAR(255) NULL,
    region VARCHAR(255) NULL,
    education VARCHAR(255) NULL
    
);

CREATE TABLE password_reset_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);


CREATE TABLE email_verification_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    new_email VARCHAR(255) NOT NULL,
    token VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_used INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);


-- Chat messages table to store chat messages
CREATE TABLE chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    is_from_user BOOLEAN NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    stage VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Summaries
CREATE TABLE IF NOT EXISTS summaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    conversation_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    abstract TEXT,
    original_dream TEXT,
    rewritten_dream TEXT,
    selected BOOLEAN DEFAULT FALSE,  
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS dream_entries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,  
    abstract TEXT NOT NULL,       
    original_dream TEXT NOT NULL,
    rewritten_dream TEXT NOT NULL,
    times INT DEFAULT 0,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);




