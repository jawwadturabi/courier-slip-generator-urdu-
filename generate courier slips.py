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
    This version excludes the 'From:' section and any organization heading,
    and uses multi_cell() for the address to wrap text automatically.
    """
    spacing     = 5
    y_position  = 10 + label_index * (label_height + spacing)
    x_position  = margin_left
    label_width = 210 - 20  # 10 mm margins on left+right

    # 1) Draw the box
    pdf.rect(x_position, y_position, label_width, label_height)

    # 2) Temporarily disable auto page‐breaks while we fill this box
    old_auto, old_margin = pdf.auto_page_break, pdf.b_margin
    pdf.set_auto_page_break(False, 0)

    # 3) Move inside the box
    pdf.set_xy(x_position, y_position + 5)

    # ---- "To:" ----
    pdf.set_font("Arial", "B", 12)
    pdf.set_x(x_position + 5)
    pdf.cell(label_width - 10, 8, "To:", ln=1)

    # ---- Name ----
    pdf.set_font("NotoNastaliq", "", 10)
    pdf.set_x(x_position + 5)
    pdf.cell(label_width - 10, 6, f"Name: {reshape_text(student['Name'])}", ln=1)

    # ---- Address (auto‐wrapping) ----
    address_txt = f"Address: {reshape_text(student['Address'])}"
    pdf.set_x(x_position + 5)
    pdf.multi_cell(label_width - 10, 6, address_txt, border=0)

    # ---- Mobile ----
    pdf.set_x(x_position + 5)
    pdf.cell(label_width - 10, 6, f"Mobile: {student['Mobile']}", ln=1)

    # ---- Congratulations message (auto‐wrapping) ----
    msg = "درسِ نظامی میں شاندار کامیابی پر دل کی گہرائیوں سے مبارک باد! اسے تحفے کے طور پر قبول فرمائیں۔ شکریہ!"
    pdf.set_x(x_position + 5)
    pdf.multi_cell(label_width - 10, 5, reshape_text(msg), border=0, align="R")

    # 4) Restore auto page‐break behavior
    pdf.set_auto_page_break(old_auto, old_margin)

def main():
    # Create the PDF: A4, portrait, measuring in mm
    pdf = LabelPDF(orientation="P", unit="mm", format="A4")
    
    # Register Unicode fonts; ensure these TTF files are in your project directory.
    pdf.add_font('NotoNastaliq', "", "NotoNaskhArabic-VariableFont_wght.ttf", uni=True)  
    
    # Set the number of labels per page (you can adjust this as needed)
    labels_per_page = 5
    margin_left = 10

    # Calculate label height dynamically for A4 page, accounting for margins and spacing.
    margin_top = 10
    margin_bottom = 10
    spacing = 5  # vertical spacing between labels in mm
    available_height = 297 - margin_top - margin_bottom - (labels_per_page - 1) * spacing
    label_height = available_height / labels_per_page

    with open("Sheet6.csv", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        label_count = 0
        for student in reader:
            # Add a new page whenever we reach the number of labels per page
            if label_count % labels_per_page == 0:
                pdf.add_page()
            position = label_count % labels_per_page
            draw_label(pdf, student, position, label_height, margin_left)
            label_count += 1

    pdf.output("Sheet6.pdf")
    print("PDF generated successfully as 'Sheet6.pdf'.")

if __name__ == '__main__':
    main()
