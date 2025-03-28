import streamlit as st
import google.generativeai as genai
from pdf2image import convert_from_bytes
import base64
from io import BytesIO

# Configure Gemini API
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key) 
model = genai.GenerativeModel("gemini-1.5-flash")  # Updated model

# Streamlit interface
st.title("OCR with Gemini API")
uploaded_file = st.file_uploader(
    "Upload a document (PDF or Image)", 
    type=["pdf", "png", "jpg", "jpeg"]
)

# Initialize images variable
images = None

if uploaded_file is not None:
    # Display file upload confirmation
    st.write("File uploaded successfully:", uploaded_file.name)

    # Preprocess file and display preview
    if uploaded_file.type == "application/pdf":
        # Convert PDF to list of images
        images = convert_from_bytes(uploaded_file.read())
        st.write(f"Converted PDF to {len(images)} image(s)")

        # Display preview of the first page
        st.subheader("Preview of the First Page:")
        st.image(images[0], caption="First page of the PDF", use_column_width=True)
    else:
        # For image files, use directly
        images = [uploaded_file]
        st.write("Image file ready for processing")

        # Display preview of the image
        st.subheader("Preview of the Uploaded Image:")
        st.image(uploaded_file, caption="Uploaded image", use_column_width=True)

    # Extract text with Gemini API
    if images:
        st.write("Processing with Gemini API...")
        
        # Convert the first image to base64 for the API
        if uploaded_file.type == "application/pdf":
            # For PDFs, images[0] is a PIL image
            buffered = BytesIO()
            images[0].save(buffered, format="PNG")
            img_bytes = buffered.getvalue()
        else:
            # For images, read the uploaded file directly
            img_bytes = uploaded_file.read()
        
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")

        # Prepare the content for the API
        prompt = "Extract all text from this image."
        content = [
            {"text": prompt},
            {
                "inline_data": {
                    "mime_type": "image/png",
                    "data": img_base64
                }
            }
        ]

        # Call the API with error handling
        try:
            response = model.generate_content(content)
            extracted_text = response.text
            st.write("Extracted Text:")
            st.write(extracted_text)
        except Exception as e:
            st.error(f"Error processing with Gemini API: {str(e)}")