from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import sqlite3
import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE = 'database.db'
UPLOAD_FOLDER = 'uploads'  # Folder to store uploaded resumes
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}  # Allowed file extensions

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

from flask import session


def get_db_connection():
    """Gets a database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_users_table():
    """Creates the 'users' table in the database."""
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
    print("Users table created (or already exists).")


def create_jobs_table():
    """Creates the 'jobs' table in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

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
    print("Jobs table created (or already exists).")


def create_applications_table():
    """Creates the 'applications' table in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            application_id INTEGER PRIMARY KEY AUTOINCREMENT,
            applicant_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            resume_path TEXT NOT NULL,
            applied_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'applied' CHECK (status IN ('applied', 'shortlisted', 'not shortlisted')),
            prediction_score REAL,
            FOREIGN KEY (applicant_id) REFERENCES users (user_id),
            FOREIGN KEY (job_id) REFERENCES jobs (job_id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Applications table created (or already exists).")


# Create the tables
create_users_table()
create_jobs_table()
create_applications_table()


def allowed_file(filename):
    """Checks if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

now = datetime.datetime.now() # Pass current time to the templates

@app.route('/')
def index():
    """Home page."""
    return render_template('index.html', now=now)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        user_type = request.form['user_type']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password, email, user_type) VALUES (?, ?, ?, ?)",
                (username, password, email, user_type),
            )
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists.', 'danger')
            return render_template('register.html')
        finally:
            conn.close()

    return render_template('register.html', now=now)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'POST':
        user_type = request.form.get('userType')

        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?', (username, password)
        ).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['user_id']
            session['username'] = user['username']  # Store username in session
            session['user_type'] = user['user_type']
            flash('Login successful!', 'success')
            if user['user_type'] == 'company':
                session['company_name'] = request.form.get('company_name')  # Store company name

                return redirect(url_for('company_dashboard'))
            else:
                return redirect(url_for('applicant_dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html', now=now)


@app.route('/logout')
def logout():
    """Logout route."""
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))



@app.route('/company_dashboard')
def company_dashboard():
    """Company dashboard page."""
    if 'user_id' not in session or session['user_type'] != 'company':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()
    company_id = session['user_id']

    # Get company name from session (ensure it's set during login/registration)

    # Get jobs posted by the company
    jobs = cursor.execute('SELECT * FROM jobs WHERE company_id = ?', (company_id,)).fetchall()

    # Get total applications for the company's jobs
    total_applications = cursor.execute(
        '''SELECT COUNT(applications.application_id) 
           FROM applications 
           JOIN jobs ON applications.job_id = jobs.job_id 
           WHERE jobs.company_id = ?''',
        (company_id,),
    ).fetchone()[0] or 0

    #get shortlisted applications
    shortlisted_applications = cursor.execute('''
        SELECT applications.*, users.username, users.email, jobs.title
        FROM applications
        JOIN users ON applications.applicant_id = users.user_id
        JOIN jobs ON applications.job_id = jobs.job_id
        WHERE applications.status = 'shortlisted'
        AND jobs.company_id = ?
    ''', (company_id,)).fetchall()

    conn.close()
    return render_template(
        'company_dashboard.html',
        company_name=session['company_name'],

        jobs=jobs,
        total_applications=total_applications,
        shortlisted_applications=shortlisted_applications,
        now=now
    )

    
    


@app.route('/applicant_dashboard')
def applicant_dashboard():
    """Applicant dashboard page."""
    if 'user_id' not in session or session['user_type'] != 'applicant':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()
    applicant_id = session['user_id']

    # Get applications by the applicant
    applications = cursor.execute(
        '''SELECT applications.*, jobs.title
           FROM applications 
           JOIN jobs ON applications.job_id = jobs.job_id
           WHERE applications.applicant_id = ?''',
        (applicant_id,),
    ).fetchall()

    # Get all jobs
    jobs = cursor.execute('SELECT jobs.*, users.username as company_name FROM jobs JOIN users ON jobs.company_id = users.user_id').fetchall()
    conn.close()
    return render_template('applicant_dashboard.html', applications=applications, jobs=jobs, now=now)


@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    """Post a new job page."""
    if 'user_id' not in session or session['user_type'] != 'company':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        requirements = request.form['requirements']
        location = request.form['location']
        job_type = request.form['job_type']
        salary = request.form['salary']
        company_id = session['user_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''INSERT INTO jobs (title, description, requirements, location, job_type, salary, company_id) 
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (title, description, requirements, location, job_type, salary, company_id),
        )
        conn.commit()
        conn.close()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('company_dashboard'))

    return render_template('post_job.html', now=now)



