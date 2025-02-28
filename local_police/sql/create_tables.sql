-- Agents table
CREATE TABLE IF NOT EXISTS Agents (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    nip VARCHAR(6) UNIQUE NOT NULL,
    section VARCHAR(255),
    group_name VARCHAR(255),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20)
);

-- Activities table
CREATE TABLE IF NOT EXISTS Activities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

-- ScheduledActivities table
CREATE TABLE IF NOT EXISTS ScheduledActivities (
    id SERIAL PRIMARY KEY,
    activity_id INTEGER REFERENCES Activities(id),
    date DATE NOT NULL,
    shift VARCHAR(255) NOT NULL,
    instructor_id INTEGER REFERENCES Agents(id), -- Assuming Agents table includes instructors
    max_capacity INTEGER DEFAULT 20,
    CONSTRAINT unique_scheduled_activity UNIQUE (activity_id, date, shift, instructor_id)
);

-- AgentAssignments table to track agents assigned to scheduled activities
CREATE TABLE IF NOT EXISTS AgentAssignments (
    id SERIAL PRIMARY KEY,
    scheduled_activity_id INTEGER REFERENCES ScheduledActivities(id),
    agent_id INTEGER REFERENCES Agents(id),
    CONSTRAINT unique_agent_assignment UNIQUE (scheduled_activity_id, agent_id)
);

-- Insert default activities
INSERT INTO Activities (name) VALUES
    ('Personal Defense')
ON CONFLICT (name) DO NOTHING;

INSERT INTO Activities (name) VALUES
    ('Physical Conditioning')
ON CONFLICT (name) DO NOTHING;
