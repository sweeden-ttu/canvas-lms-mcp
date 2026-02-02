-- PostgreSQL Database Schema for Canvas LMS MCP Data
-- This schema synchronizes with YAML data files in the _data directory
-- Designed to support relational database structure with minimum 4 columns per table

-- Navigation data (from nav.yml)
CREATE TABLE IF NOT EXISTS navigation (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    order_index INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Course modules (from syllabus_modules.yml)
CREATE TABLE IF NOT EXISTS course_modules (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    folder VARCHAR(255) NOT NULL,
    weeks VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Module topics (from syllabus_modules.yml - topics array)
CREATE TABLE IF NOT EXISTS module_topics (
    id SERIAL PRIMARY KEY,
    module_id INTEGER NOT NULL REFERENCES course_modules(id) ON DELETE CASCADE,
    topic_text TEXT NOT NULL,
    order_index INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Courses (for Canvas course data)
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY,  -- Canvas course ID (positive) or negative ID for unsynced
    name VARCHAR(255) NOT NULL,
    account_id INTEGER NOT NULL,
    term VARCHAR(100),
    status VARCHAR(50) NOT NULL,
    start_date DATE,
    end_date DATE,
    enrollment_count INTEGER DEFAULT 0,
    canvas_id INTEGER,  -- NULL until synced, then Canvas-assigned ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT courses_min_columns CHECK (
        id IS NOT NULL AND
        name IS NOT NULL AND
        account_id IS NOT NULL AND
        status IS NOT NULL
    )
);

-- Assignments (for Canvas assignment data)
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY,  -- Negative ID for unsynced, positive for synced
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    due_date DATE,
    points INTEGER,
    assignment_type VARCHAR(100),
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    canvas_id INTEGER,  -- NULL until synced, then Canvas-assigned ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT assignments_min_columns CHECK (
        id IS NOT NULL AND
        course_id IS NOT NULL AND
        name IS NOT NULL AND
        status IS NOT NULL
    )
);

-- Students/Users (for Canvas user data)
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,  -- Canvas user ID
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    login_id VARCHAR(255),
    sis_user_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT students_min_columns CHECK (
        id IS NOT NULL AND
        name IS NOT NULL AND
        email IS NOT NULL AND
        created_at IS NOT NULL
    )
);

-- Enrollments (relationship between students and courses)
CREATE TABLE IF NOT EXISTS enrollments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    enrollment_type VARCHAR(50) NOT NULL,
    enrollment_status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, course_id),
    CONSTRAINT enrollments_min_columns CHECK (
        id IS NOT NULL AND
        student_id IS NOT NULL AND
        course_id IS NOT NULL AND
        enrollment_type IS NOT NULL
    )
);

-- Submissions (for assignment submissions)
CREATE TABLE IF NOT EXISTS submissions (
    id SERIAL PRIMARY KEY,
    assignment_id INTEGER NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    submitted_at TIMESTAMP,
    score DECIMAL(10, 2),
    grade VARCHAR(10),
    workflow_state VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT submissions_min_columns CHECK (
        id IS NOT NULL AND
        assignment_id IS NOT NULL AND
        student_id IS NOT NULL AND
        submitted_at IS NOT NULL
    )
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_courses_account_id ON courses(account_id);
CREATE INDEX IF NOT EXISTS idx_courses_canvas_id ON courses(canvas_id);
CREATE INDEX IF NOT EXISTS idx_assignments_course_id ON assignments(course_id);
CREATE INDEX IF NOT EXISTS idx_assignments_canvas_id ON assignments(canvas_id);
CREATE INDEX IF NOT EXISTS idx_module_topics_module_id ON module_topics(module_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course_id ON enrollments(course_id);
CREATE INDEX IF NOT EXISTS idx_submissions_assignment_id ON submissions(assignment_id);
CREATE INDEX IF NOT EXISTS idx_submissions_student_id ON submissions(student_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to auto-update updated_at
CREATE TRIGGER update_navigation_updated_at BEFORE UPDATE ON navigation
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_course_modules_updated_at BEFORE UPDATE ON course_modules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_module_topics_updated_at BEFORE UPDATE ON module_topics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_courses_updated_at BEFORE UPDATE ON courses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_assignments_updated_at BEFORE UPDATE ON assignments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_students_updated_at BEFORE UPDATE ON students
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_enrollments_updated_at BEFORE UPDATE ON enrollments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_submissions_updated_at BEFORE UPDATE ON submissions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE navigation IS 'Navigation menu items synchronized from _data/nav.yml';
COMMENT ON TABLE course_modules IS 'Course modules synchronized from _data/syllabus_modules.yml';
COMMENT ON TABLE module_topics IS 'Topics within course modules from _data/syllabus_modules.yml';
COMMENT ON TABLE courses IS 'Canvas courses with Canvas IDs or negative IDs for unsynced items';
COMMENT ON TABLE assignments IS 'Canvas assignments with Canvas IDs or negative IDs for unsynced items';
COMMENT ON TABLE students IS 'Canvas users/students';
COMMENT ON TABLE enrollments IS 'Student enrollments in courses';
COMMENT ON TABLE submissions IS 'Assignment submissions by students';

COMMENT ON COLUMN courses.id IS 'Canvas course ID (positive) or negative ID for unsynced items';
COMMENT ON COLUMN courses.canvas_id IS 'Canvas-assigned ID after synchronization, NULL for unsynced';
COMMENT ON COLUMN assignments.id IS 'Negative ID for unsynced items, positive for synced';
COMMENT ON COLUMN assignments.canvas_id IS 'Canvas-assigned ID after synchronization, NULL for unsynced';