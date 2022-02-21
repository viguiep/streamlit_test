import fpdf # PDF creation


class PDF(fpdf.FPDF):

    def header(self):
        title = 'Summarization of articles'
        self.set_font('Arial', 'B', 15) # Arial bold 15

        # Calculate width of title and position
        w = self.get_string_width(self.title) + 6
        self.set_x((210 - w) / 2)

        # Colors of frame, background and text
        self.set_draw_color(0, 80, 180)
        self.set_fill_color(230, 230, 0)
        self.set_text_color(220, 50, 50)

        self.set_line_width(1) # Thickness of frame (1 mm)
        self.cell(w, 9, title, 1, 1, 'C', 1) # Title
        self.ln(20) # Line break

    def footer(self):
        self.set_y(-15) # Position at 1.5 cm from bottom
        self.set_font('Arial', 'I', 8) # Arial italic 8
        self.set_text_color(128) # Text color in gray
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C') # Page number

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12) # Arial 12
        self.set_fill_color(200, 220, 255) # Background color
        self.cell(0, 6, title, 0, 1, 'L', 1) # Title
        self.ln(4) # Line break

    def chapter_body(self, content):
        txt = content.encode('utf-8').decode('latin-1')

        self.set_font('Arial', '', 11) # Times 12
        self.multi_cell(0, 5, txt) # Output justified text
        self.ln(10) # Line break

    def print_chapter(self, title, content):
        self.chapter_title(title)
        self.chapter_body(content)

def create_summary_pdf(summary_list, output_main_topics, my_remarks= 'I do not have any remark.'):
    pdf = PDF()
    pdf.set_title('Summarization of articles')
    pdf.set_author('Qoqaq.com')
    #fpdf.add_font("Arial", "", "arial.ttf", uni=True)
    pdf.add_page()
    pdf.print_chapter('Main topics', output_main_topics)
    summary_block = ''.join('- ' + sentence + '\n\n' for sentence in summary_list)
    pdf.print_chapter('Summary', summary_block)
    pdf.print_chapter('My remarks', my_remarks)
    pdf.output('Summary.pdf', 'F')
