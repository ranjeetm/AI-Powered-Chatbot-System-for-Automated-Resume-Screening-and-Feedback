"""
Enhanced Metadata Extractor
Extracts email, phone, location, name, and other info from resumes
"""

import re

def extract_email_phone_location(text):
    """
    Extract email, phone number, and location from resume text
    Returns: (email, phone, location)
    """
    if not text:
        return "Not found", "Not found", "Not found"
    
    email = extract_email(text)
    phone = extract_phone(text)
    location = extract_location(text)
    
    return email, phone, location


def extract_email(text):
    """Extract email address from text"""
    # Enhanced email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    
    if emails:
        # Return the first valid email
        return emails[0]
    
    return "Not found"


def extract_phone(text):
    """Extract phone number from text with multiple formats"""
    # Multiple phone patterns
    phone_patterns = [
        r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # +1 (123) 456-7890
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (123) 456-7890
        r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # 123-456-7890
        r'\+\d{10,15}',  # +12345678901
        r'\d{10}',  # 1234567890
    ]
    
    for pattern in phone_patterns:
        phones = re.findall(pattern, text)
        if phones:
            # Clean up the phone number
            phone = phones[0]
            # Remove extra spaces and format
            phone = re.sub(r'\s+', ' ', phone)
            return phone
    
    return "Not found"


def extract_location(text):
    """Extract location (city, state) from text"""
    # Common location patterns
    location_patterns = [
        # City, State format
        r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*),\s*([A-Z]{2})\b',
        # City, State Name format
        r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*),\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\b',
    ]
    
    # Common keywords that indicate location section
    location_keywords = ['location:', 'address:', 'residence:', 'based in:', 'location']
    
    lines = text.split('\n')
    
    # First, try to find location near keywords
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in location_keywords):
            # Check this line and next few lines
            search_text = ' '.join(lines[i:i+3])
            
            for pattern in location_patterns:
                matches = re.findall(pattern, search_text)
                if matches:
                    city, state = matches[0]
                    return f"{city}, {state}"
    
    # If not found near keywords, search entire text
    for pattern in location_patterns:
        matches = re.findall(pattern, text)
        if matches:
            # Filter out common false positives
            for city, state in matches:
                # Avoid dates and other non-location matches
                if len(city) > 2 and not city.isdigit():
                    return f"{city}, {state}"
    
    return "Not found"