@app.route('/job_listings')
def job_listings():
    """Job listings page for companies."""
    if 'user_id' not in session or session['user_type'] != 'company':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()
    company_id = session['user_id']

    # Fetch jobs posted by the logged-in company
    jobs = cursor.execute(
        '''SELECT jobs.*, COUNT(applications.application_id) as applications
           FROM jobs
           LEFT JOIN applications ON jobs.job_id = applications.job_id
           WHERE jobs.company_id = ?
           GROUP BY jobs.job_id''',
        (company_id,),
    ).fetchall()
    conn.close()
    return render_template('job_listings.html', jobs=jobs, now=now)


@app.route('/job_details/<int:job_id>')
def job_details(job_id):
    """Job details page."""
    conn = get_db_connection()
    cursor = conn.cursor()

    job = cursor.execute(
        '''SELECT jobs.*, users.username as company_name
           FROM jobs
           JOIN users ON jobs.company_id = users.user_id
           WHERE jobs.job_id = ?''',
        (job_id,),
    ).fetchone()

    if not job:
        flash('Job not found.', 'danger')
        return redirect(url_for('index'))
    
    if session.get('user_type') == 'applicant':
        return render_template('job_details.html', job=job)
    elif session.get('user_type') == 'company':
        return render_template('job_details.html', job=job)
    else:
        return render_template('job_details.html', job=job, now=now)


@app.route('/apply_job/<int:job_id>', methods=['GET', 'POST'])
def apply_job(job_id):
    """Apply for a job page."""
    if 'user_id' not in session or session['user_type'] != 'applicant':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()
    applicant_id = session['user_id']

    # Check if the applicant has already applied for this job
    application = cursor.execute(
        'SELECT * FROM applications WHERE applicant_id = ? AND job_id = ?',
        (applicant_id, job_id),
    ).fetchone()

    if application:
        # Fetch the application status
        application_status = application['status']
        conn.close()
        return render_template('apply_job.html', job=application, application_status=application_status)


    job = cursor.execute('SELECT * FROM jobs WHERE job_id = ?', (job_id,)).fetchone()
    if not job:
        flash('Job not found.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No resume uploaded.', 'danger')
            return render_template('apply_job.html', job=job)
        resume = request.files['resume']
        if resume.filename == '':
            flash('No resume selected.', 'danger')
            return render_template('apply_job.html', job=job)
        if resume and allowed_file(resume.filename):
            filename = secure_filename(resume.filename)
            resume_path = os.path.join(UPLOAD_FOLDER, filename)
            resume.save(resume_path)

            cursor.execute(
                'INSERT INTO applications (applicant_id, job_id, resume_path) VALUES (?, ?, ?)',
                (applicant_id, job_id, resume_path),
            )
            conn.commit()
            conn.close()
            flash('Application submitted successfully!', 'success')
            return redirect(url_for('applicant_dashboard'))
        else:
            flash('Invalid file type. Please upload a PDF, DOC, or DOCX file.', 'danger')
            return render_template('apply_job.html', job=job)

    return render_template('apply_job.html', job=job)



@app.route('/shortlisting/<int:job_id>', methods=['GET', 'POST'])
def shortlisting(job_id):
    """Shortlisting page for companies to view applications for a job."""
    if 'user_id' not in session or session['user_type'] != 'company':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()
    company_id = session['user_id']

    # Ensure the job belongs to the logged-in company
    job = cursor.execute('SELECT * FROM jobs WHERE job_id = ? AND company_id = ?', (job_id, company_id)).fetchone()
    if not job:
        flash('Job not found or does not belong to your company.', 'danger')
        return redirect(url_for('job_listings'))

    if request.method == 'POST':
        applicant_id = request.form['applicant_id']
        #check the current status.
        application_status = cursor.execute('SELECT status from applications where job_id = ? AND applicant_id = ?', (job_id, applicant_id)).fetchone()[0]
        if application_status == 'applied':
            cursor.execute(
                'UPDATE applications SET status = "shortlisted" WHERE job_id = ? AND applicant_id = ?',
                (job_id, applicant_id),
            )
            conn.commit()
            flash('Applicant shortlisted.', 'success')
        elif application_status == 'shortlisted':
            cursor.execute(
                'UPDATE applications SET status = "not shortlisted" WHERE job_id = ? AND applicant_id = ?',
                (job_id, applicant_id),
            )
            conn.commit()
            flash('Applicant Not Shortlisted.', 'success')
        else:
            flash('Applicant already shortlisted or not shortlisted.', 'warning')

        return redirect(url_for('shortlisting', job_id=job_id))

    applications = cursor.execute(
        '''SELECT applications.*, users.username, users.email
           FROM applications
           JOIN users ON applications.applicant_id = users.user_id
           WHERE applications.job_id = ?''',
        (job_id,),
    ).fetchall()
    conn.close()
    return render_template('shortlisting.html', job=job, applications=applications)


if __name__ == '__main__':
    app.run(debug=True)

