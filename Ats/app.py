from dotenv import load_dotenv
load_dotenv()
import base64
import io
import streamlit as st
import os
from PIL import Image
import pdf2image
import google.generativeai as genai

# Load and configure the Gemini API
api_key = os.getenv("GENAI_API_KEY")
if not api_key:
    st.error("API key not found. Please check your .env file.")
else:
    genai.configure(api_key=api_key)

# Initialize the Gemini 1.5 model
model = genai.GenerativeModel('gemini-1.5-flash')

# Function to get response from Generative AI
def get_gemini_response(input, pdf_content, prompt):
    try:
        response = model.generate_content([input, pdf_content[0], prompt])
        return response.text
    except Exception as e:
        st.error(f"Error while generating content: {e}")
        return None

# Function to convert PDF to image
def convert_pdf_to_image(pdf_path):
    try:
        if pdf_path is not None:
            images = pdf2image.convert_from_bytes(pdf_path.read())
            first_page = images[0]

            img_byte_arr = io.BytesIO()
            first_page.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()

            pdf_parts = [{
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode('utf-8')
            }]
            return pdf_parts
        else:
            raise FileNotFoundError("File not found")
    except Exception as e:
        st.error(f"Error converting PDF to image: {e}")
        return None

# Streamlit App Configuration
st.set_page_config(page_title="ATS Resume Expert", page_icon="🔮")
st.header("🔮 ATS Resume Expert")

input_text = st.text_area("Job Description", key="input", height=250)
uploaded_file = st.file_uploader("Upload a resume (PDF)...", type=["pdf"])

if uploaded_file:
    st.write("Resume uploaded successfully")

submit1 = st.button("Tell Me about the resume")
submit2 = st.button("How can I improve my resume?")
submit3 = st.button("Percentage Matched")

input_prompt1 = """
Analyze the following resume and corresponding job description to assess the candidate's fit for the role. Identify the candidate's key skills and experience that directly align with the job requirements. Additionally, highlight any relevant certifications, achievements, or projects that demonstrate their capabilities.

Next, evaluate the candidate's experience level and identify any potential gaps compared to the desired qualifications. Are there specific skills or areas of knowledge that may require additional training or experience?

Finally, based on your analysis, provide a score (e.g., 1-5) indicating the overall fit between the candidate's profile and the job description. Briefly explain the rationale behind your score.
"""

input_prompt2 = """
Skills: Identify the skills that are missing in regards to the description. Provide a list of skills that the candidate should consider adding to their resume to better align with the job requirements.

Experience: Evaluate the candidate's work experience and identify any gaps or areas that require further elaboration. Suggest specific examples or projects that could enhance the resume and demonstrate the candidate's qualifications.

Formatting: Review the resume's structure, layout, and overall presentation. Provide recommendations on how the candidate can improve the visual appeal and readability of their resume.
"""

input_prompt3 = """
You are a highly specialized ATS scanner with expertise in data science and resume parsing. Analyze the provided resume and corresponding job description.

Matching Score: Calculate a percentage score (0-100%) reflecting the overall match between the candidate's profile and the job requirements. This score should consider factors like:

Keyword Match: Identify and quantify the match between skills, experience, and qualifications listed in the resume and job description. Give in a paragraph manner that is more clear to understand. Only give the 10-15 most important keywords.

Missing Keywords: Identify and list the top 5-10 most critical skills or qualifications mentioned in the job description that are missing from the candidate's resume. Make it crisp.

Work Experience: Evaluate the relevance and depth of the candidate's experience compared to the desired years of experience and specific job duties.

Final Thoughts: Briefly summarize your assessment, including:

Key strengths of the candidate based on the resume-job description match.
Reasons for any significant gaps in the matching score.
Recommendation for further consideration based on the overall analysis (e.g., proceed to interview, needs additional information, not a strong fit).
"""

if submit1 or submit2 or submit3:
    if uploaded_file is not None:
        pdf_content = convert_pdf_to_image(uploaded_file)
        if pdf_content:  # Proceed only if conversion was successful
            if submit1:
                response = get_gemini_response(input_text, pdf_content, input_prompt1)
            elif submit2:
                response = get_gemini_response(input_text, pdf_content, input_prompt2)
            elif submit3:
                response = get_gemini_response(input_text, pdf_content, input_prompt3)
            
            if response:
                st.subheader("The Response is:")
                st.write(response)
        else:
            st.write("Failed to process the uploaded resume.")
    else:
        st.write("Please upload a resume first.")
