# jd_parser.py

import os
import json
import sys
from dotenv import load_dotenv
from groq import Groq
from scoring_models import JobRequirements

def parse_jd_to_requirements(txt_path: str) -> JobRequirements:
    """Reads a raw text JD file and structures it into standardized requirements using Groq Cloud."""
    print(f"[1/4] Reading raw text JD from file: {txt_path}...")
    
    if not os.path.exists(txt_path):
        raise FileNotFoundError(f"Job Description file not found at: {txt_path}")
        
    with open(txt_path, "r", encoding="utf-8") as f:
        raw_content = f.read()
        
    # 1. Initialize and verify the Groq client connection
    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise ValueError(
            "❌ Missing Environment Variable: 'GROQ_API_KEY' could not be found. "
            "Please ensure your local .env file contains a valid token string."
        )
        
    groq_client = Groq(api_key=GROQ_API_KEY)
    
    # 2. System instructions incorporating the mandatory JSON object keywords and target_companies field
    system_prompt = (
        "You are an enterprise-grade ATS parsing engine. Your task is to analyze a raw Job Description "
        "and extract its core requirements into a valid, well-formed JSON object structural format.\n\n"
        "CRITICAL RULE FOR 'required_skills':\n"
        "You must ATOMIZE all skills. Do not extract sentences, descriptions, or grouped clauses. "
        "If a requirement lists multiple technologies, frameworks, or tools (even inside parentheses), "
        "you must break them apart into individual, isolated string elements.\n\n"
        "--- ABSTRACT EXAMPLES OF THE EXPECTED BEHAVIOR ---\n"
        "Input text: 'Proficient in tool clustering platforms (AlphaTool, BetaFramework, GammaKit)'\n"
        "Output list: ['AlphaTool', 'BetaFramework', 'GammaKit']\n"
        "---------------------------------------------------\n\n"
        "OUTPUT REQUIREMENT:\n"
        "Analyze the provided text and output a pure JSON object mapping exactly to this structure:\n"
        "{\n"
        "  \"required_skills\": [\"string\"],\n"
        "  \"target_experience_months\": 0,\n"
        "  \"target_seniority\": \"string\",\n"
        "  \"target_companies\": [\"string\"]\n"  # <-- Restored field to pass Pydantic validation
        "}\n\n"
        "Note for 'target_companies': If the job description explicitly mentions preferred target companies, background organizations, "
        "or direct industry competitors to source candidates from, extract them here. If none are specified, leave it as an empty list []."
    )
    
    print("⚡ [Groq Engine] Normalizing unstructured JD criteria to schema targets...")
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extract from this raw text Job Description:\n\n{raw_content}"}
            ],
            temperature=0.0,
            max_tokens=1024,
            response_format={"type": "json_object"}
        )
        
        # 3. Extract payload and compile back to target validation structures
        json_payload_string = response.choices[0].message.content.strip()
        print("[3/3] Job Description extraction and normalization complete.")
        
        return JobRequirements.model_validate_json(json_payload_string)
        
    except Exception as e:
        print(f"❌ [JD PARSER CRASH] Failed to route or compile requirement models: {str(e)}")
        raise e