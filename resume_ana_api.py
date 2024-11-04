# import spacy
# from fastapi import FastAPI, File, UploadFile, Form
# from fastapi.responses import JSONResponse
# from pdfminer.high_level import extract_text
# from io import BytesIO
# import re

# app = FastAPI()

# nlp = spacy.load("en_core_web_md")

# def extract_text_from_pdf(pdf_path):
#     return extract_text(pdf_path)

# def normalize_skill(skill):
#     return re.sub(r'\d+', '', skill).strip().lower()

# def find_skills_in_text(text, skills_list):
#     doc = nlp(text.lower())
#     skills_found = [skill for skill in skills_list if normalize_skill(skill) in doc.text]
#     return skills_found

# def extract_contact_info(text):
#     email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
#     phone_pattern = re.compile(r'\+92-\d{10}|\+92\d{9}|\+03\d{2}-\d{7}|03\d{9}|\+92\s?\d{10}')
#     email = email_pattern.findall(text)
#     phone = phone_pattern.findall(text)

#     lines = text.split('\n')
#     name = None
#     if lines:
#         first_line = lines[0].strip()
#         if len(lines) > 1:
#             second_line_words = lines[1].strip().split()[:2]
#             if "ENGINEER" not in second_line_words:
#                 name = f"{first_line} {' '.join(second_line_words)}".strip()
#             else:
#                 name = first_line
    
#     email = email[0] if email else None
#     phone = phone[0] if phone else None

#     return name, email, phone

# @app.post("/uploadfile")
# async def create_upload_file(skills_required: str = Form(...), resume_files: list[UploadFile] = File(...)):
#     responses = []
    
#     try:
#         # Split skills_required by commas and then by slashes
#         skills_list = [skill.strip() for skill_with_slash in skills_required.split(',') for skill in skill_with_slash.split('/')]
#         lower_skill_list = [normalize_skill(s) for s in skills_list]
#         skills = set(lower_skill_list)

#         for resume_file in resume_files:
#             resume_contents = await resume_file.read()
#             resume_pdf = BytesIO(resume_contents)
#             text = extract_text_from_pdf(resume_pdf)

#             skills_extracted = set(find_skills_in_text(text, skills))
#             skills_missing = skills - skills_extracted  # Calculate missing skills
#             name, email, phone = extract_contact_info(text)

#             if skills_extracted:
#                 skill_rate = round((len(skills_extracted) / len(skills)) * 100, 2)
#                 response_data = {
#                     "success": True,
#                     "responseMessage": "Skills Matched",
#                     "responseCode": "200",
#                     "data": {
#                         "skills_required": skills_required,
#                         "confidence": f'{skill_rate}%',
#                         "skills_extracted": list(skills_extracted),
#                         "skills_missing": list(skills_missing),  # Include missing skills
#                         "name": name,
#                         "email": email,
#                         "phone": phone if phone else "no contact info"
#                     }
#                 }
#             elif email is None and phone is None:
#                 response_data = {
#                     "success": False,
#                     "responseMessage": "No contact info",
#                     "responseCode": "404",
#                     "data": {}
#                 }
#             else:
#                 response_data = {
#                     "success": True,
#                     "responseMessage": "Skill Not Matched",
#                     "responseCode": "200",
#                     "data": {
#                         "skills_required": skills_required,
#                         "confidence": "0.0%",
#                         "skills_extracted": list(skills_extracted),
#                         "skills_missing": list(skills_missing),  # Include missing skills
#                         "name": name,
#                         "email": email,
#                         "phone": phone if phone else "no contact info"
#                     }
#                 }

#             responses.append(response_data)
    
#     except Exception as e:
#         response_data = {
#             "success": False,
#             "responseMessage": f"Error: {str(e)}",
#             "responseCode": "500",
#             "data": {}
#         }
#         responses.append(response_data)

#     return JSONResponse(content={"results": responses})


import spacy
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from pdfminer.high_level import extract_text
from io import BytesIO
from difflib import SequenceMatcher
import re


app = FastAPI()

nlp = spacy.load("en_core_web_md")

def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

