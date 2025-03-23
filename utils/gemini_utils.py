"""
Gemini API utilities for PDF parsing and structured data extraction
"""
import os
import base64
import logging
from typing import Optional, Dict, Any
import google.generativeai as genai

logger = logging.getLogger(__name__)

def setup_gemini_api():
    """
    Set up the Gemini API with the API key from environment variables
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable not set")
        return False
    
    genai.configure(api_key=api_key)
    return True

def encode_pdf_to_base64(file_path: str) -> Optional[str]:
    """
    Encode a PDF file to base64 for sending to Gemini API
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Base64-encoded string of the PDF file or None if error
    """
    try:
        with open(file_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
            base64_encoded = base64.b64encode(pdf_bytes).decode("utf-8")
            return base64_encoded
    except Exception as e:
        logger.error(f"Error encoding PDF to base64: {e}")
        return None

def parse_pdf_with_gemini(file_path: str) -> Optional[str]:
    """
    Parse a PDF file using Gemini Flash 2.0 and return structured markdown
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Structured markdown string or None if error
    """
    try:
        # Set up Gemini API
        if not setup_gemini_api():
            return None
        
        # Encode PDF to base64
        base64_pdf = encode_pdf_to_base64(file_path)
        if not base64_pdf:
            return None
        
        # Create a model instance
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Prepare the prompt
        prompt = """
        Convert this court cause list PDF to structured markdown format, maintaining all the original information exactly as it appears in the document. Your output must be a true and accurate representation of the PDF content.

        Include the following information in your markdown:
        1. Court name and number exactly as shown in the document
        2. Judge name(s) with exact spelling and formatting as in the document
        3. Date of the cause list as it appears in the document
        4. Type of cause list (e.g., Regular, Supplementary) as specified in the document
        5. All cases listed with their:
           - Case number exactly as formatted in the document
           - Parties involved with exact names as written
           - Any additional information present in the document

        IMPORTANT GUIDELINES:
        - Preserve all information exactly as it appears in the PDF
        - Do not add any interpretations, summaries, or information not present in the original
        - Maintain the same organization and structure of information as in the original
        - Use appropriate markdown formatting (headings, lists, tables) to represent the structure
        - If any information is not available in the document, do not include it or indicate it's not present
        - Do not alter case numbers, names, or any other text from how it appears in the source
        
        DO NOT include any explanatory text, comments, or notes before or after the markdown content.
        DO NOT start with phrases like "Here's the structured markdown" or "Okay, here's the".
        DO NOT wrap the output in markdown code blocks (```).
        ONLY output the raw markdown content directly.
        """
        
        # Create the content parts
        content_parts = [
            {"text": prompt},
            {
                "inline_data": {
                    "mime_type": "application/pdf",
                    "data": base64_pdf
                }
            }
        ]
        
        # Generate the response
        response = model.generate_content(
            content_parts,
            generation_config=genai.GenerationConfig(
                temperature=0.0,  # Lower temperature for more factual responses
                max_output_tokens=4096,  # Limit output size
                response_mime_type="text/plain"  # Ensure plain text response
            )
        )
        
        # Return the structured markdown
        return response.text
    
    except Exception as e:
        logger.error(f"Error parsing PDF with Gemini: {e}")
        return None

def save_markdown_output(file_path: str, markdown_content: str) -> Optional[str]:
    """
    Save the markdown content to a file
    
    Args:
        file_path: Path to the PDF file
        markdown_content: Markdown content to save
        
    Returns:
        Path to the saved markdown file or None if error
    """
    try:
        # Create the markdown file path by changing the extension
        markdown_path = os.path.splitext(file_path)[0] + ".md"
        
        # Clean the markdown content
        # Remove any markdown code block markers
        cleaned_content = markdown_content.strip()
        if cleaned_content.startswith("```markdown"):
            cleaned_content = cleaned_content[len("```markdown"):].strip()
        elif cleaned_content.startswith("```"):
            cleaned_content = cleaned_content[3:].strip()
            
        if cleaned_content.endswith("```"):
            cleaned_content = cleaned_content[:-3].strip()
            
        # Remove any explanatory text at the beginning
        common_prefixes = [
            "Here's the structured markdown output:",
            "Here's the structured markdown:",
            "Okay, here's the structured markdown",
            "Here is the structured markdown",
            "The structured markdown is as follows:",
            "I've analyzed the PDF and extracted the following information:"
        ]
        
        for prefix in common_prefixes:
            if cleaned_content.startswith(prefix):
                cleaned_content = cleaned_content[len(prefix):].strip()
        
        # Write the cleaned markdown content to the file
        with open(markdown_path, "w", encoding="utf-8") as md_file:
            md_file.write(cleaned_content)
        
        return markdown_path
    
    except Exception as e:
        logger.error(f"Error saving markdown output: {e}")
        return None
