-- ============================================
-- AUTH PROJECT - PostgreSQL Database Schema
-- ============================================
-- DDL, DML, Triggers, Functions, Indexes
-- Database: PostgreSQL 14+
-- Features: RBAC, Token Management, Device Tracking, Login Attempts
-- ============================================

-- ============================================
-- 1. EXTENSIONS
-- ============================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- 2. CUSTOM TYPES (ENUMS)
-- ============================================
DO $$ BEGIN
    CREATE TYPE token_type AS ENUM ('access', 'refresh');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE device_status AS ENUM ('active', 'inactive', 'blocked');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ============================================
-- 3. DDL - CORE TABLES
-- ============================================

-- ----------------------------------------
-- 3.1 RBAC TABLES
-- ----------------------------------------

-- Permissions table
CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    code VARCHAR(100) NOT NULL,
    description TEXT,
    module VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT permissions_code_unique UNIQUE (code)
);

-- Roles table
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    is_system BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT roles_code_unique UNIQUE (code)
);

-- Role-Permission mapping (Many-to-Many)
CREATE TABLE IF NOT EXISTS role_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_id UUID NOT NULL,
    permission_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_role_permissions_role 
        FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    CONSTRAINT fk_role_permissions_permission 
        FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
    CONSTRAINT role_permissions_unique UNIQUE (role_id, permission_id)
);

-- ----------------------------------------
-- 3.2 USERS TABLE
-- ----------------------------------------

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    role_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT users_email_unique UNIQUE (email),
    CONSTRAINT users_email_valid CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT fk_users_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE SET NULL
);

-- ----------------------------------------
-- 3.3 TOKEN MANAGEMENT TABLES
-- ----------------------------------------

