"""
Script to extract images from ICT619_Project_Documentation.docx
Requires: pip install python-docx pillow
"""

import os
import zipfile
from pathlib import Path

def extract_images_from_docx(docx_path, output_dir="docs/images"):
    """
    Extract all images from a .docx file.
    
    .docx files are actually ZIP archives containing XML and media files.
    Images are stored in word/media/ directory inside the ZIP.
    """
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    docx_path = Path(docx_path)
    
    if not docx_path.exists():
        print(f"❌ File not found: {docx_path}")
        return []
    
    print(f"📄 Extracting images from: {docx_path}")
    
    extracted_images = []
    
    try:
        # .docx files are ZIP archives
        with zipfile.ZipFile(docx_path, 'r') as docx_zip:
            # List all files in the archive
            all_files = docx_zip.namelist()
            
            # Find all image files in word/media/
            image_files = [f for f in all_files if f.startswith('word/media/')]
            
            if not image_files:
                print("⚠️  No images found in the document")
                return []
            
            print(f"📸 Found {len(image_files)} image(s)")
            
            # Extract each image
            for img_file in image_files:
                # Get the filename
                img_filename = os.path.basename(img_file)
                
                # Determine file extension
                ext = os.path.splitext(img_filename)[1] or '.png'
                
                # Create output path
                output_path = Path(output_dir) / img_filename
                
                # Extract the image
                with docx_zip.open(img_file) as source:
                    with open(output_path, 'wb') as target:
                        target.write(source.read())
                
                extracted_images.append(str(output_path))
                print(f"✅ Extracted: {img_filename} -> {output_path}")
            
            print(f"\n🎉 Successfully extracted {len(extracted_images)} image(s) to {output_dir}/")
            
    except zipfile.BadZipFile:
        print(f"❌ Error: {docx_path} is not a valid .docx file")
    except Exception as e:
        print(f"❌ Error extracting images: {e}")
    
    return extracted_images


def extract_images_alternative(docx_path, output_dir="docs/images"):
    """
    Alternative method using python-docx library (if available)
    """
    try:
        from docx import Document
        from docx.document import Document as _Document
        from docx.oxml.text.paragraph import CT_P
        from docx.oxml.table import CT_Tbl
        from docx.table import _Cell, Table
        from docx.text.paragraph import Paragraph
        
        docx_path = Path(docx_path)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        print(f"📄 Opening document with python-docx: {docx_path}")
        doc = Document(str(docx_path))
        
        extracted_images = []
        image_count = 0
        
        # Extract images from document relationships
        for rel in doc.part.rels.values():
            if "image" in rel.target_ref:
                image_count += 1
                img_data = rel.target_part.blob
                img_ext = rel.target_ref.split('.')[-1] if '.' in rel.target_ref else 'png'
                img_filename = f"image_{image_count}.{img_ext}"
                output_path = Path(output_dir) / img_filename
                
                with open(output_path, 'wb') as f:
                    f.write(img_data)
                
                extracted_images.append(str(output_path))
                print(f"✅ Extracted: {img_filename} -> {output_path}")
        
        if extracted_images:
            print(f"\n🎉 Successfully extracted {len(extracted_images)} image(s) to {output_dir}/")
        else:
            print("⚠️  No images found using python-docx method")
        
        return extracted_images
        
    except ImportError:
        print("⚠️  python-docx not installed. Using ZIP method instead.")
        return None
    except Exception as e:
        print(f"⚠️  Error with python-docx method: {e}")
        return None


if __name__ == "__main__":
    docx_file = "ICT619_Project_Documentation.docx"
    output_directory = "docs/images"
    
    print("=" * 60)
    print("🖼️  Image Extractor for Word Documents")
    print("=" * 60)
    print()
    
    # Try python-docx method first (more reliable)
    images = extract_images_alternative(docx_file, output_directory)
    
    # Fallback to ZIP method
    if not images:
        print("\n📦 Trying ZIP extraction method...")
        images = extract_images_from_docx(docx_file, output_directory)
    
    if images:
        print("\n" + "=" * 60)
        print("📋 Extracted Images:")
        print("=" * 60)
        for i, img in enumerate(images, 1):
            print(f"{i}. {img}")
        print("\n💡 You can now update ReadmeFirst.MD with these image paths!")
    else:
        print("\n❌ No images were extracted. Please check:")
        print("   1. The .docx file exists and is valid")
        print("   2. The document contains images")
        print("   3. Try installing: pip install python-docx")

