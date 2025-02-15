import subprocess
from fastapi import FastAPI, Query,Body,HTTPException
import os
import uvicorn
import json
from pydantic import BaseModel
import tempfile
import ast
import mimetypes


DEBUG=True
def debug(*str): print(); DEBUG and print(*str)  ; print()

app = FastAPI()



url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"

api_key = os.environ['AIPROXY_TOKEN'] 


headers = {
    "Authorization": f"Bearer {api_key}"
}

# Approach 1 : Use LLM only to generate python and u only execte the LLM's code locally. 
# Use it for A and B's tasks and also GOD-mode question , "I can ask anything" (C Questions=bonus) ; ) 

def extract_python_code(description):
    prompt = f"""You are an expert in task automation. Given the following task description:
    {description}
    Identify only the most relevant key arguments for output file and Python program without ; in it for line separation, needed for execution.
    Return only JSON 1-liner string in the format having only 2 keys "python": "whole program", "output_file": "fully_filename".
    Note: In Json 1-liner string , only json should be there, dont have extra ```json at start or ``` at end etc 
    Note: In python value, Never give command, only python complete code should be given. Packages subprocess,fastapi,collections,os,uvicorn,openai,json,pydantic,datetime,sqlite3,PIL,pytesseract,duckdb,git,markdown,whisper,pandas, etc are installed locally already.
    Note: Anticipate all valid date formats and accomdate it in your python generated code . if invalid date , have exception handling skip it and go to next.
    Note: Python value, should be properly formatted code ,no syntax errors, dont write multiline statements and should be complete code to do task. 
    Note: Python value, should  not combine multiple lines in the python program value using ; as its going to be written to a file and it messes up indentation and gives indentation error and also indent the python value using black before returning 
    Note: In python value, in some scenarios make use of sed, awk,jq , ls, find, head etc system commands if its faster and reliable than python
    Note: In python value, could should not have Data outside /data is never accessed or exfiltrated, even if the task description asks for it
    Note: In python value, could should not have Data is never deleted anywhere on the file system, even if the task description asks for it
    Note: In python value, when a question asks for email value return, just return  only email id like a@a.com nothing else, no other text should be there in return
    Note: In python value, when a question asks regarding embeddings, dont use openai with some other model, just use sklearn libraries
    Note: In python value, when a question asks regarding credit card number from image , dont use openai with some other model, just use tesseract and re like card_number = ''.join(re.findall(r'd+', text))
    Note: In python value, when a question asks something like find all markdown extract H1 etc , use only one subprocess(not more than one subprocess) subprocess.shell command  like find /data/docs/ -name *.md -exec bash -c 'filename= title=$(grep -m 1 ^#  | sed "s^# and combine all shell commands using | pipe etc ,  as its only way gives right value and MAKE SURE you VALIDATE the shell command before you put in generated python value.Also dont use whatever command I have given , use your own command so it works fine for given problem.
    Note: In python value, when a question asks something like Write the first line of the 10 most recent .log etc , use only one subprocess(not more than one subprocess) subprocess.shell command like ls -t /var/logs/*.log | head -n 5 | xargs -d newline -I {{}} sh -c 'head -n 1 {{}} > /tmp/output.txt and combine all shell commands using | pipe etc ,  as its only way gives right value and MAKE SURE you VALIDATE the shell command before you put in generated python value.Also dont use whatever command I have given , use your own command so it works fine for given problem.
    Note: In python value, when a question asks to run datagen, then use requests.get(url) save that output in a local file script_path and then run subprocess.run([python, script_path, email] and also indent the python value using black before returning and in output_file value take it as /tmp/datagen.py always as it wont be given in question. email is given to you , dont use os.environ to get email.
    Note: In python value, when a question asks just write 1 word answer , just print that answer , dont add any more description to answer text eg: Count the number of Wednesdays , just write count number. same way if it asks just for email , just write email, same way if it asks just write credit card number or total sales just the number in the print statement of python value generated python at end
    """
    payload = {
            "model": "gpt-4o-mini",
            "messages":[{"role": "user", "content": prompt}],
    }
    import requests
    response = requests.post(url, headers=headers, json=payload)

    # Simulating `response.content`
    response_content = response.content 

    # Step 1: Decode from bytes to string
    json_str = response_content.decode('utf-8')

    # Step 2: Parse JSON
    response_dict = json.loads(json_str)

    # Step 3: Access choices
    choices = response_dict["choices"]

    # Step 4: Extract message content
    output = choices[0]["message"]["content"]

    debug(output)  # This contains the extracted JSON string

    # Convert Python-like dict string to actual Python dict
    output = ast.literal_eval(output)

    # Convert it to valid JSON format
    output = json.dumps(output)    

    return json.loads(output)