-- Token Families (for refresh token rotation)
CREATE TABLE IF NOT EXISTS token_families (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    device_id UUID,
    current_jti VARCHAR(36) NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_token_families_user 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Token Blacklist (for logout)
CREATE TABLE IF NOT EXISTS token_blacklist (
    id SERIAL PRIMARY KEY,
    jti VARCHAR(36) NOT NULL,
    token_type token_type NOT NULL,
    user_id UUID,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    blacklisted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reason VARCHAR(100),
    
    CONSTRAINT token_blacklist_jti_unique UNIQUE (jti),
    CONSTRAINT fk_token_blacklist_user 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- ----------------------------------------
-- 3.4 EMAIL VERIFICATION TOKENS
-- ----------------------------------------

CREATE TABLE IF NOT EXISTS email_verification_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    verified_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT fk_email_verification_user 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ----------------------------------------
-- 3.5 PASSWORD RESET TOKENS
-- ----------------------------------------

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT fk_password_reset_user 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ----------------------------------------
-- 3.6 USER DEVICES (Device Management)
-- ----------------------------------------

CREATE TABLE IF NOT EXISTS user_devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    device_name VARCHAR(255),
    device_type VARCHAR(50),
    browser VARCHAR(100),
    os VARCHAR(100),
    ip_address VARCHAR(45),
    user_agent TEXT,
    fingerprint VARCHAR(255),
    status device_status DEFAULT 'active',
    is_trusted BOOLEAN DEFAULT FALSE,
    last_login_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_user_devices_user 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Add FK from token_families to user_devices
ALTER TABLE token_families 
    ADD CONSTRAINT fk_token_families_device 
    FOREIGN KEY (device_id) REFERENCES user_devices(id) ON DELETE SET NULL;

-- ----------------------------------------
-- 3.7 LOGIN ATTEMPTS (Failed Login Tracking)
-- ----------------------------------------

CREATE TABLE IF NOT EXISTS login_attempts (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    user_id UUID,
    ip_address VARCHAR(45) NOT NULL,
    user_agent TEXT,
    is_successful BOOLEAN DEFAULT FALSE,
    failure_reason VARCHAR(100),
    attempted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_login_attempts_user 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================
-- 4. INDEXES
-- ============================================

-- RBAC indexes
CREATE INDEX IF NOT EXISTS idx_permissions_code ON permissions(code);
CREATE INDEX IF NOT EXISTS idx_permissions_module ON permissions(module);
CREATE INDEX IF NOT EXISTS idx_roles_code ON roles(code);
CREATE INDEX IF NOT EXISTS idx_role_permissions_role ON role_permissions(role_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_permission ON role_permissions(permission_id);

-- Users indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role_id);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_users_verified ON users(is_verified);

-- Token Families indexes
CREATE INDEX IF NOT EXISTS idx_token_families_user_id ON token_families(user_id);
CREATE INDEX IF NOT EXISTS idx_token_families_device_id ON token_families(device_id);
CREATE INDEX IF NOT EXISTS idx_token_families_current_jti ON token_families(current_jti);
CREATE INDEX IF NOT EXISTS idx_token_families_expires_at ON token_families(expires_at);
CREATE INDEX IF NOT EXISTS idx_token_families_active ON token_families(user_id, is_revoked) 
    WHERE is_revoked = FALSE;

-- Token Blacklist indexes
CREATE INDEX IF NOT EXISTS idx_token_blacklist_jti ON token_blacklist(jti);
CREATE INDEX IF NOT EXISTS idx_token_blacklist_expires_at ON token_blacklist(expires_at);
CREATE INDEX IF NOT EXISTS idx_token_blacklist_user_id ON token_blacklist(user_id);

-- Email Verification indexes
CREATE INDEX IF NOT EXISTS idx_email_verification_user ON email_verification_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_email_verification_token ON email_verification_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_email_verification_expires ON email_verification_tokens(expires_at);

-- Password Reset indexes
CREATE INDEX IF NOT EXISTS idx_password_reset_user ON password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_token ON password_reset_tokens(token_hash);

-- User Devices indexes
CREATE INDEX IF NOT EXISTS idx_user_devices_user ON user_devices(user_id);
CREATE INDEX IF NOT EXISTS idx_user_devices_fingerprint ON user_devices(fingerprint);
CREATE INDEX IF NOT EXISTS idx_user_devices_status ON user_devices(status);
CREATE INDEX IF NOT EXISTS idx_user_devices_trusted ON user_devices(user_id, is_trusted) 
    WHERE is_trusted = TRUE;

-- Login Attempts indexes
CREATE INDEX IF NOT EXISTS idx_login_attempts_email ON login_attempts(email);
CREATE INDEX IF NOT EXISTS idx_login_attempts_ip ON login_attempts(ip_address);
CREATE INDEX IF NOT EXISTS idx_login_attempts_user ON login_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_login_attempts_time ON login_attempts(attempted_at);
CREATE INDEX IF NOT EXISTS idx_login_attempts_failed ON login_attempts(email, ip_address, attempted_at) 
    WHERE is_successful = FALSE;

-- ============================================
-- 5. FUNCTIONS
-- ============================================

-- Function: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function: Update last_used_at
CREATE OR REPLACE FUNCTION update_last_used_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_used_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function: Clean expired tokens
CREATE OR REPLACE FUNCTION cleanup_expired_tokens()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
    temp_count INTEGER;
BEGIN
    -- Clean token blacklist
    DELETE FROM token_blacklist WHERE expires_at < CURRENT_TIMESTAMP;
    GET DIAGNOSTICS temp_count = ROW_COUNT;
    deleted_count := deleted_count + temp_count;
    
    -- Clean token families
    DELETE FROM token_families WHERE expires_at < CURRENT_TIMESTAMP;
    GET DIAGNOSTICS temp_count = ROW_COUNT;
    deleted_count := deleted_count + temp_count;
    
    -- Clean email verification tokens
    DELETE FROM email_verification_tokens WHERE expires_at < CURRENT_TIMESTAMP AND verified_at IS NULL;
    GET DIAGNOSTICS temp_count = ROW_COUNT;
    deleted_count := deleted_count + temp_count;
    
    -- Clean password reset tokens
    DELETE FROM password_reset_tokens WHERE expires_at < CURRENT_TIMESTAMP AND used_at IS NULL;
    GET DIAGNOSTICS temp_count = ROW_COUNT;
    deleted_count := deleted_count + temp_count;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function: Revoke all user sessions
CREATE OR REPLACE FUNCTION revoke_all_user_sessions(p_user_id UUID)
RETURNS INTEGER AS $$
DECLARE
    revoked_count INTEGER;
BEGIN
    UPDATE token_families 
    SET is_revoked = TRUE 
    WHERE user_id = p_user_id AND is_revoked = FALSE;
    
    GET DIAGNOSTICS revoked_count = ROW_COUNT;
    RETURN revoked_count;
END;
$$ LANGUAGE plpgsql;

-- Function: Check if token is blacklisted
CREATE OR REPLACE FUNCTION is_token_blacklisted(p_jti VARCHAR(36))
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM token_blacklist 
        WHERE jti = p_jti AND expires_at > CURRENT_TIMESTAMP
    );
END;
$$ LANGUAGE plpgsql;

-- Function: Count failed login attempts (for rate limiting)
CREATE OR REPLACE FUNCTION count_failed_login_attempts(
    p_email VARCHAR(255),
    p_ip_address VARCHAR(45),
    p_window_minutes INTEGER DEFAULT 15
)
RETURNS INTEGER AS $$
DECLARE
    attempt_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO attempt_count
    FROM login_attempts
    WHERE (email = p_email OR ip_address = p_ip_address)
      AND is_successful = FALSE
      AND attempted_at > (CURRENT_TIMESTAMP - (p_window_minutes || ' minutes')::INTERVAL);
    
    RETURN attempt_count;
END;
$$ LANGUAGE plpgsql;

-- Function: Check if login is blocked
CREATE OR REPLACE FUNCTION is_login_blocked(
    p_email VARCHAR(255),
    p_ip_address VARCHAR(45),
    p_max_attempts INTEGER DEFAULT 5
)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN count_failed_login_attempts(p_email, p_ip_address) >= p_max_attempts;
END;
$$ LANGUAGE plpgsql;

-- Function: Get user permissions
CREATE OR REPLACE FUNCTION get_user_permissions(p_user_id UUID)
RETURNS TABLE(permission_code VARCHAR, permission_name VARCHAR, module VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT p.code, p.name, p.module
    FROM permissions p
    JOIN role_permissions rp ON p.id = rp.permission_id
    JOIN roles r ON r.id = rp.role_id
    JOIN users u ON u.role_id = r.id
    WHERE u.id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Check if user has permission
CREATE OR REPLACE FUNCTION user_has_permission(p_user_id UUID, p_permission_code VARCHAR)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM get_user_permissions(p_user_id) 
        WHERE permission_code = p_permission_code
    );
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 6. TRIGGERS
-- ============================================

-- Users: Auto-update updated_at
DROP TRIGGER IF EXISTS trigger_users_updated_at ON users;
CREATE TRIGGER trigger_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Roles: Auto-update updated_at
DROP TRIGGER IF EXISTS trigger_roles_updated_at ON roles;
CREATE TRIGGER trigger_roles_updated_at
    BEFORE UPDATE ON roles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Token Families: Auto-update last_used_at
DROP TRIGGER IF EXISTS trigger_token_families_last_used ON token_families;
CREATE TRIGGER trigger_token_families_last_used
    BEFORE UPDATE OF current_jti ON token_families
    FOR EACH ROW
    EXECUTE FUNCTION update_last_used_at_column();

-- User Devices: Auto-update updated_at
DROP TRIGGER IF EXISTS trigger_user_devices_updated_at ON user_devices;
CREATE TRIGGER trigger_user_devices_updated_at
    BEFORE UPDATE ON user_devices
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 7. DML - SEED DATA
-- ============================================

-- 7.1 Default Permissions
INSERT INTO permissions (name, code, description, module) VALUES
    -- User permissions
    ('View Profile', 'user:profile:read', 'View own profile', 'user'),
    ('Edit Profile', 'user:profile:write', 'Edit own profile', 'user'),
    ('Change Password', 'user:password:write', 'Change own password', 'user'),
    ('Manage Devices', 'user:devices:write', 'Manage own devices', 'user'),
    
    -- Admin permissions
    ('View All Users', 'admin:users:read', 'View all users', 'admin'),
    ('Create User', 'admin:users:create', 'Create new user', 'admin'),
    ('Edit User', 'admin:users:write', 'Edit any user', 'admin'),
    ('Delete User', 'admin:users:delete', 'Delete user', 'admin'),
    ('Manage Roles', 'admin:roles:write', 'Manage roles', 'admin'),
    ('View Logs', 'admin:logs:read', 'View system logs', 'admin'),
    
    -- System permissions
    ('Full Access', 'system:full_access', 'Full system access', 'system')
ON CONFLICT (code) DO NOTHING;

-- 7.2 Default Roles
INSERT INTO roles (name, code, description, is_default, is_system) VALUES
    ('User', 'user', 'Standard user role', TRUE, FALSE),
    ('Moderator', 'moderator', 'Moderator role', FALSE, FALSE),
    ('Admin', 'admin', 'Administrator role', FALSE, TRUE),
    ('Super Admin', 'super_admin', 'Super administrator with full access', FALSE, TRUE)
ON CONFLICT (code) DO NOTHING;

-- 7.3 Role-Permission Mappings
-- User role permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.code = 'user' AND p.code IN (
    'user:profile:read', 
    'user:profile:write', 
    'user:password:write', 
    'user:devices:write'
)
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- Admin role permissions (all admin + user permissions)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.code = 'admin' AND p.module IN ('user', 'admin')
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- Super Admin role permissions (all permissions)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.code = 'super_admin'
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- 7.4 Default Admin User (password: Admin@123)
INSERT INTO users (email, hashed_password, full_name, is_active, is_verified, role_id)
SELECT 
    'admin@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.GYQF9xqvGKwWWy',
    'System Admin',
    TRUE,
    TRUE,
    r.id
FROM roles r WHERE r.code = 'super_admin'
ON CONFLICT (email) DO NOTHING;

-- ============================================
-- 8. VIEWS
-- ============================================

-- View: Active sessions per user
CREATE OR REPLACE VIEW v_active_sessions AS
SELECT 
    u.id AS user_id,
    u.email,
    u.full_name,
    COUNT(tf.id) AS active_sessions,
    MAX(tf.last_used_at) AS last_activity
FROM users u
LEFT JOIN token_families tf ON u.id = tf.user_id 
    AND tf.is_revoked = FALSE 
    AND tf.expires_at > CURRENT_TIMESTAMP
GROUP BY u.id, u.email, u.full_name;

-- View: User with role and permissions count
CREATE OR REPLACE VIEW v_user_roles AS
SELECT 
    u.id,
    u.email,
    u.full_name,
    u.is_active,
    u.is_verified,
    r.name AS role_name,
    r.code AS role_code,
    (SELECT COUNT(*) FROM get_user_permissions(u.id)) AS permissions_count
FROM users u
LEFT JOIN roles r ON u.role_id = r.id;

-- View: Login attempts statistics
CREATE OR REPLACE VIEW v_login_stats AS
SELECT 
    date_trunc('hour', attempted_at) AS hour,
    COUNT(*) FILTER (WHERE is_successful = TRUE) AS successful,
    COUNT(*) FILTER (WHERE is_successful = FALSE) AS failed,
    COUNT(DISTINCT ip_address) AS unique_ips
FROM login_attempts
WHERE attempted_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY date_trunc('hour', attempted_at)
ORDER BY hour DESC;

-- View: Devices per user
CREATE OR REPLACE VIEW v_user_devices_summary AS
SELECT 
    u.id AS user_id,
    u.email,
    COUNT(ud.id) AS total_devices,
    COUNT(ud.id) FILTER (WHERE ud.status = 'active') AS active_devices,
    COUNT(ud.id) FILTER (WHERE ud.is_trusted = TRUE) AS trusted_devices
FROM users u
LEFT JOIN user_devices ud ON u.id = ud.user_id
GROUP BY u.id, u.email;

-- ============================================
-- 9. COMMENTS (Documentation)
-- ============================================

COMMENT ON TABLE users IS 'User accounts with authentication info';
COMMENT ON TABLE roles IS 'RBAC roles';
COMMENT ON TABLE permissions IS 'RBAC permissions';
COMMENT ON TABLE role_permissions IS 'Many-to-many mapping between roles and permissions';
COMMENT ON TABLE token_families IS 'Refresh token families for token rotation';
COMMENT ON TABLE token_blacklist IS 'Blacklisted tokens (revoked on logout)';
COMMENT ON TABLE user_devices IS 'Registered user devices for device management';
COMMENT ON TABLE login_attempts IS 'Login attempt tracking for security and rate limiting';
COMMENT ON TABLE email_verification_tokens IS 'Email verification tokens';
COMMENT ON TABLE password_reset_tokens IS 'Password reset tokens';

-- ============================================
-- END OF SCHEMA
-- ============================================