def extract_name(text):
    """Extract candidate name from resume"""
    lines = text.split('\n')
    
    # Usually the first few lines contain the name
    for line in lines[:5]:
        line = line.strip()
        
        # Skip empty lines
        if not line or len(line) < 3:
            continue
        
        # Skip lines with email or phone
        if '@' in line or re.search(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', line):
            continue
        
        # Name pattern: 2-4 capitalized words
        name_pattern = r'^[A-Z][a-z]+(?:\s[A-Z][a-z]+){1,3}$'
        
        if re.match(name_pattern, line):
            return line
    
    return "Not found"


def extract_skills(text):
    """Extract technical skills from resume"""
    # Comprehensive skill list
    skills_list = [
        # Programming Languages
        'Python', 'Java', 'JavaScript', 'C++', 'C#', 'R', 'SQL', 'Scala', 'Go', 'Ruby',
        'PHP', 'Swift', 'Kotlin', 'TypeScript', 'Rust', 'MATLAB', 'Perl', 'Shell',
        
        # ML/AI
        'Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision', 'TensorFlow',
        'PyTorch', 'Keras', 'Scikit-learn', 'XGBoost', 'LightGBM', 'Neural Networks',
        'CNN', 'RNN', 'LSTM', 'Transformer', 'BERT', 'GPT', 'Reinforcement Learning',
        
        # Big Data
        'Hadoop', 'Spark', 'Hive', 'Kafka', 'Flink', 'Storm', 'HBase', 'Cassandra',
        'Airflow', 'MapReduce',
        
        # Cloud
        'AWS', 'Azure', 'GCP', 'Google Cloud', 'S3', 'EC2', 'Lambda', 'SageMaker',
        'Docker', 'Kubernetes', 'Terraform',
        
        # Databases
        'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch', 'DynamoDB',
        'Oracle', 'SQL Server', 'Snowflake', 'Redshift', 'BigQuery',
        
        # Visualization
        'Tableau', 'Power BI', 'Looker', 'Plotly', 'Matplotlib', 'Seaborn', 'D3.js',
        
        # Web Frameworks
        'Django', 'Flask', 'FastAPI', 'React', 'Angular', 'Vue.js', 'Node.js', 'Express',
        
        # DevOps
        'Git', 'GitHub', 'GitLab', 'Jenkins', 'CI/CD', 'Linux', 'Bash', 'Nginx',
        
        # Data Science
        'Pandas', 'NumPy', 'SciPy', 'Statistics', 'A/B Testing', 'Hypothesis Testing',
        'Time Series', 'Forecasting', 'Regression', 'Classification', 'Clustering'
    ]
    
    found_skills = []
    text_lower = text.lower()
    
    for skill in skills_list:
        # Case-insensitive search with word boundaries
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    
    return sorted(set(found_skills))


def extract_experience_years(text):
    """Extract total years of experience"""
    # Patterns to find years of experience
    patterns = [
        r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
        r'experience[:\s]+(\d+)\+?\s*years?',
        r'(\d+)\+?\s*years?\s+professional',
    ]
    
    years = []
    for pattern in patterns:
        matches = re.findall(pattern, text.lower())
        years.extend([int(y) for y in matches])
    
    if years:
        return max(years)  # Return highest mentioned
    
    return None


def extract_education(text):
    """Extract education details"""
    education_levels = {
        'PhD': ['phd', 'ph.d', 'doctorate', 'doctoral'],
        'Masters': ['masters', 'master', 'msc', 'ms', 'mba', 'ma'],
        'Bachelors': ['bachelors', 'bachelor', 'bsc', 'bs', 'ba', 'beng', 'btech']
    }
    
    text_lower = text.lower()
    found_education = []
    
    for level, keywords in education_levels.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_education.append(level)
                break
    
    return found_education if found_education else ['Not specified']


def extract_certifications(text):
    """Extract certifications from resume"""
    common_certs = [
        'AWS Certified', 'Azure Certified', 'GCP Certified',
        'PMP', 'CISSP', 'CFA', 'CPA',
        'Certified Data Scientist', 'TensorFlow Certificate',
        'Kubernetes Certified', 'Docker Certified',
        'Scrum Master', 'Six Sigma', 'ITIL'
    ]
    
    found_certs = []
    text_lower = text.lower()
    
    for cert in common_certs:
        if cert.lower() in text_lower:
            found_certs.append(cert)
    
    return found_certs


def extract_companies(text):
    """Extract company names (basic pattern matching)"""
    # Look for common company indicators
    company_patterns = [
        r'(?:at|@)\s+([A-Z][A-Za-z\s&]+(?:Inc|LLC|Corp|Ltd|Company)?)',
        r'([A-Z][A-Za-z\s&]+(?:Inc|LLC|Corp|Ltd))\s+[-–—]',
    ]
    
    companies = []
    for pattern in company_patterns:
        matches = re.findall(pattern, text)
        companies.extend(matches)
    
    # Clean up and deduplicate
    companies = [c.strip() for c in companies]
    return list(set(companies))[:5]  # Return top 5


def get_comprehensive_metadata(text):
    """
    Extract all metadata from resume
    Returns: Dictionary with all extracted information
    """
    return {
        'name': extract_name(text),
        'email': extract_email(text),
        'phone': extract_phone(text),
        'location': extract_location(text),
        'skills': extract_skills(text),
        'experience_years': extract_experience_years(text),
        'education': extract_education(text),
        'certifications': extract_certifications(text),
        'companies': extract_companies(text)
    }