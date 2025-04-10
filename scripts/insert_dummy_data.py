import sqlite3

DATABASE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def insert_dummy_company():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if company user already exists
    cursor.execute("SELECT user_id FROM users WHERE username = ?", ('test_company',))
    company = cursor.fetchone()

    if company:
        print("Dummy company already exists.")
        return company['user_id']
    else:
        cursor.execute('''
            INSERT INTO users (username, password, email, user_type)
            VALUES (?, ?, ?, ?)
        ''', ('test_company', 'hashed_password', 'test@company.com', 'company'))

        conn.commit()
        company_id = cursor.lastrowid
        print(f"Inserted dummy company with user_id: {company_id}")
        return company_id

def insert_dummy_job(company_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO jobs (title, description, requirements, location, job_type, salary, company_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        'Data Scientist',
        'Responsible for analyzing large datasets to extract actionable insights.',
        'Python, SQL, Machine Learning',
        'Remote',
        'Full-time',
        95000,
        company_id
    ))

    conn.commit()
    job_id = cursor.lastrowid
    print(f"Inserted dummy job with job_id: {job_id}")
    conn.close()

if __name__ == '__main__':
    company_id = insert_dummy_company()
    insert_dummy_job(company_id)
