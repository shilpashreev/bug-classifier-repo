# classifier.py
import os
import json
import xml.etree.ElementTree as ET
from pydantic import BaseModel, Field
from typing import Literal, Dict, Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# --- Pydantic Schema ---
class BugClassification(BaseModel):
    """Structured output for classifying a single bug report."""
    priority: Literal["High", "Medium", "Low"] = Field(
        description="The severity of the bug: High, Medium, or Low."
    )
    component: Literal["UI", "Backend", "Database", "API", "Testing"] = Field(
        description="The primary application component this bug affects."
    )
    is_valid_bug: bool = Field(
        description="True if the report is a valid bug; False if it is a feature request or irrelevant."
    )
    summary_of_bug: str = Field(
        description="A one-sentence summary of the bug and its impact."
    )

# --- File Loading Function ---
def load_file_content(file_path: str) -> str:
    """Reads and parses content from a JSON or XML file into a single string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if file_path.lower().endswith(".json"):
            json_data = json.loads(content)
            return json.dumps(json_data, indent=2)
        
        elif file_path.lower().endswith(".xml"):
            root = ET.fromstring(content)
            bug_text = []
            for elem in root.iter():
                if elem.text and elem.text.strip():
                    bug_text.append(f"{elem.tag.capitalize()}: {elem.text.strip()}")
            return "\n".join(bug_text)
            
        else:
            return f"Error: Unsupported file format for {file_path}"
            
    except Exception as e:
        return f"Error reading file: {e}"

# --- Classification Function ---
def classify_bug_report(file_path: str, bug_classification_schema: BaseModel) -> Dict[str, Any]:
    """
    Initializes the Gemini model and LangChain pipeline to classify the bug report.
    """
    
    file_content_str = load_file_content(file_path)
    if file_content_str.startswith("Error"):
        return {"error": file_content_str}
        
    # NOTE: Ensure GOOGLE_API_KEY is set in your environment
    if not os.getenv("GOOGLE_API_KEY"):
         print("WARNING: GOOGLE_API_KEY is not set. Classification will likely fail.")

    # 1. Initialize the Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0, 
    )

    # 2. Define the Structured Output Chain
    structured_llm = llm.with_structured_output(
        bug_classification_schema,
        method="json_mode" 
    )

    # 3. Define the Prompt Template
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an expert bug classification system. Classify the report according to the JSON schema."),
            ("human", "Classify the following bug report content:\n\n{bug_report_content}"),
        ]
    )

    # 4. Create the Classification Chain
    classification_chain = prompt | structured_llm

    # 5. Invoke the Chain
    result = classification_chain.invoke(
        {"bug_report_content": file_content_str}
    )
    # The result from structured_output is a Pydantic object, convert to dict for testing
    return result.dict()
