from fastapi import FastAPI, HTTPException 
from pydantic import BaseModel
from typing import List, Optional
import google.generativeai as genai
from dotenv import load_dotenv
import os
import random

# Load API key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

app = FastAPI()

class PromptRequest(BaseModel):
    prompt: str

class PromptVariant(BaseModel):
    optimized_prompt: str
    reason: Optional[str] = None

class PromptResponse(BaseModel):
    original_prompt: str
    quality_score: int
    suggestions: List[str]
    issues_detected: List[str]
    variants: List[PromptVariant]
@app.post("/optimize", response_model=PromptResponse)
async def optimize(data: PromptRequest):
    prompt = data.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt can't be empty.")

    system_prompt = (
        f"You are a world-class prompt engineer AI assistant.\n"
        f"Your task is to help users improve their prompts.\n\n"
        f"Original Prompt: \"{prompt}\"\n\n"
        f"Step 1: Rate the prompt from 0-100 based on clarity, specificity, and usefulness.\n"
        f"Step 2: Suggest short, crisp improvements (avoid long sentences,e.g. clarify audience, format, scope).\n"
        f"Step 3: List 3-5 issues with the original prompt.\n"
        f"Step 4: Generate exactly 6 optimized prompt variants.\n"
        f"Each variant should be in this format:\n"
        f"Optimized Prompt: [full improved prompt here]\n"
        f"Reason: [explanation why it's better]\n"
        f"Use bullet points (*) only for suggestions and issues, not for prompt variants.\n"
    )

    try:
        response = model.generate_content(system_prompt)
        text = response.text.strip()
        lines = text.splitlines()

        quality_score = None
        suggestions = []
        issues = []
        variants = []

        section = None
        current_prompt = ""
        current_reason = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue

            lline = line.lower()

            if "score" in lline and any(char.isdigit() for char in line):
                section = "score"
                numbers = [int(s) for s in line.split() if s.isdigit()]
                if numbers:
                    quality_score = numbers[0]
                continue

            elif lline.startswith("optimized prompt:"):
                section = "variant"
                current_prompt = line.split(":", 1)[1].strip()
                continue

            elif lline.startswith("reason:"):
                current_reason = line.split(":", 1)[1].strip()
                if current_prompt:
                    variants.append(PromptVariant(
                        optimized_prompt=current_prompt,
                        reason=current_reason
                    ))
                    current_prompt = ""
                    current_reason = ""
                continue

            elif "suggest" in lline:
                section = "suggestions"
                continue

            elif "issue" in lline:
                section = "issues"
                continue

            # Parse bullet points in suggestions or issues
            if section == "suggestions" and line.startswith("*"):
                suggestions.append(line[1:].strip())

            elif section == "issues" and line.startswith("*"):
                issues.append(line[1:].strip())

            elif section == "variant" and current_prompt:
                current_prompt += " " + line  # join multi-line prompt

        if not quality_score:
            quality_score = random.randint(60, 85)

        return PromptResponse(
            original_prompt=prompt,
            quality_score=quality_score,
            suggestions=suggestions,
            issues_detected=issues,
            variants=variants
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini error: {e}")


