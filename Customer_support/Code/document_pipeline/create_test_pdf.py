"""
Script to create a sample PDF with CPSC text for testing.
Run this to generate test PDF: python create_test_pdf.py
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from pathlib import Path

# CPSC Text content
CPSC_TEXT = """
U.S. Consumer Product Safety Commission (CPSC)

Introduction

The U.S. Consumer Product Safety Commission (CPSC or Commission), established by Congress in 1972, is an independent federal regulatory agency charged with reducing unreasonable risks of injury and death associated with consumer products.

Mission and Goals

The CPSC achieves that goal through education, safety standards activities, regulation, and enforcement of the statutes and implementing regulations.

The CPSC has jurisdiction over thousands of types of consumer products used in the home, in schools, in recreation, or otherwise.

Legislative Authority

To carry out its mission, CPSC administers seven statutes passed by Congress (the Acts). They are:

1. Consumer Product Safety Act (CPSA) - The primary statute establishing the CPSC
2. Federal Hazardous Substances Act (FHSA) - Regulates hazardous household products
3. Flammable Fabrics Act (FFA) - Sets flammability standards for clothing and textiles
4. Poison Prevention Packaging Act (PPPA) - Requires child-resistant packaging
5. Refrigerator Safety Act (RSA) - Prevents child entrapment hazards
6. Virginia Graeme Baker Pool and Spa Safety Act (VGB Act) - Pool and spa drain safety
7. Children's Gasoline Burn Prevention Act (CGBPA) - Regulates portable fuel containers

Scope of Regulation

The Commission works to ensure that consumer products are safe for families and individuals across the United States. The CPSC's jurisdiction covers:

- Household appliances and electronics
- Children's toys and products
- Recreational equipment
- Furniture and home furnishings
- Personal care items
- Garden and outdoor equipment

How CPSC Operates

Education and Outreach

The CPSC conducts public awareness campaigns to educate consumers about product safety and hazard prevention.

Standards Development

Working with industry and stakeholders to develop voluntary and mandatory safety standards for consumer products.

Regulatory Enforcement

The CPSC has the authority to:
- Issue recalls of hazardous products
- Ban dangerous products from the marketplace
- Impose fines and penalties on violators
- Conduct investigations and inspections

Data Collection and Analysis

The Commission maintains databases of injury reports, product incidents, and safety data to identify emerging hazards and trends.

Consumer Protection

The CPSC's work directly impacts American families by:
- Preventing an estimated thousands of deaths annually
- Reducing product-related injuries
- Ensuring children's products meet strict safety standards
- Providing safety information to consumers

Historical Context

Since its establishment in 1972, the CPSC has been at the forefront of consumer protection. The agency was created in response to growing concerns about product safety and the need for a dedicated federal body to oversee consumer product regulations.

Throughout its history, the CPSC has adapted to emerging challenges, from addressing new technologies to responding to evolving consumer needs. The Commission continues to play a vital role in protecting American consumers from unsafe products.

Contact and Resources

Consumers can report unsafe products and get safety information through:
- CPSC Hotline: 1-800-638-2772
- Website: www.cpsc.gov
- SaferProducts.gov database

Conclusion

The Consumer Product Safety Commission remains committed to its mission of protecting the public from unreasonable risks of injury and death associated with consumer products. Through education, regulation, and enforcement, the CPSC continues to make American homes, schools, and communities safer for everyone.
"""

def create_cpsc_pdf(output_path: str):
    """Create a PDF with CPSC text content."""
    
    # Create PDF
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=4))
    
    # Split text into paragraphs and add to document
    paragraphs = CPSC_TEXT.strip().split('\n\n')
    
    for para in paragraphs:
        if para.strip():
            # Use heading style for titles
            if len(para) < 50 and para.strip() and not para.strip()[0].isdigit():
                p = Paragraph(para.strip(), styles['Heading2'])
            else:
                p = Paragraph(para.strip().replace('\n', '<br/>'), styles['BodyText'])
            
            elements.append(p)
            elements.append(Spacer(1, 12))
    
    # Build PDF
    doc.build(elements)
    print(f"✓ Created PDF: {output_path}")

def main():
    """Main function to create test PDF."""
    # Determine output path
    current_dir = Path(__file__).parent
    data_dir = current_dir.parent.parent / "Data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = data_dir / "CPSC_Overview.pdf"
    
    print(f"Creating CPSC test PDF at: {output_path}")
    
    try:
        create_cpsc_pdf(str(output_path))
        print(f"\n✓ Success! PDF created at:")
        print(f"  {output_path}")
        print(f"\nNow you can run the ingestion pipeline:")
        print(f"  python main.py")
    except Exception as e:
        print(f"\n✗ Error creating PDF: {e}")
        print(f"\nIf reportlab is not installed, run:")
        print(f"  pip install reportlab")

if __name__ == "__main__":
    main()