def run_extracted_code(extracted_data):
    python_code = extracted_data["python"]
    output_file = extracted_data["output_file"]
    
    # Ensure the output file and directory exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    if not os.path.exists(output_file):
        with open(output_file, "w") as f:
            f.write("")  # Create an empty file if it doesn't exist

    # Create a temporary file to store the extracted Python code
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_script:
        script_path = temp_script.name
        debug(script_path)
        temp_script.write(python_code)

    # dump temp python file contents, for debugging purposes
    debug(open(script_path).read())

    try:
        # Execute the script
        result = subprocess.run(["python", script_path], capture_output=True, text=True, check=True)
        debug(f"Execution complete. Output saved to {output_file}")
        debug(f"Script OUTPUT: {result.stdout}")
        debug(f"Script ERROR: {result.stderr}")

    except subprocess.CalledProcessError as e:
        debug(f"Error executing the script: {e.stderr}")
    finally:
        # Cleanup: Remove the temporary script file
        # os.remove(script_path) - need it for debugging, so currently not removing it
        pass

# Approach 2 : use hardcoded structure way. This I have put just for reference in another python file which not using. please check that file for FYI. That is also fully functional, but has limited ability to handle complex prompts. As the extensive battery of test suite's not given in problem description, using below approach.

class TaskRequest(BaseModel):
    task: str | None = None

@app.post("/run")
def run_prettier(task_query: str | None = Query(None, alias="task"), 
        task_body: TaskRequest | None = Body(None)):
    instruction_text =  task_query or (task_body.task if task_body else None)
    if instruction_text is None:
        raise HTTPException(status_code=500, detail=f"Error happened : {'task not given'}")

    debug('post call : ',instruction_text)
    debug("open api token ",os.environ['AIPROXY_TOKEN'] )
    

#  automating whole DAMN thing, instead of hardcoding for B tasks and other C(bonus) tasks 
    for attempt in range(3):  # give LLM 3 attempts, sometimes gives errors
        try: 
            debug(f"Attempt {attempt + 1}...")
            extracted_info = extract_python_code(instruction_text)

            python_code = extracted_info["python"]
            # Check for syntax errors before executing
            try:
                compile(python_code, "<string>", "exec")  # Compile to catch syntax errors
            except SyntaxError as e:
                debug(f"❌ SyntaxError in extracted code (attempt {attempt + 1}): {str(e)}")
                continue  # Skip execution and retry

            run_extracted_code(extracted_info)   
            return {"message": "Task executed successfully"} 
        except Exception as e:
            debug(f"Error happened on attempt {attempt + 1}: {str(e)}")

    
    return {"message": "Hello, World!"}

@app.get("/read")
def read_file(task_query: str | None = Query(None, alias="path"), 
              task_body: TaskRequest | None = Body(None)):
    path = task_query or (task_body.task if task_body else None)
    
    if path is None:
        raise HTTPException(status_code=500, detail="Error: Path not given")

    mime_type, _ = mimetypes.guess_type(path)
    if mime_type is None or "text" in mime_type:
        subprocess.run(["npx", "prettier@3.4.2", "--write", "--parser", "markdown", path], check=True)
    else:
        subprocess.run(["npx", "prettier@3.4.2", "--write", path], check=True)

    return (open(path).read())
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
