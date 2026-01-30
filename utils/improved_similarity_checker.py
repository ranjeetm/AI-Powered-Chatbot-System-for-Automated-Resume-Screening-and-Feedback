"""
Enhanced Similarity Checker with Multiple Scoring Algorithms
Provides more accurate resume-to-job description matching
"""

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class EnhancedSimilarityChecker:
    
    def __init__(self):
        self.skill_keywords = {
            'programming': ['python', 'java', 'javascript', 'c++', 'r', 'scala', 'go', 'rust', 'sql', 'typescript'],
            'ml_frameworks': ['tensorflow', 'pytorch', 'keras', 'scikit-learn', 'xgboost', 'lightgbm', 'catboost'],
            'big_data': ['spark', 'hadoop', 'hive', 'kafka', 'flink', 'airflow'],
            'cloud': ['aws', 'azure', 'gcp', 'google cloud', 's3', 'ec2', 'sagemaker', 'lambda'],
            'databases': ['sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'cassandra', 'snowflake', 'redshift'],
            'ml_concepts': ['machine learning', 'deep learning', 'nlp', 'computer vision', 'neural network', 
                          'supervised learning', 'unsupervised learning', 'reinforcement learning', 'regression',
                          'classification', 'clustering', 'cnn', 'rnn', 'lstm', 'transformer', 'bert', 'gpt'],
            'tools': ['git', 'docker', 'kubernetes', 'jenkins', 'ci/cd', 'jira', 'linux'],
            'visualization': ['tableau', 'power bi', 'plotly', 'matplotlib', 'seaborn', 'looker', 'd3.js'],
            'statistics': ['statistics', 'probability', 'hypothesis testing', 'a/b testing', 'statistical analysis',
                         'regression analysis', 'time series', 'forecasting']
        }
        
        # Flatten all skills for quick lookup
        self.all_skills = set()
        for category in self.skill_keywords.values():
            self.all_skills.update(category)
    
    def preprocess_text(self, text):
        """Clean and preprocess text"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces and alphanumeric
        text = re.sub(r'[^a-zA-Z0-9\s\+\#\.]', ' ', text)
        
        # Handle common variations
        text = text.replace('c++', 'cplusplus')
        text = text.replace('c#', 'csharp')
        text = text.replace('.net', 'dotnet')
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def extract_skills(self, text):
        """Extract technical skills from text"""
        text_lower = text.lower()
        found_skills = set()
        
        for skill in self.all_skills:
            # Use word boundaries for exact matching
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill)
        
        return found_skills
    
    def calculate_skill_match_score(self, resume_text, jd_text):
        """Calculate score based on skill matching"""
        resume_skills = self.extract_skills(resume_text)
        jd_skills = self.extract_skills(jd_text)
        
        if not jd_skills:
            return 0.0
        
        matched_skills = resume_skills.intersection(jd_skills)
        skill_match_ratio = len(matched_skills) / len(jd_skills)
        
        # Bonus for having extra relevant skills
        extra_skills = resume_skills - jd_skills
        extra_bonus = min(len(extra_skills) * 0.02, 0.1)  # Max 10% bonus
        
        return min((skill_match_ratio * 100) + (extra_bonus * 100), 100)
    
    def calculate_tfidf_score(self, resume_text, jd_text):
        """Calculate cosine similarity using TF-IDF"""
        # Preprocess texts
        resume_clean = self.preprocess_text(resume_text)
        jd_clean = self.preprocess_text(jd_text)
        
        if not resume_clean or not jd_clean:
            return 0.0
        
        try:
            # Create TF-IDF vectorizer with more lenient settings
            vectorizer = TfidfVectorizer(
                max_features=500,  # Reduced from 1000 for better matching
                stop_words='english',
                ngram_range=(1, 3),  # Include trigrams for better phrase matching
                min_df=1,
                max_df=0.95,  # Ignore very common terms
                sublinear_tf=True  # Use log scaling for term frequency
            )
            
            # Fit and transform
            tfidf_matrix = vectorizer.fit_transform([jd_clean, resume_clean])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Boost the score - raw cosine similarity is often too low
            # Apply a sigmoid-like transformation to boost mid-range scores
            boosted_similarity = similarity * 1.5  # 50% boost
            boosted_similarity = min(boosted_similarity, 0.95)  # Cap at 95%
            
            return boosted_similarity * 100
        
        except Exception as e:
            print(f"TF-IDF calculation error: {e}")
            return 0.0
    
    def calculate_keyword_density_score(self, resume_text, jd_text):
        """Calculate score based on keyword density"""
        # Extract important keywords from JD
        jd_words = set(self.preprocess_text(jd_text).split())
        resume_words = set(self.preprocess_text(resume_text).split())
        
        # Remove very common words
        common_words = {'the', 'and', 'for', 'with', 'this', 'that', 'from', 'have', 
                       'has', 'had', 'are', 'was', 'were', 'will', 'would', 'could',
                       'should', 'may', 'might', 'must', 'can', 'our', 'your', 'their',
                       'about', 'into', 'through', 'during', 'before', 'after', 'above',
                       'below', 'between', 'under', 'again', 'further', 'then', 'once'}
        
        jd_keywords = jd_words - common_words
        jd_keywords = {w for w in jd_keywords if len(w) > 2}  # Filter short words
        
        if not jd_keywords:
            return 50.0  # Return 50% if no keywords found
        
        # Count matches
        matched_keywords = resume_words.intersection(jd_keywords)
        
        # Calculate base score
        base_score = (len(matched_keywords) / len(jd_keywords)) * 100
        
        # Give bonus for having more keywords than required
        extra_keywords = len(matched_keywords) - len(jd_keywords)
        if extra_keywords > 0:
            bonus = min(extra_keywords * 0.5, 15)  # Max 15% bonus
            base_score = min(base_score + bonus, 100)
        
        return base_score
    
    def calculate_experience_score(self, resume_text, jd_text):
        """Score based on experience indicators"""
        score = 50.0  # Start with base score
        
        # Check for years of experience
        exp_pattern = r'(\d+)[\+]?\s*(?:year|yr)s?'
        
        resume_exp = re.findall(exp_pattern, resume_text.lower())
        jd_exp = re.findall(exp_pattern, jd_text.lower())
        
        if resume_exp and jd_exp:
            max_resume_exp = max([int(x) for x in resume_exp])
            required_exp = max([int(x) for x in jd_exp])
            
            if max_resume_exp >= required_exp:
                score = 100  # Meets or exceeds requirement
            elif max_resume_exp >= required_exp * 0.8:
                score = 85  # Close enough (80%+ of requirement)
            elif max_resume_exp >= required_exp * 0.6:
                score = 70  # Reasonable (60%+ of requirement)
            else:
                score = 60  # Below requirement but has experience
        elif resume_exp:
            # Has experience mentioned but JD doesn't specify
            years = max([int(x) for x in resume_exp])
            if years >= 5:
                score = 90
            elif years >= 3:
                score = 80
            elif years >= 1:
                score = 70
        
        # Check for projects/achievements - add to score
        achievement_keywords = ['developed', 'built', 'created', 'led', 'managed', 
                               'implemented', 'designed', 'architected', 'deployed', 
                               'achieved', 'delivered', 'launched', 'optimized']
        
        achievement_count = sum(resume_text.lower().count(keyword) for keyword in achievement_keywords)
        score += min(achievement_count * 1.5, 15)  # Max 15 points
        
        # Check for quantifiable achievements - add to score
        numbers_pattern = r'\d+%|\d+\+|\$\d+|increased.*\d+|reduced.*\d+|improved.*\d+'
        quantified_achievements = len(re.findall(numbers_pattern, resume_text.lower()))
        score += min(quantified_achievements * 2, 10)  # Max 10 points
        
        return min(score, 100)
    
    def calculate_education_score(self, resume_text, jd_text):
        """Score based on education match"""
        education_keywords = {
            'phd': 100,
            'doctorate': 100,
            'ph.d': 100,
            'masters': 80,
            'master': 80,
            'msc': 80,
            'ms': 80,
            'mba': 70,
            'bachelors': 60,
            'bachelor': 60,
            'bsc': 60,
            'bs': 60,
            'degree': 40
        }
        
        resume_lower = resume_text.lower()
        jd_lower = jd_text.lower()
        
        # Find highest education in resume
        resume_edu_score = 0
        for edu, score in education_keywords.items():
            if edu in resume_lower:
                resume_edu_score = max(resume_edu_score, score)
        
        # Find required education in JD
        jd_edu_score = 0
        for edu, score in education_keywords.items():
            if edu in jd_lower:
                jd_edu_score = max(jd_edu_score, score)
        
        # Score based on match
        if resume_edu_score >= jd_edu_score:
            return 100
        elif resume_edu_score > 0:
            return (resume_edu_score / max(jd_edu_score, 1)) * 100
        else:
            return 50  # No education info found
    
    def calculate_weighted_score(self, resume_text, jd_text):
        """Calculate final weighted score combining all methods"""
        
        # Calculate individual scores
        skill_score = self.calculate_skill_match_score(resume_text, jd_text)
        tfidf_score = self.calculate_tfidf_score(resume_text, jd_text)
        keyword_score = self.calculate_keyword_density_score(resume_text, jd_text)
        experience_score = self.calculate_experience_score(resume_text, jd_text)
        education_score = self.calculate_education_score(resume_text, jd_text)
        
        # Apply bonuses and adjustments
        # If skill match is very high, boost other scores
        if skill_score >= 90:
            tfidf_score = max(tfidf_score, 60)  # Minimum 60% if skills are strong
            keyword_score = max(keyword_score, 50)  # Minimum 50% if skills are strong
        elif skill_score >= 80:
            tfidf_score = max(tfidf_score, 50)
            keyword_score = max(keyword_score, 40)
        
        # Weighted combination with adjusted weights
        weights = {
            'skills': 0.50,      # 50% - Most important (increased from 35%)
            'tfidf': 0.20,       # 20% - Overall content similarity (reduced from 25%)
            'keywords': 0.15,    # 15% - Keyword matching (reduced from 20%)
            'experience': 0.10,  # 10% - Experience indicators (reduced from 15%)
            'education': 0.05    # 5% - Education match (same)
        }
        
        final_score = (
            skill_score * weights['skills'] +
            tfidf_score * weights['tfidf'] +
            keyword_score * weights['keywords'] +
            experience_score * weights['experience'] +
            education_score * weights['education']
        )
        
        # Apply skill bonus - if skills are excellent, add bonus
        if skill_score >= 95:
            final_score = min(final_score + 8, 100)  # +8% bonus
        elif skill_score >= 85:
            final_score = min(final_score + 5, 100)  # +5% bonus
        elif skill_score >= 75:
            final_score = min(final_score + 3, 100)  # +3% bonus
        
        # Ensure minimum score based on skill match
        if skill_score >= 90:
            final_score = max(final_score, 75)  # At least 75% if 90%+ skills
        elif skill_score >= 80:
            final_score = max(final_score, 70)  # At least 70% if 80%+ skills
        elif skill_score >= 70:
            final_score = max(final_score, 65)  # At least 65% if 70%+ skills
        
        return round(final_score, 1)
    
    def get_detailed_analysis(self, resume_text, jd_text):
        """Get detailed breakdown of the analysis"""
        
        resume_skills = self.extract_skills(resume_text)
        jd_skills = self.extract_skills(jd_text)
        matched_skills = resume_skills.intersection(jd_skills)
        missing_skills = jd_skills - resume_skills
        extra_skills = resume_skills - jd_skills
        
        analysis = {
            'overall_score': self.calculate_weighted_score(resume_text, jd_text),
            'breakdown': {
                'skill_match': round(self.calculate_skill_match_score(resume_text, jd_text), 1),
                'content_similarity': round(self.calculate_tfidf_score(resume_text, jd_text), 1),
                'keyword_density': round(self.calculate_keyword_density_score(resume_text, jd_text), 1),
                'experience': round(self.calculate_experience_score(resume_text, jd_text), 1),
                'education': round(self.calculate_education_score(resume_text, jd_text), 1)
            },
            'skills': {
                'matched': sorted(list(matched_skills)),
                'missing': sorted(list(missing_skills)),
                'extra': sorted(list(extra_skills))
            }
        }
        
        return analysis


# Main function for backward compatibility
def calculate_similarity_score(jd_text, resume_text):
    """
    Calculate similarity score between job description and resume
    Returns: Score as string with % (e.g., "85.5")
    """
    checker = EnhancedSimilarityChecker()
    score = checker.calculate_weighted_score(resume_text, jd_text)
    return f"{score:.1f}"


def get_detailed_match_analysis(jd_text, resume_text):
    """
    Get detailed analysis of resume match
    Returns: Dictionary with scores and skill breakdown
    """
    checker = EnhancedSimilarityChecker()
    return checker.get_detailed_analysis(resume_text, jd_text)