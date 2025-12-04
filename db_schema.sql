-- ============================================
-- AI-Powered Conversational Diary Database Schema
-- ============================================

-- Drop tables if exist (for clean setup)
DROP TABLE IF EXISTS journals CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================
-- 1. USERS TABLE
-- ============================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    timezone VARCHAR(50) NOT NULL DEFAULT 'America/New_York',
    preferred_call_time TIME NOT NULL DEFAULT '20:00:00',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Index for phone lookup (used during incoming calls)
CREATE INDEX idx_users_phone_number ON users(phone_number);

-- ============================================
-- 2. CONVERSATIONS TABLE (Temporary, 7-30 days retention)
-- ============================================
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    status VARCHAR(20) NOT NULL DEFAULT 'in_progress' 
        CHECK (status IN ('in_progress', 'completed', 'failed', 'interrupted')),
    raw_transcript JSONB,  -- Full chat history, temporary storage
    twilio_call_sid VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Index for user lookup and cleanup job
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);
CREATE INDEX idx_conversations_status ON conversations(status);

-- ============================================
-- 3. JOURNALS TABLE (Permanent storage)
-- ============================================
CREATE TABLE journals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    duration_seconds INTEGER,
    topics JSONB DEFAULT '[]',  -- e.g., ["stress", "work", "sleep"]
    detected_emotions JSONB DEFAULT '{}',  -- e.g., {"anxiety": 0.7, "sadness": 0.3}
    markdown_file_path VARCHAR(255) NOT NULL,
    vector_embedding_id VARCHAR(100),  -- Reference to Pinecone/Qdrant
    summary_text TEXT,  -- Optional: store summary text for quick access
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX idx_journals_user_id ON journals(user_id);
CREATE INDEX idx_journals_created_at ON journals(created_at);
CREATE INDEX idx_journals_topics ON journals USING GIN(topics);
CREATE INDEX idx_journals_detected_emotions ON journals USING GIN(detected_emotions);

-- ============================================
-- MOCK DATA INSERTS
-- ============================================

-- Insert mock users
INSERT INTO users (phone_number, timezone, preferred_call_time, is_active) VALUES
('+1234567890', 'America/New_York', '20:00:00', TRUE),
('+1987654321', 'America/Los_Angeles', '21:00:00', TRUE),
('+1555123456', 'America/Chicago', '19:30:00', TRUE),
('+1555987654', 'Europe/London', '22:00:00', FALSE);

-- Insert mock conversations
INSERT INTO conversations (user_id, started_at, ended_at, duration_seconds, status, raw_transcript, twilio_call_sid) VALUES
(
    1,
    '2025-01-15 20:00:00-05',
    '2025-01-15 20:12:30-05',
    750,
    'completed',
    '[
        {"role": "assistant", "content": "Hi Sarah! How was your day today?", "timestamp": "2025-01-15T20:00:05"},
        {"role": "user", "content": "Hey! It was pretty stressful actually. I had a big presentation at work.", "timestamp": "2025-01-15T20:00:15"},
        {"role": "assistant", "content": "I hear you. Presentations can be nerve-wracking. How did it go?", "timestamp": "2025-01-15T20:00:25"},
        {"role": "user", "content": "Better than expected! My manager said I did a great job.", "timestamp": "2025-01-15T20:00:40"},
        {"role": "assistant", "content": "That''s wonderful news! How are you feeling now that it''s over?", "timestamp": "2025-01-15T20:00:50"},
        {"role": "user", "content": "Relieved, but also tired. I didn''t sleep well last night because I was anxious.", "timestamp": "2025-01-15T20:01:05"}
    ]'::jsonb,
    'CA1234567890abcdef'
),
(
    1,
    '2025-01-16 20:00:00-05',
    '2025-01-16 20:08:45-05',
    525,
    'completed',
    '[
        {"role": "assistant", "content": "Good evening Sarah! Last time you mentioned feeling tired after your presentation. How are you doing today?", "timestamp": "2025-01-16T20:00:05"},
        {"role": "user", "content": "Much better! I finally got a good night''s sleep.", "timestamp": "2025-01-16T20:00:18"},
        {"role": "assistant", "content": "That''s great to hear. Sleep makes such a difference. Anything on your mind tonight?", "timestamp": "2025-01-16T20:00:28"},
        {"role": "user", "content": "I''ve been thinking about work-life balance. I feel like I''ve been neglecting my hobbies.", "timestamp": "2025-01-16T20:00:45"}
    ]'::jsonb,
    'CA2345678901bcdefg'
),
(
    2,
    '2025-01-16 21:00:00-08',
    '2025-01-16 21:15:20-08',
    920,
    'completed',
    '[
        {"role": "assistant", "content": "Hi Mike! How''s everything going?", "timestamp": "2025-01-16T21:00:05"},
        {"role": "user", "content": "Not great honestly. I''ve been feeling overwhelmed with my CS6180 assignment.", "timestamp": "2025-01-16T21:00:20"},
        {"role": "assistant", "content": "I understand. What part of the assignment is giving you trouble?", "timestamp": "2025-01-16T21:00:32"},
        {"role": "user", "content": "The transformer architecture. I keep getting confused about self-attention.", "timestamp": "2025-01-16T21:00:50"}
    ]'::jsonb,
    'CA3456789012cdefgh'
),
(
    1,
    '2025-01-17 20:00:00-05',
    NULL,
    NULL,
    'failed',
    NULL,
    'CA4567890123defghi'
),
(
    3,
    '2025-01-17 19:30:00-06',
    '2025-01-17 19:41:00-06',
    660,
    'completed',
    '[
        {"role": "assistant", "content": "Hello! How are you feeling this evening?", "timestamp": "2025-01-17T19:30:05"},
        {"role": "user", "content": "Pretty good! I went for a run today and it really helped clear my head.", "timestamp": "2025-01-17T19:30:18"},
        {"role": "assistant", "content": "Exercise is wonderful for mental clarity. What were you thinking about during your run?", "timestamp": "2025-01-17T19:30:30"},
        {"role": "user", "content": "Mostly about my goals for this year. I want to be more consistent with self-care.", "timestamp": "2025-01-17T19:30:48"}
    ]'::jsonb,
    'CA5678901234efghij'
);

