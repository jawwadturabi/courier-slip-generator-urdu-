import csv
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display

def reshape_text(text):
    """
    Reshapes and reorders Arabic/Urdu text for correct display in PDFs.
    Only needed if your data includes Urdu. 
    """
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

class LabelPDF(FPDF):
    def header(self):
        # No header needed; override to leave this blank.
        pass
        
    def footer(self):
        # Print the page number at the bottom (using regular style, not italic)
        self.set_y(-15)
        self.set_font("Arial", "", 8)
        self.cell(0, 16, f"Page {self.page_no()}", 0, 0, "C")

def draw_label(pdf, student, label_index, label_height, margin_left):
    """
    Draw a receipt/label for a student. 
    This version excludes the 'From:' section and any organization heading.
    """
    spacing = 5  # spacing between labels in mm
    y_position = 10 + label_index * (label_height + spacing)
    x_position = margin_left
    label_width = 210 - 20  # Using 10 mm left/right margins

    # Optionally draw a border around each label
    pdf.rect(x_position, y_position, label_width, label_height)

    # Set the cursor position with a small inset from the border
    pdf.set_xy(x_position, y_position + 5)

    # "To:" section for the student details
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "To:", ln=1)
    pdf.set_font("NotoNastaliq", "", 10)
    pdf.cell(0, 6, f"Name: {reshape_text(student['Name'])}", ln=1)
    pdf.cell(0, 6, f"Address: {reshape_text(student['Address'])}", ln=1)
    pdf.cell(0, 6, f"Mobile: {student['Mobile']}", ln=1)
    
    pdf.ln(4)
    pdf.set_font("NotoNastaliq", "", 12)
    pdf.multi_cell(
        label_width - 10,  # width with some padding
        5, 
        reshape_text("درسِ نظامی میں شاندار کامیابی پر دل کی گہرائیوں سے مبارک باد! اسے تحفے کے طور پر قبول فرمائیں۔ شکریہ!"),
        border=0
    )

def main():
    # Create the PDF: A4, portrait, measuring in mm
    pdf = LabelPDF(orientation="P", unit="mm", format="A4")
    
    # Register Unicode fonts; ensure these TTF files are in your project directory.
    # pdf.add_font('NotoNastaliq', '', 'NotoNastaliqSans.ttf', uni=True)
    # pdf.add_font('NotoNastaliq', 'B', 'NotoNastaliqSans-Bold.ttf', uni=True)
    pdf.add_font('NotoNastaliq',"", "NotoNaskhArabic-VariableFont_wght.ttf", uni=True)  
    
    # Set the number of labels per page (you can adjust this as needed)
    labels_per_page = 5
    margin_left = 10

    # Calculate label height dynamically for A4 page, accounting for margins and spacing.
    margin_top = 10
    margin_bottom = 10
    spacing = 5  # vertical spacing between labels in mm
    available_height = 297 - margin_top - margin_bottom - (labels_per_page - 1) * spacing
    label_height = available_height / labels_per_page

    with open("Karachi Only.csv", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        label_count = 0
        for student in reader:
            # Add a new page whenever we reach the number of labels per page
            if label_count % labels_per_page == 0:
                pdf.add_page()
            position = label_count % labels_per_page
            draw_label(pdf, student, position, label_height, margin_left)
            label_count += 1

    pdf.output("Karachi Only.pdf")
    print("PDF generated successfully as 'Karachi Only.pdf'.")

if __name__ == '__main__':
    main()
