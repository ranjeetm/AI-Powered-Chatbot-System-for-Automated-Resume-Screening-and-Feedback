import sqlite3
import pandas as pd
from datetime import datetime
import json
from pathlib import Path
import os

class ResumeDatabase:
    """SQLite database handler for resume screening application"""

    def __init__(self, db_path="resume_screening.db"):
        """Initialize database connection"""
        self.db_path = db_path
        # Ensure DB file directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        self.init_database()
        # Attempt lightweight migrations (add columns if missing)
        self._ensure_migrations()

    def init_database(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Candidates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                resume_text TEXT,
                resume_filename TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Screening results table (note: job_description_id may be added in migrations)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS screening_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER,
                job_description TEXT,
                match_score REAL,
                strengths TEXT,
                weaknesses TEXT,
                recommendations TEXT,
                screened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (candidate_id) REFERENCES candidates (id)
            )
        """)

        # Job descriptions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_descriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                requirements TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def _ensure_migrations(self):
        """
        Lightweight migration logic:
         - Add job_description_id column to screening_results if missing
         - Keep existing job_description (text) for backward compatibility
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # check columns in screening_results
        cursor.execute("PRAGMA table_info(screening_results);")
        cols = [row[1] for row in cursor.fetchall()]
        if 'job_description_id' not in cols:
            try:
                cursor.execute("ALTER TABLE screening_results ADD COLUMN job_description_id INTEGER;")
                conn.commit()
            except Exception:
                # If ALTER fails for any reason (rare), ignore and continue to preserve data
                pass

        conn.close()

    # ---------------------
    # Job descriptions CRUD
    # ---------------------
    def add_job_description(self, title, description, requirements=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO job_descriptions (title, description, requirements)
            VALUES (?, ?, ?)
        """, (title, description, requirements))
        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return job_id

    def get_job_descriptions(self):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM job_descriptions ORDER BY created_at DESC", conn)
        conn.close()
        return df

    def get_job_description_by_id(self, job_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM job_descriptions WHERE id = ?", (job_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        columns = ['id', 'title', 'description', 'requirements', 'created_at']
        return dict(zip(columns, row))

    def update_job_description(self, job_id, title=None, description=None, requirements=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Build dynamic update
        updates = []
        params = []
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if requirements is not None:
            updates.append("requirements = ?")
            params.append(requirements)
        params.append(job_id)
        if updates:
            query = f"UPDATE job_descriptions SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
        conn.close()

    def delete_job_description(self, job_id):
        """
        Delete a job posting. Note: previous screening_results keep their job_description text,
        but will have job_description_id set to NULL. If desired, you can cascade-delete results,
        but we leave results intact.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM job_descriptions WHERE id = ?", (job_id,))
        # Optionally set job_description_id to NULL for existing results
        cursor.execute("UPDATE screening_results SET job_description_id = NULL WHERE job_description_id = ?", (job_id,))
        conn.commit()
        conn.close()

    # ---------------------
    # Candidate & Results
    # ---------------------
    def add_candidate(self, name, resume_text, resume_filename, email=None, phone=None):
        """Add a new candidate to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO candidates (name, email, phone, resume_text, resume_filename)
                VALUES (?, ?, ?, ?, ?)
            """, (name, email, phone, resume_text, resume_filename))

            candidate_id = cursor.lastrowid
            conn.commit()
            return candidate_id
        except sqlite3.IntegrityError as e:
            print(f"Error: {e}")
            return None
        finally:
            conn.close()

    def add_screening_result(self, candidate_id, job_description, match_score,
                             strengths=None, weaknesses=None, recommendations=None,
                             job_description_id=None):
        """Add screening results for a candidate"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Convert lists to JSON strings for storage
        strengths_json = json.dumps(strengths) if strengths else None
        weaknesses_json = json.dumps(weaknesses) if weaknesses else None
        recommendations_json = json.dumps(recommendations) if recommendations else None

        cursor.execute("""
            INSERT INTO screening_results 
            (candidate_id, job_description, match_score, strengths, weaknesses, recommendations, job_description_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (candidate_id, job_description, match_score,
              strengths_json, weaknesses_json, recommendations_json, job_description_id))

        conn.commit()
        conn.close()

    def get_all_candidates(self):
        """Retrieve all candidates"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM candidates ORDER BY uploaded_at DESC", conn)
        conn.close()
        return df

    def get_candidate_by_id(self, candidate_id):
        """Get specific candidate details"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            columns = ['id', 'name', 'email', 'phone', 'resume_text',
                       'resume_filename', 'uploaded_at']
            return dict(zip(columns, result))
        return None

    def get_screening_results(self, candidate_id=None, job_id=None):
        """Get screening results, optionally filtered by candidate or job"""
        conn = sqlite3.connect(self.db_path)

        if candidate_id:
            query = """
                SELECT sr.*, c.name, c.email, jd.title as job_title, sr.job_description_id
                FROM screening_results sr
                JOIN candidates c ON sr.candidate_id = c.id
                LEFT JOIN job_descriptions jd ON sr.job_description_id = jd.id
                WHERE sr.candidate_id = ?
                ORDER BY sr.screened_at DESC
            """
            df = pd.read_sql_query(query, conn, params=(candidate_id,))
        else:
            if job_id:
                query = """
                    SELECT sr.*, c.name, c.email, jd.title as job_title, sr.job_description_id
                    FROM screening_results sr
                    JOIN candidates c ON sr.candidate_id = c.id
                    LEFT JOIN job_descriptions jd ON sr.job_description_id = jd.id
                    WHERE sr.job_description_id = ?
                    ORDER BY sr.screened_at DESC
                """
                df = pd.read_sql_query(query, conn, params=(job_id,))
            else:
                query = """
                    SELECT sr.*, c.name, c.email, jd.title as job_title, sr.job_description_id
                    FROM screening_results sr
                    JOIN candidates c ON sr.candidate_id = c.id
                    LEFT JOIN job_descriptions jd ON sr.job_description_id = jd.id
                    ORDER BY sr.screened_at DESC
                """
                df = pd.read_sql_query(query, conn)

        conn.close()

        # Parse JSON columns back to lists
        if not df.empty:
            for col in ['strengths', 'weaknesses', 'recommendations']:
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: json.loads(x) if x else [])

        return df

    def get_top_candidates(self, limit=10):
        """Get top candidates by match score"""
        conn = sqlite3.connect(self.db_path)

        query = """
            SELECT c.id, c.name, c.email, 
                   MAX(sr.match_score) as best_score,
                   c.uploaded_at
            FROM candidates c
            JOIN screening_results sr ON c.id = sr.candidate_id
            GROUP BY c.id
            ORDER BY best_score DESC
            LIMIT ?
        """

        df = pd.read_sql_query(query, conn, params=(limit,))
        conn.close()
        return df

    def search_candidates(self, search_term):
        """Search candidates by name or email"""
        conn = sqlite3.connect(self.db_path)

        query = """
            SELECT * FROM candidates 
            WHERE name LIKE ? OR email LIKE ?
            ORDER BY uploaded_at DESC
        """

        search_pattern = f"%{search_term}%"
        df = pd.read_sql_query(query, conn, params=(search_pattern, search_pattern))
        conn.close()
        return df

    def delete_candidate(self, candidate_id):
        """Delete a candidate and their screening results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Delete screening results first (foreign key constraint)
        cursor.execute("DELETE FROM screening_results WHERE candidate_id = ?",
                       (candidate_id,))
        cursor.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))

        conn.commit()
        conn.close()

    def get_statistics(self):
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        # Total candidates
        cursor.execute("SELECT COUNT(*) FROM candidates")
        stats['total_candidates'] = cursor.fetchone()[0]

        # Total screenings
        cursor.execute("SELECT COUNT(*) FROM screening_results")
        stats['total_screenings'] = cursor.fetchone()[0]

        # Average score
        cursor.execute("SELECT AVG(match_score) FROM screening_results")
        avg_score = cursor.fetchone()[0]
        stats['avg_score'] = round(avg_score, 2) if avg_score else 0

        # Top score
        cursor.execute("SELECT MAX(match_score) FROM screening_results")
        top_score = cursor.fetchone()[0]
        stats['top_score'] = round(top_score, 2) if top_score else 0

        # Qualified candidates (score >= 70)
        cursor.execute("SELECT COUNT(DISTINCT candidate_id) FROM screening_results WHERE match_score >= 70")
        stats['qualified_candidates'] = cursor.fetchone()[0]

        conn.close()
        return stats

    def export_to_csv(self, output_path="resume_data_export.csv"):
        """Export all data to CSV"""
        conn = sqlite3.connect(self.db_path)

        query = """
            SELECT 
                c.name,
                c.email,
                c.phone,
                c.resume_filename,
                sr.match_score,
                jd.title as job_title,
                sr.screened_at,
                c.uploaded_at
            FROM candidates c
            LEFT JOIN screening_results sr ON c.id = sr.candidate_id
            LEFT JOIN job_descriptions jd ON sr.job_description_id = jd.id
            ORDER BY c.uploaded_at DESC
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        df.to_csv(output_path, index=False)
        return output_path

    def clear_all_data(self):
        """Clear all data from database (use with caution!)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM screening_results")
        cursor.execute("DELETE FROM candidates")
        cursor.execute("DELETE FROM job_descriptions")

        conn.commit()
        conn.close()

    def backup_database(self, backup_path=None):
        """Create a backup of the database"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"resume_screening_backup_{timestamp}.db"

        import shutil
        shutil.copy2(self.db_path, backup_path)
        return backup_path


# Example usage functions
def example_usage():
    """Example of how to use the database"""

    # Initialize database
    db = ResumeDatabase()

    # Add a candidate
    candidate_id = db.add_candidate(
        name="John Doe",
        email="john@example.com",
        phone="123-456-7890",
        resume_text="Experienced software engineer...",
        resume_filename="john_doe_resume.pdf"
    )

    # Add screening result
    db.add_screening_result(
        candidate_id=candidate_id,
        job_description="Looking for Python developer...",
        match_score=85.5,
        strengths=["Python", "Machine Learning", "5 years experience"],
        weaknesses=["No cloud experience"],
        recommendations=["Consider for senior role", "Interview ASAP"]
    )

    # Retrieve data
    all_candidates = db.get_all_candidates()
    print(f"Total candidates: {len(all_candidates)}")

    # Get statistics
    stats = db.get_statistics()
    print(f"Statistics: {stats}")

    # Export data
    db.export_to_csv()

    # Backup database
    backup_file = db.backup_database()
    print(f"Backup created: {backup_file}")