def normalize_skill(skill):
    # Normalize skills more robustly, potentially adding common variations
    skill_variations = {
        "python": ["pyhton", "python3"],
        # Add more common variations as needed
    }
    skill = skill.strip().lower()
    for key, variations in skill_variations.items():
        if skill in variations:
            return key
    return re.sub(r'\d+', '', skill).strip()

def find_skills_in_text(text, skills_list):
    doc = nlp(text.lower())
    skills_found = [skill for skill in skills_list if normalize_skill(skill) in doc.text]
    return skills_found

# def extract_contact_info(text):
#     # Updated regex for email to handle newlines and whitespaces between email parts
#     email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+(?:@|\s*@\s*)[A-Za-z0-9.-]+(?:\.|\s*\.\s*)[A-Za-z]{2,}\b', re.MULTILINE)
#     # phone_pattern = re.compile(r'(?:\+92|0)\d{10}')
#     # phone_pattern = re.compile(r'(\+\d{2}\s?3\d{2}[\s.-]?\d{7}|\b03\d{2}[\s.-]?\d{7}\b)')
#     # phone_pattern = re.compile(r'(\+\d{1,3}[\s\(\)\.-]*3\d{2}[\s\(\)\.-]*\d{3}[\s\(\)\.-]*\d{4}|\b03\d{2}[\s\(\)\.-]*\d{3}[\s\(\)\.-]*\d{4}\b)')
#     # phone_pattern = re.compile(r'(\+\d{1,3}[\s\(\)\.-]*\d{1,3}[\s\(\)\.-]*\d{3}[\s\(\)\.-]*\d{4}|\b03\d{2}[\s\(\)\.-]*\d{3}[\s\(\)\.-]*\d{4}\b)')
#     phone_pattern = re.compile(r'(\+\d{1,3}[\s\(\)\.-]*\d{1,3}[\s\(\)\.-]*\d{3}[\s\(\)\.-]*\d{4}|\b03\d{2}[\s\(\)\.-]*\d{3}[\s\(\)\.-]*\d{4}\b|\b\d{3}[\s\(\)\.-]*\d{3}[\s\(\)\.-]*\d{4}\b)')

#     # Extract emails and phone numbers
#     email_matches = email_pattern.findall(text)
#     phone_matches = phone_pattern.findall(text)

#     # Join email parts that may be split across lines
#     email_matches = [re.sub(r'\s+', '', email) for email in email_matches]
    
# # Check the number of emails before filtering
#     if len(email_matches) > 1:
#         # Filter emails by specific domains only if more than one email is found
#         valid_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
#         filtered_emails = [email for email in email_matches if any(domain in email for domain in valid_domains)]
        
#         # If filtered emails are found, select the first one, otherwise set email to None
#         email = filtered_emails[0] if filtered_emails else None
#     else:
#         # If there's only one email, return it without filtering
#         email = email_matches[0] if email_matches else None
    
#     phone = phone_matches[0] if phone_matches else None

#     # Process phone number to remove all non-numeric characters
#     if phone:
#         phone = re.sub(r'\D', '', phone)

#     # Extract name: taking the first line as the name and cleaning it
#     lines = text.split('\n')
#     name = None
#     if lines:
#         first_line = lines[0].strip()
#         name = first_line
#         name = re.sub(rf"{re.escape(email) if email else ''}|{re.escape(phone) if phone else ''}", "", name).strip()

#     return name, email, phone

def similarity(a, b):
    """Calculate the similarity between two strings."""
    return SequenceMatcher(None, a, b).ratio()

