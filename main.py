from fastapi import FastAPI, HTTPException
import subprocess
import json
from openai import OpenAI
import os

app = FastAPI()

client = OpenAI( api_key=os.getenv("OPENAI_API_KEY"))
if not client:
    raise Exception("OPENAI_API_KEY environment variable not set")


@app.get("/scan")
def run_bandit_scan():
    
    command = ["bandit", "-r", "./badscript.py", "-f", "json"]

    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.stdout:
        output = json.loads(result.stdout)
    else:
        output = {"error": "No output from Bandit or an error occurred."}

    return output


@app.get("/scan-and-fix")
async def scan_and_fix_script():
    script_path = './badscript.py'

    command = ["bandit", "-r", script_path, "-f", "json"]
    bandit_result = subprocess.run(command, capture_output=True, text=True)
    bandit_output = json.loads(bandit_result.stdout) if bandit_result.stdout else {}

    try:
        with open(script_path, 'r') as file:
            script_content = file.read()
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Failed to read script file: {str(e)}")

    prompt = f"The following Python script has security issues as identified by a Bandit scan:\n\n{script_content}\n\nBandit scan results:\n{json.dumps(bandit_output, indent=2)}\n\nPlease rewrite the script to fix these security issues."
    
    try:
        chat_completion = client.chat.completions.create(
        messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
    model="gpt-3.5-turbo",
)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API call failed: {str(e)}")

    return {"suggestions": chat_completion}
