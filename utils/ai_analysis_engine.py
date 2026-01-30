"""
AI-Powered Analysis Engine
Generates intelligent strengths, weaknesses, and recommendations
"""

import re
from collections import Counter

class AIAnalysisEngine:
    
    def __init__(self):
        self.critical_skills = {
            'programming': ['python', 'java', 'javascript', 'sql', 'r'],
            'ml': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn'],
            'cloud': ['aws', 'azure', 'gcp', 'google cloud'],
            'big_data': ['spark', 'hadoop', 'kafka'],
            'databases': ['sql', 'postgresql', 'mongodb', 'mysql'],
        }
    
    def analyze_resume(self, resume_text, jd_text, match_score):
        """
        Comprehensive analysis of resume against job description
        Returns: strengths, weaknesses, recommendations
        """
        resume_lower = resume_text.lower()
        jd_lower = jd_text.lower()
        
        strengths = self._identify_strengths(resume_lower, jd_lower)
        weaknesses = self._identify_weaknesses(resume_lower, jd_lower)
        recommendations = self._generate_recommendations(resume_lower, jd_lower, match_score, weaknesses)
        
        return strengths, weaknesses, recommendations
    
    def _identify_strengths(self, resume_text, jd_text):
        """Identify candidate's strengths"""
        strengths = []
        
        # 1. Matching critical skills
        matched_critical = []
        for category, skills in self.critical_skills.items():
            for skill in skills:
                if skill in resume_text and skill in jd_text:
                    matched_critical.append(skill)
        
        if matched_critical:
            if len(matched_critical) >= 5:
                strengths.append(f"Strong technical foundation with expertise in {', '.join(matched_critical[:5])}")
            else:
                strengths.append(f"Proficiency in key technologies: {', '.join(matched_critical)}")
        
        # 2. Quantifiable achievements
        numbers = re.findall(r'\d+%|\d+\+|increased.*\d+|reduced.*\d+|improved.*\d+', resume_text)
        if len(numbers) >= 5:
            strengths.append("Strong track record of quantifiable achievements and measurable impact")
        elif len(numbers) >= 3:
            strengths.append("Demonstrates results with specific metrics and outcomes")
        
        # 3. Leadership indicators
        leadership_terms = ['led', 'managed', 'directed', 'coordinated', 'mentored', 'supervised']
        leadership_count = sum(resume_text.count(term) for term in leadership_terms)
        if leadership_count >= 3:
            strengths.append("Proven leadership and team management experience")
        
        # 4. Project experience
        project_indicators = ['project', 'developed', 'built', 'implemented', 'deployed', 'created']
        project_count = sum(resume_text.count(term) for term in project_indicators)
        if project_count >= 5:
            strengths.append("Extensive hands-on project experience and implementation skills")
        
        # 5. Advanced skills
        advanced_skills = ['deep learning', 'neural network', 'nlp', 'computer vision', 'transformer', 
                          'bert', 'gpt', 'reinforcement learning']
        advanced_found = [skill for skill in advanced_skills if skill in resume_text]
        if len(advanced_found) >= 2:
            strengths.append(f"Advanced expertise in cutting-edge technologies: {', '.join(advanced_found[:3])}")
        
        # 6. Experience level
        exp_match = re.search(r'(\d+)\+?\s*years?\s+(?:of\s+)?experience', resume_text)
        if exp_match:
            years = int(exp_match.group(1))
            if years >= 5:
                strengths.append(f"Substantial industry experience ({years}+ years)")
            elif years >= 3:
                strengths.append(f"Solid professional experience ({years} years)")
        
        # 7. Education
        high_edu = ['phd', 'ph.d', 'masters', 'master', 'msc']
        if any(edu in resume_text for edu in high_edu):
            strengths.append("Strong educational background in relevant field")
        
        # 8. Cloud experience
        cloud_platforms = ['aws', 'azure', 'gcp', 'google cloud']
        cloud_found = [c for c in cloud_platforms if c in resume_text and c in jd_text]
        if cloud_found:
            strengths.append(f"Experience with cloud platforms: {', '.join(cloud_found)}")
        
        # 9. Soft skills mentioned
        soft_skills = ['communication', 'collaboration', 'problem-solving', 'analytical', 
                      'team player', 'leadership']
        soft_found = [s for s in soft_skills if s in resume_text]
        if len(soft_found) >= 2:
            strengths.append(f"Well-rounded professional with strong {' and '.join(soft_found[:2])} skills")
        
        # If no strengths found, add generic ones
        if not strengths:
            strengths = [
                "Relevant experience in the field",
                "Technical skills aligned with role requirements",
                "Professional background matches industry standards"
            ]
        
        return strengths[:6]  # Return top 6 strengths
    
    def _identify_weaknesses(self, resume_text, jd_text):
        """Identify gaps and weaknesses"""
        weaknesses = []
        
        # 1. Missing critical skills from JD
        missing_critical = []
        for category, skills in self.critical_skills.items():
            for skill in skills:
                if skill in jd_text and skill not in resume_text:
                    missing_critical.append(skill)
        
        if missing_critical:
            if len(missing_critical) <= 2:
                weaknesses.append(f"Missing experience with: {', '.join(missing_critical)}")
            else:
                weaknesses.append(f"Limited exposure to key technologies: {', '.join(missing_critical[:3])}")
        
        # 2. Lack of quantifiable achievements
        numbers = re.findall(r'\d+%|\d+\+', resume_text)
        if len(numbers) < 3:
            weaknesses.append("Could strengthen resume with more quantifiable achievements and metrics")
        
        # 3. Missing cloud experience
        if any(cloud in jd_text for cloud in ['aws', 'azure', 'gcp', 'cloud']):
            if not any(cloud in resume_text for cloud in ['aws', 'azure', 'gcp', 'cloud']):
                weaknesses.append("Limited cloud platform experience (AWS, Azure, or GCP)")
        
        # 4. No ML experience if required
        ml_terms = ['machine learning', 'deep learning', 'neural network', 'tensorflow', 'pytorch']
        if any(term in jd_text for term in ml_terms):
            if not any(term in resume_text for term in ml_terms):
                weaknesses.append("Insufficient machine learning or AI experience")
        
        # 5. Missing big data tools
        big_data = ['spark', 'hadoop', 'kafka', 'hive', 'flink']
        if any(tool in jd_text for tool in big_data):
            if not any(tool in resume_text for tool in big_data):
                weaknesses.append("Limited big data processing experience")
        
        # 6. Weak action verbs
        strong_verbs = ['led', 'managed', 'developed', 'implemented', 'architected', 
                       'optimized', 'engineered', 'designed']
        verb_count = sum(resume_text.count(verb) for verb in strong_verbs)
        if verb_count < 5:
            weaknesses.append("Could use stronger action verbs to describe accomplishments")
        
        # 7. Resume length issues
        word_count = len(resume_text.split())
        if word_count < 400:
            weaknesses.append("Resume appears brief - consider adding more detail about experiences")
        elif word_count > 1500:
            weaknesses.append("Resume is lengthy - focus on most relevant experiences")
        
        # 8. No certifications mentioned
        cert_keywords = ['certified', 'certification', 'certificate']
        if any(cert in jd_text for cert in cert_keywords):
            if not any(cert in resume_text for cert in cert_keywords):
                weaknesses.append("No relevant certifications mentioned")
        
        # If no weaknesses found, add constructive ones
        if not weaknesses:
            weaknesses = [
                "Consider adding more specific project examples",
                "Could highlight leadership experiences more prominently",
                "May benefit from including relevant certifications"
            ]
        
        return weaknesses[:5]  # Return top 5 weaknesses
    
    def _generate_recommendations(self, resume_text, jd_text, match_score, weaknesses):
        """Generate actionable recommendations"""
        recommendations = []
        
        # 1. Score-based recommendations
        if match_score < 60:
            recommendations.append("Strongly consider tailoring your resume to highlight skills matching this specific role")
            recommendations.append("Add more keywords from the job description naturally into your experience descriptions")
        elif match_score < 75:
            recommendations.append("Good foundation - focus on emphasizing your most relevant experiences")
            recommendations.append("Add specific examples that demonstrate required skills in action")
        else:
            recommendations.append("Strong match! Ensure your top achievements are prominently featured")
            recommendations.append("Consider adding a summary section highlighting your key qualifications")
        
        # 2. Based on weaknesses
        weakness_text = ' '.join(weaknesses).lower()
        
        if 'quantifiable' in weakness_text or 'metrics' in weakness_text:
            recommendations.append("Add numbers and metrics to your achievements (e.g., '25% improvement', 'saved $50K', 'led team of 8')")
        
        if 'cloud' in weakness_text:
            recommendations.append("Highlight any cloud-related projects or experiences, even if limited")
        
        if 'machine learning' in weakness_text or 'ml' in weakness_text:
            recommendations.append("Include any ML coursework, projects, or self-learning experiences")
        
        if 'action verbs' in weakness_text:
            recommendations.append("Start bullet points with strong action verbs: Led, Engineered, Architected, Optimized, Implemented")
        
        if 'certifications' in weakness_text:
            recommendations.append("Consider obtaining relevant certifications (AWS, Azure, TensorFlow, etc.) to strengthen your profile")
        
        # 3. Always include these
        if 'keywords' not in ' '.join(recommendations):
            recommendations.append("Naturally incorporate industry-specific keywords from the job posting")
        
        recommendations.append("Ensure your LinkedIn profile matches your resume for consistency")
        
        # 4. Format recommendations
        numbers = re.findall(r'\d+%|\d+\+', resume_text)
        if len(numbers) < 5:
            recommendations.append("Quantify your impact wherever possible - numbers grab attention")
        
        # 5. ATS optimization
        recommendations.append("Use standard section headers (Experience, Education, Skills) for ATS compatibility")
        
        return recommendations[:8]  # Return top 8 recommendations


def generate_analysis(resume_text, jd_text, match_score):
    """
    Main function to generate complete analysis
    Returns: (strengths_list, weaknesses_list, recommendations_list)
    """
    engine = AIAnalysisEngine()
    return engine.analyze_resume(resume_text, jd_text, match_score)