def extract_contact_info(text):
    # Updated regex for email to handle newlines and whitespaces between email parts
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+(?:@|\s*@\s*)[A-Za-z0-9.-]+(?:\.|\s*\.\s*)[A-Za-z]{2,}\b', re.MULTILINE)
    phone_pattern = re.compile(r'(\+\d{1,3}[\s\(\)\.-]*\d{1,3}[\s\(\)\.-]*\d{3}[\s\(\)\.-]*\d{4}|\b03\d{2}[\s\(\)\.-]*\d{3}[\s\(\)\.-]*\d{4}\b|\b\d{3}[\s\(\)\.-]*\d{3}[\s\(\)\.-]*\d{4}\b)')
    



    # Extract emails and phone numbers
    email_matches = email_pattern.findall(text)
    phone_matches = phone_pattern.findall(text)

    # Join email parts that may be split across lines
    email_matches = [re.sub(r'\s+', '', email) for email in email_matches]

    # Check the number of emails before filtering
    if len(email_matches) > 1:
        valid_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
        filtered_emails = [email for email in email_matches if any(domain in email for domain in valid_domains)]
        email = filtered_emails[0] if filtered_emails else None
    else:
        email = email_matches[0] if email_matches else None

    phone = phone_matches[0] if phone_matches else None

    # Process phone number to remove all non-numeric characters
    if phone:
        phone = re.sub(r'\D', '', phone)

    
    # Extract the part of the email before the '@'
    if email:
        email_local_part = email.split('@')[0].lower()
    else:
        email_local_part = ""
    
    # Extract name: taking the first line as the name and cleaning it
    lines = text.split('\n')
    first_line_name = None
    if lines:
        first_line_name = lines[0].strip()
        # Remove email and phone from the potential name
        first_line_name = re.sub(rf"{re.escape(email) if email else ''}|{re.escape(phone) if phone else ''}", "", first_line_name).strip()

        #                     # Clean up the text for name extraction
    cleaned_text = re.sub(r'\n+', ' ', text)  # Replace newlines with spaces
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Remove extra spaces
    cleaned_text = re.sub(r'\f', '', cleaned_text)  # Remove form feeds
    cleaned_text = re.sub(r'http[s]?://\S+|www\.\S+', '', cleaned_text)  # Remove URLs
    cleaned_text = re.sub(r'\(.*?\)', '', cleaned_text)  # Remove parentheses content (like (LinkedIn))
    
    # Use SpaCy to extract the name
    doc = nlp(cleaned_text)
    spacy_names = [ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON"]
    
    # Logic to determine which name to keep using similarity to email local part
    if spacy_names:
        # Get the first valid name from SpaCy (if any)
        spacy_name = spacy_names[0]
        
        # Compare the first line name and spacy name to the email local part
        first_line_similarity = similarity(first_line_name.lower(), email_local_part) if first_line_name else 0
        spacy_name_similarity = similarity(spacy_name.lower(), email_local_part)
    
        # Choose the name with higher similarity to the email's local part
        if first_line_similarity > spacy_name_similarity:
            name = first_line_name
        else:
            name = spacy_name
    else:
        # Default to the first line name if no SpaCy names found
        name = first_line_name

    return name, email, phone   

@app.post("/uploadfile")
async def create_upload_file(skills_required: str = Form(...), resume_files: list[UploadFile] = File(...)):
    responses = []

    try:
        skills_list = [skill.strip() for skill_with_slash in skills_required.split(',') for skill in skill_with_slash.split('/')]
        lower_skill_list = [normalize_skill(s) for s in skills_list]
        skills = set(lower_skill_list)

        for resume_file in resume_files:
            resume_contents = await resume_file.read()
            resume_pdf = BytesIO(resume_contents)
            text = extract_text_from_pdf(resume_pdf)

            skills_extracted = set(find_skills_in_text(text, skills))
            skills_missing = skills - skills_extracted
            name, email, phone = extract_contact_info(text)

            if email is None and phone is None:
                response_data = {
                    "success": False,
                    "responseMessage": "No valid contact info",
                    "responseCode": "404",
                    "data": {}
                }
            else:
                skill_rate = round((len(skills_extracted) / len(skills)) * 100, 2)
                response_data = {
                    "success": True,
                    "responseMessage": "Skills Matched",
                    "responseCode": "200",
                    "data": {
                        "skills_required": skills_required,
                        "confidence": f'{skill_rate}%',
                        "skills_extracted": list(skills_extracted),
                        "skills_missing": list(skills_missing),
                        "name": name,
                        "email": email if email else "no contact info",
                        "phone": int(phone) if phone else "no contact info",
                        # "text": text if text else "no text"
                    }
                }

            responses.append(response_data)

    except Exception as e:
        response_data = {
            "success": False,
            "responseMessage": f"Error: {str(e)}",
            "responseCode": "500",
            "data": {}
        }
        responses.append(response_data)

    return JSONResponse(content={"results": responses})
