# Resume Analyzer API

## Overview

The Resume Analyzer API is a FastAPI application designed to analyze resumes (PDF files) and extract relevant skills, contact information, and other pertinent details. The API takes multiple PDF resumes as input and compares the skills listed in the resumes against the required skills provided by the user. It also returns information regarding matched and missing skills along with the confidence level for each resume analyzed.

## Features

- Upload multiple PDF resumes.
- Extract skills and contact information from resumes.
- Compare extracted skills with required skills.
- Return a structured JSON response with analysis results.

## Requirements

- Python 3.7 or later
- FastAPI
- Uvicorn
- Pydantic
- PyPDF2 (or another PDF processing library)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
