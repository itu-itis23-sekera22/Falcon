from ai71 import AI71
import re
import pdfplumber
import ast

# pdf_path = 'oyn.pdf' Testing

AI71_API_KEY = ''

weights = {
    'experience': 0.35,
    'skills': 0.35,
    'soft_skills': 0.05,
    'education': 0.2,
    'additional_criteria': 0.05
}

client = AI71(AI71_API_KEY)

# Take PDF format files and return string 
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Classify the information by their criteria and return string
def classify_cv_content(cv_text):
    prompt = f"""
    I have a CV with the following content:

    {cv_text}

    Please classify the information into the following categories:

    1. **Experience:** List the candidate's work experience, including roles, companies, and dates.
    2. **Technical Skills:** List all technical skills mentioned in the CV.
    3. **Education:** List the candidate’s educational background, including degrees, institutions, and dates.
    4. **Soft Skills:** List any soft skills or personal attributes mentioned in the CV.
    5. **Additional Criteria:** List additional criteria and achivements such as hackathons, certificates, awards etc. Do not include any other skills or experience that are already categorized above.

    Please format the output as follows:
    - **Experience:** [Detailed experience information]
    - **Technical Skills:** [List of skills]
    - **Education:** [Educational details]
    - **Soft Skills:** [List of soft skills]
    - **Additional Criteria:** [List of additional criteria or achievements]

    Write down every categorized information as a list.
    """

    output = client.chat.completions.create(
        model="tiiuae/falcon-180B-chat",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return output.choices[0].message.content

# Extract the ratings from classified text and return dictionary 
def extract_scores(cv_text):
    
    prompt = f'''
    Extract the following information from the text and format it as a dictionary:
    1. Experience rating
    2. Education rating
    3. Skills rating
    4. Soft Skills rating
    5. Additional Criteria rating
    6. Overall Score

    Text:
    {cv_text}

    Format the output as follows:
    {{
        "Experience": <score>,
        "Education": <score>,
        "Skills": <score>,
        "Soft Skills": <score>,
        "Additional Criteria": <score>,
        "Overall Score": <score>
    }}
    Ensure the scores are numeric values (integers or floats) and the keys match exactly.
    
    '''
    output = client.chat.completions.create(
        model= 'tiiuae/falcon-180B-chat',
        messages= [
            {"role" : "user", "content" : f'{prompt}'}  
        ]
    )
    
    response_content = output.choices[0].message.content

    try: 
        scores = ast.literal_eval(response_content)
    except (ValueError, SyntaxError): 
        raise('Failed to parse the content into a dictonary.')
    
    return scores



CV_responses = {}

# Evaluate the first CV
output = client.chat.completions.create(
    model="tiiuae/falcon-180B-chat",
    messages=[
        {"role": "system", "content": "You are a Human Resources assistant tasked with ranking resumes based on specific criteria. The criteria are: Experience, Education, Skills, Additional Criteria and Soft Skills.\nEach criterion should be rated out of 10 points.\nPlease provide a detailed rating and explanation for each criterion."},
        {"role": "system", "content": "Evaluation Guidelines:\n1. **Experience:** Rate based on quality, impact and relevance of the experiences. Focus on the candidate’s previous work roles and projects. Consider factors such as impact and outcome, complexity and innovation, relevance and applicability, recognition and awards, and scope and scale. Technical skills should not be evaluated here; only work history and project details are relevant.\n2. **Education:** Rate based on the level and quality of education. Consider whether the candidate holds a bachelor’s degree, master’s degree, or higher. Higher degrees or more advanced education relevant to the job role should be rated more favorably. Use university rankings (e.g., QS World University Rankings) for added context. For example, a master’s degree in Computer Science from a top-ranked university should be rated higher than a bachelor’s degree from a less recognized institution.\n3. **Skills:** Rate based on the relevance and proficiency in required technical skills. Ensure that high proficiency and practical application of required technical skills are reflected in the rating. Technical skills should be evaluated here only, not in the Experience section.\n4. **Soft Skills:** Rate based on the presence of key soft skills such as communication, teamwork, and leadership demonstrated through examples of roles in the CV.\n5. **Additional Criteria:** Rate based on the quality and significance of additional achievements such as certifications, awards, and hackathons. High-impact and relevant achievements should be rated higher.\nFor each criterion, if the candidate's features match exactly with the job posting, give around 7 points. Add extra points depending on extra useful features that does not take a part in job posting.\nProvide a detailed rating and explanation for each criterion.\n"},
        {"role": "system", "content": "Overall Score = (Experience score * 0.35) + (Education Score * 0.20) + (Skills Score * 0.35) + (Soft Skills Score * 0.05) + (Additional Criteria Score * 0.05).\nAfter you rate each criterion, calculate the overall score using this formula."},
        {"role": "user", "content": f"This is the job posting:\n{job_advertisement}\nEvaluate this CV:\n{cv_oyn}\n according to the job posting and provide rating and explanation for each criterion."}
    ],
)

content = output.choices[0].message.content
CV_responses = {'Ozan Andaç' : content}

# Evaluate all CVs with reference to the previous one (This part will be changed after the database implementation)
'''
previous = content

for CV in CVs[1:]:
    output = client.chat.completions.create(
        model="tiiuae/falcon-180B-chat",
        messages=[
            {"role": "system", "content": "You are a Human Resources assistant tasked with ranking resumes based on specific criteria. The criteria are: Experience, Education, Skills, Additional Criteria and Soft Skills. Each criterion should be rated out of 10 points.\nPlease provide a detailed rating and explanation for each criterion."},
            {"role": "system", "content": "Evaluation Guidelines:\n1. **Experience:** Rate based on quality, impact and relevance of the experiences. Focus on the candidate’s previous work roles and projects. Consider factors such as impact and outcome, complexity and innovation, relevance and applicability, recognition and awards, and scope and scale. Technical skills should not be evaluated here; only work history and project details are relevant.\n2. **Education:** Rate based on the level and quality of education. Consider whether the candidate holds a bachelor’s degree, master’s degree, or higher. Higher degrees or more advanced education relevant to the job role should be rated more favorably. Use university rankings (e.g., QS World University Rankings) for added context. For example, a master’s degree in Computer Science from a top-ranked university should be rated higher than a bachelor’s degree from a less recognized institution.\n3. **Skills:** Rate based on the relevance and proficiency in required technical skills. Ensure that high proficiency and practical application of required technical skills are reflected in the rating. Technical skills should be evaluated here only, not in the Experience section.\n4. **Soft Skills:** Rate based on the presence of key soft skills such as communication, teamwork, and leadership demonstrated through examples of roles in the CV.\n5. **Additional Criteria:** Rate based on the quality and significance of additional achievements such as certifications, awards, and hackathons. High-impact and relevant achievements should be rated higher.\nFor each criterion, if the candidate's features match exactly with the job posting, give around 7 points. Add extra points depending on extra useful features that does not take a part in job posting.\nProvide a detailed rating and explanation for each criterion.\n"},
            {"role": "system", "content": "Overall Score = (Experience score * 0.35) + (Education Score * 0.20) + (Skills Score * 0.35) + (Soft Skills Score * 0.05) + (Additional Criteria Score * 0.05). After you rate each criterion, calculate the overall score using this formula."},
            {"role": "assistant", "content": f"Sample CV rating and analyzing : {previous}."},
            {"role": "user", "content": f"This is the job posting:\n{job_advertisement}\nEvaluate this CV:\n{CV['content']}\n according to the job posting and comparing with sample CV, provide rating and explanation for each criterion."},
        ],
)
    CV_responses[CV['name']] = output.choices[0].message.content
    previous = output.choices[0].message.content
'''

for CV in CV_responses.keys():

    print(f"{CV} Analyz\n {CV_responses[CV]}\n\n")
    print(extract_scores(CV_responses[CV]))