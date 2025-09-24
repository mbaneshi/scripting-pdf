import streamlit as st
import os
import pandas as pd
from database import create_tables, save_pdf_document, get_documents, get_document_by_id
from pdf_extractor import extract_text_with_metadata, validate_pdf
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="PDF Translation SaaS",
    page_icon="📄",
    layout="wide"
)

# Initialize database tables
@st.cache_resource
def init_database():
    create_tables()
    return True

init_database()

# Main title
st.title("📄 PDF Translation SaaS Platform")
st.markdown("Extract text from PDFs and prepare for AI translation")

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page", ["Upload PDF", "View Documents", "Extract Text"])

if page == "Upload PDF":
    st.header("Upload PDF Document")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload a PDF file to extract text"
    )
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Validate PDF
        if validate_pdf(temp_path):
            st.success(f"✅ Valid PDF: {uploaded_file.name}")
            
            # Extract text button
            if st.button("Extract Text and Save to Database"):
                with st.spinner("Extracting text from PDF..."):
                    try:
                        # Extract text and metadata
                        result = extract_text_with_metadata(temp_path)
                        
                        # Save to database
                        doc_id = save_pdf_document(
                            filename=result["filename"],
                            text=result["text"],
                            file_size=result["file_size"],
                            page_count=result["page_count"]
                        )
                        
                        st.success(f"✅ Text extracted and saved! Document ID: {doc_id}")
                        
                        # Display summary
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Pages", result["page_count"])
                        with col2:
                            st.metric("File Size", f"{result['file_size'] / 1024:.1f} KB")
                        with col3:
                            st.metric("Characters", len(result["text"]))
                        
                        # Show preview of extracted text
                        st.subheader("Text Preview (First 500 characters)")
                        st.text_area("Extracted Text", result["text"][:500] + "...", height=200)
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                    finally:
                        # Clean up temp file
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
        else:
            st.error("❌ Invalid PDF file")

elif page == "View Documents":
    st.header("Stored Documents")
    
    # Get all documents
    documents = get_documents()
    
    if documents:
        # Create DataFrame for display
        data = []
        for doc in documents:
            data.append({
                "ID": doc.id,
                "Filename": doc.filename,
                "Pages": doc.page_count,
                "Size (KB)": f"{doc.file_size / 1024:.1f}" if doc.file_size else "N/A",
                "Extracted": doc.extracted_at.strftime("%Y-%m-%d %H:%M") if doc.extracted_at else "N/A",
                "Processed": "✅" if doc.processed else "❌"
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
        # Document details
        st.subheader("Document Details")
        selected_id = st.selectbox("Select Document ID", [doc.id for doc in documents])
        
        if selected_id:
            doc = get_document_by_id(selected_id)
            if doc:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Filename:** {doc.filename}")
                    st.write(f"**Pages:** {doc.page_count}")
                    st.write(f"**Size:** {doc.file_size / 1024:.1f} KB" if doc.file_size else "N/A")
                    st.write(f"**Extracted:** {doc.extracted_at}")
                
                with col2:
                    st.write(f"**Status:** {'Processed' if doc.processed else 'Pending'}")
                    st.write(f"**Text Length:** {len(doc.original_text) if doc.original_text else 0} characters")
                
                # Show text preview
                if doc.original_text:
                    st.subheader("Text Preview")
                    preview_length = st.slider("Preview Length", 100, 2000, 500)
                    st.text_area("Extracted Text", doc.original_text[:preview_length] + "...", height=300)
    else:
        st.info("No documents found. Upload a PDF first.")

elif page == "Extract Text":
    st.header("Extract Text from Existing PDF")
    
    # List existing PDFs in directory
    pdf_files = [f for f in os.listdir(".") if f.endswith(".pdf")]
    
    if pdf_files:
        selected_pdf = st.selectbox("Select PDF file", pdf_files)
        
        if selected_pdf:
            st.write(f"Selected: **{selected_pdf}**")
            
            if st.button("Extract and Save"):
                with st.spinner("Processing PDF..."):
                    try:
                        result = extract_text_with_metadata(selected_pdf)
                        
                        # Save to database
                        doc_id = save_pdf_document(
                            filename=result["filename"],
                            text=result["text"],
                            file_size=result["file_size"],
                            page_count=result["page_count"]
                        )
                        
                        st.success(f"✅ Successfully processed! Document ID: {doc_id}")
                        
                        # Display results
                        st.subheader("Extraction Results")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Pages", result["page_count"])
                        with col2:
                            st.metric("File Size", f"{result['file_size'] / 1024:.1f} KB")
                        with col3:
                            st.metric("Characters", len(result["text"]))
                        
                        # Show metadata
                        if result["metadata"]:
                            st.subheader("PDF Metadata")
                            metadata_df = pd.DataFrame(list(result["metadata"].items()), columns=["Property", "Value"])
                            st.dataframe(metadata_df, use_container_width=True)
                        
                        # Text preview
                        st.subheader("Text Preview")
                        preview_length = st.slider("Preview Length", 100, 2000, 500)
                        st.text_area("Extracted Text", result["text"][:preview_length] + "...", height=300)
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    else:
        st.info("No PDF files found in the current directory.")

# Footer
st.markdown("---")
st.markdown("**PDF Translation SaaS Platform** - Ready for AI integration")
