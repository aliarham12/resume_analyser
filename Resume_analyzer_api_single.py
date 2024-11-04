import spacy
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from pdfminer.high_level import extract_text
from io import BytesIO
import re

app = FastAPI()

nlp = spacy.load("en_core_web_md")

def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

def normalize_skill(skill):
    # Remove numeric parts from the skill (e.g., "python3" -> "python")
    return re.sub(r'\d+', '', skill).strip().lower()

def find_skills_in_text(text, skills_list):
    doc = nlp(text.lower())  # Normalize text to lowercase
    skills_found = [skill for skill in skills_list if normalize_skill(skill) in doc.text]
    return skills_found

def extract_contact_info(text):
    # Regular expression for email
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    # Regular expression for Pakistani phone numbers (e.g., +92xxxxxxxxxx, 03xxxxxxxxx, +92-xxxxxxxxxx, +92 xxxxxxxxxx)
    phone_pattern = re.compile(r'\+92-\d{10}|\+92\d{9}|\+03\d{2}-\d{7}|03\d{9}|\+92\s?\d{10}')
    # Extract email and phone number
    email = email_pattern.findall(text)
    phone = phone_pattern.findall(text)

    # Extract name from the first line and first two words of the second line
    lines = text.split('\n')
    name = None
    if lines:
        first_line = lines[0].strip()
        if len(lines) > 1:
            second_line_words = lines[1].strip().split()[:2]
            if "ENGINEER" not in second_line_words:  # Check if the second line contains "ENGINEER"
                name = f"{first_line} {' '.join(second_line_words)}".strip()
            else:
                name = first_line
    
    email = email[0] if email else None
    phone = phone[0] if phone else None

    return name, email, phone

@app.post("/uploadfile")
async def create_upload_file(skills_required: str = Form(...), resume_file: UploadFile = File(...)):
    try:
        resume_contents = await resume_file.read()
        resume_pdf = BytesIO(resume_contents)
        text = extract_text_from_pdf(resume_pdf)

        # Split skills_required by commas first, then split by slashes
        skills_list = [skill.strip() for skill_with_slash in skills_required.split(',') for skill in skill_with_slash.split('/')]
        lower_skill_list = [normalize_skill(s) for s in skills_list]
        skills = set(lower_skill_list)
        skills_extracted = set(find_skills_in_text(text, skills))
        
        # Extract contact information
        name, email, phone = extract_contact_info(text)
        
        # Print the extracted contact information
        print(f"Extracted Name: {name}")
        print(f"Extracted Email: {email}")
        print(f"Extracted Phone: {phone}")
        
        if skills_extracted:
            skill_rate = round((len(skills_extracted) / len(skills)) * 100, 2)
            response_data = {
                "success": True,
                "responseMessage": "Skills Matched",
                "responseCode": "200",
                "data": {
                    "skills_required": skills_required,
                    "confidence": f'{skill_rate}%',
                    "name": name,
                    "email": email,
                    "phone": phone if phone else "no contact info"  # Set phone to "no contact info" if phone is None
                }
            }
        elif email is None and phone is None:
            response_data = {
                "success": False,
                "responseMessage": "No contact info",
                "responseCode": "404",
                "data": {}
            }
        else:
            response_data = {
                "success": True,
                "responseMessage": "Skill Not Matched",
                "responseCode": "200",
                "data": {
                    "skills_required": skills_required,
                    "confidence": "0.0%",
                    "name": name,
                    "email": email,
                    "phone": phone if phone else "no contact info"  # Set phone to "no contact info" if phone is None
                }
            }
    except Exception as e:
        response_data = {
            "success": False,
            "responseMessage": f"Error: {str(e)}",
            "responseCode": "500",
            "data": {}
        }

    return JSONResponse(content=response_data)