-- Insert mock journals
INSERT INTO journals (user_id, conversation_id, created_at, duration_seconds, topics, detected_emotions, markdown_file_path, vector_embedding_id, summary_text) VALUES
(
    1,
    1,
    '2025-01-15 20:12:30-05',
    750,
    '["work", "presentation", "stress", "sleep", "anxiety"]'::jsonb,
    '{"anxiety": 0.65, "relief": 0.72, "tiredness": 0.58, "pride": 0.45}'::jsonb,
    '/journals/2025-01-15/journal_user1_abc123.md',
    'vec_emb_001',
    'Sarah had a stressful day due to a work presentation but it went better than expected. Her manager praised her performance. She felt relieved but tired due to poor sleep from pre-presentation anxiety.'
),
(
    1,
    2,
    '2025-01-16 20:08:45-05',
    525,
    '["sleep", "work-life-balance", "hobbies", "self-reflection"]'::jsonb,
    '{"contentment": 0.70, "contemplative": 0.55, "mild_concern": 0.30}'::jsonb,
    '/journals/2025-01-16/journal_user1_def456.md',
    'vec_emb_002',
    'Sarah reported feeling much better after getting good sleep. She reflected on work-life balance and expressed concern about neglecting her hobbies.'
),
(
    2,
    3,
    '2025-01-16 21:15:20-08',
    920,
    '["academics", "CS6180", "transformers", "self-attention", "overwhelm"]'::jsonb,
    '{"stress": 0.75, "frustration": 0.60, "confusion": 0.68}'::jsonb,
    '/journals/2025-01-16/journal_user2_ghi789.md',
    'vec_emb_003',
    'Mike is feeling overwhelmed with his CS6180 Generative AI assignment. Specifically struggling to understand transformer architecture and self-attention mechanisms.'
),
(
    3,
    5,
    '2025-01-17 19:41:00-06',
    660,
    '["exercise", "running", "self-care", "goals", "mental-clarity"]'::jsonb,
    '{"positive": 0.82, "motivated": 0.75, "hopeful": 0.70}'::jsonb,
    '/journals/2025-01-17/journal_user3_jkl012.md',
    'vec_emb_004',
    'User went for a run which helped with mental clarity. Reflected on yearly goals with a focus on being more consistent with self-care practices.'
);

-- ============================================
-- USEFUL QUERIES FOR VERIFICATION
-- ============================================

-- View all users
-- SELECT * FROM users;

-- View all conversations with user info
-- SELECT c.*, u.phone_number 
-- FROM conversations c 
-- JOIN users u ON c.user_id = u.id;

-- View all journals with user info
-- SELECT j.*, u.phone_number 
-- FROM journals j 
-- JOIN users u ON j.user_id = u.id;

-- Find journals by topic
-- SELECT * FROM journals WHERE topics ? 'stress';

-- Find journals with high anxiety
-- SELECT * FROM journals 
-- WHERE (detected_emotions->>'anxiety')::float > 0.5;

-- Cleanup old conversations (example: older than 30 days)
-- DELETE FROM conversations 
-- WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '30 days';
