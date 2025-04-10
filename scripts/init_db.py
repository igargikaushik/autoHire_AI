import sqlite3

DATABASE = 'database.db'

def init_db():
    create_users_table()
    insert_sample_users()   
    create_jobs_table()
    insert_sample_jobs()    
    create_applications_table()
    print("Database initialized.")

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_users_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            user_type TEXT NOT NULL CHECK (user_type IN ('company', 'applicant'))
        )
    ''')
    conn.commit()
    conn.close()

def insert_sample_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE user_type = 'company'")
    if cursor.fetchone()[0] == 0:
        sample_companies = [
            ('technova', 'securepwd1', 'hr@technova.com', 'company'),
            ('innosoft', 'securepwd2', 'jobs@innosoft.com', 'company')
        ]
        cursor.executemany('''
            INSERT INTO users (username, password, email, user_type)
            VALUES (?, ?, ?, ?)
        ''', sample_companies)
        print(" Sample companies inserted.")
    conn.commit()
    conn.close()

def create_jobs_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS jobs')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            job_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            requirements TEXT NOT NULL,
            location TEXT NOT NULL,
            job_type TEXT NOT NULL,
            salary REAL,
            posted_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            company_id INTEGER NOT NULL,
            FOREIGN KEY (company_id) REFERENCES users (user_id)
        )
    ''')
    conn.commit()
    conn.close()

def insert_sample_jobs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE username = 'technova'")
    row = cursor.fetchone()
    if row:
        company_id = row['user_id']
        sample_jobs = [
            (
                'Software Engineer',
                'Build scalable backend services.',
                'Python, SQL, REST APIs',
                'Remote',
                'Full-time',
                80000.0,
                company_id
            )
        ]
        cursor.executemany('''
            INSERT INTO jobs (title, description, requirements, location, job_type, salary, company_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_jobs)
        print(" Sample jobs inserted for technova.")
    conn.commit()
    conn.close()

def create_applications_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS applications (
        application_id INTEGER PRIMARY KEY AUTOINCREMENT,
        applicant_id INTEGER NOT NULL,
        job_id INTEGER NOT NULL,
        resume_path TEXT NOT NULL,
        resume_summary TEXT,
        applied_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'applied' CHECK (status IN ('applied', 'shortlisted', 'not shortlisted')),
        prediction_score REAL,
        interview_scheduled BOOLEAN DEFAULT 0,
        interview_datetime TEXT,
        FOREIGN KEY (applicant_id) REFERENCES users (user_id),
        FOREIGN KEY (job_id) REFERENCES jobs (job_id)
    )
''')
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
