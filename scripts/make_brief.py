"""Optional release-document generator. Requires ReportLab, not used by the app."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'submission/TraceSol_Project_Brief.pdf'
FONT=Path('C:/Windows/Fonts/segoeui.ttf')
BOLD=Path('C:/Windows/Fonts/segoeuib.ttf')
if FONT.exists():
    pdfmetrics.registerFont(TTFont('UI',str(FONT)))
    pdfmetrics.registerFont(TTFont('UIBold',str(BOLD)))
else:
    pdfmetrics.registerFontFamily('UI',normal='Helvetica',bold='Helvetica-Bold')
    # The generation environment normally supplies Segoe UI.
    raise SystemExit('Set FONT and BOLD paths to local TTF fonts before generation.')
W,H=595.28,841.89
ink=HexColor('#173d3b');muted=HexColor('#637476');line=HexColor('#dce4df');green=HexColor('#d9edb6')
body=ParagraphStyle('body',fontName='UI',fontSize=9.2,leading=14,textColor=ink)
small=ParagraphStyle('small',fontName='UI',fontSize=8,leading=11.8,textColor=muted)


def para(c,text,x,y,width=499,style=body):
    p=Paragraph(text,style);_,height=p.wrap(width,1000);p.drawOn(c,x,y-height);return y-height


def page(c,number):
    c.setFillColor(HexColor('#f4f6f1'));c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(ink);c.setFont('UIBold',9);c.drawString(48,H-38,'TRACESOL  /  LAUNCHPAD HACKS 2026')
    c.setStrokeColor(line);c.line(48,36,W-48,36)
    c.setFont('UI',7);c.setFillColor(muted);c.drawString(48,22,'New local prototype | AI-assisted development disclosed | 8 November 2026')
    c.drawRightString(W-48,22,f'{number} / 2')


def heading(c,text,y):
    c.setFillColor(ink);c.setFont('UIBold',12);c.drawString(48,y,text)


def main():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    c=canvas.Canvas(str(OUT),pagesize=(W,H));c.setTitle('TraceSol - Solubility evidence, in context');c.setAuthor('Ngoc Bach Hoang');c.setSubject('LaunchPad Hacks project brief and no-video judge walkthrough')
    page(c,1)
    c.setFillColor(ink);c.setFont('Times-Roman',36);c.drawString(48,754,'Every measurement');c.drawString(48,713,'has a context.')
    y=para(c,'TraceSol helps chemistry students and researchers normalize solubility units, inspect source evidence, and separate disagreements from differences in experimental context.',48,687)
    c.setFillColor(green);c.roundRect(48,y-36,499,23,5,fill=1,stroke=0);c.setFillColor(ink);c.setFont('UI',8);c.drawString(59,y-28,'Local processing  /  No API keys  /  No pip dependencies  /  No video required')
    img=ImageReader(str(ROOT/'submission/screenshots/01-evidence-workbench.png'));iw,ih=img.getSize();width=440;height=ih/iw*width
    image_top=y-51
    c.drawImage(img,(W-width)/2,image_top-height,width=width,height=height,mask='auto')
    para(c,'Actual application screenshot. All displayed measurements and excerpts are synthetic teaching examples, not published experimental results.',48,65,style=small)
    c.showPage();page(c,2)
    c.setFont('Times-Roman',29);c.setFillColor(ink);c.drawString(48,758,'A review you can reproduce.')
    y=para(c,'Import a CSV, preserve the original record, inspect each conversion and source excerpt, then add your own decision and export the evidence trail. The application never chooses a source as correct or declares a record model-ready.',48,735)
    heading(c,'The useful three-minute demonstration',y-28)
    y=para(c,'<b>1. Equivalent units.</b> Q-01: 0.30224 mg/L / 302.24 g/mol = 1 micromolar. Q-02 reports 1 micromolar directly. Both normalize to log S = -6.<br/><br/><b>2. Context-aware inspection.</b> Q-03 is tenfold higher under the same recorded conditions; two pairs are flagged. Q-04 has different pH and Q-06 a different form, so these stay separate. Missing pH prevents a complete-context conclusion.<br/><br/><b>3. Human reasoning.</b> Add a follow-up decision and a reason. Edit a working value to see the comparisons recalculate and its decision reset. Export the review or save/reopen the workspace.',48,y-44)
    heading(c,'Implemented and checked',y-28)
    data=[['Area','Evidence in the package'],['Calculation & server','32 automated tests; standard-library unittest suite'],['Browser workflow','15 checks using Playwright with installed Microsoft Edge'],['Responsive layout','Checked at 390, 768, 1024, and 1440 pixels'],['Deliverables','CSV, audit JSON, printable HTML, editable workspace'],['Source trail','Original fields, excerpts, locators, calculations, SHA-256']]
    table=Table([[Paragraph(a,small),Paragraph(b,small)] for a,b in data],colWidths=[139,360]);table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),green),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),.5,line),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]));_,th=table.wrap(499,500);table.drawOn(c,48,y-44-th);y=y-44-th
    heading(c,'Transparent boundaries',y-27)
    y=para(c,'The demo is synthetic. Source excerpts are not independently verified. Compound identities are user-provided labels. Matching recorded conditions does not establish full experimental equivalence. No paper-validation accuracy, predictive performance, or time-saving claim is made.',48,y-42)
    y=para(c,'<b>Run:</b> extract the release; double-click START_TRACESOL.cmd on Windows, or run python app.py with Python 3.10+. Open http://127.0.0.1:8765. No internet is required after Python is available.',48,y-12)
    y=para(c,'<b>Submission state:</b> local build and written materials prepared; not published or submitted. Confirm age/student/geographic eligibility and add a public downloadable-build URL accessible through judging. Video is optional under the public event requirements.',48,y-12)
    para(c,'Background: IUPAC Gold Book entries S05740 and A00295; Llompart et al., Scientific Data (2024), DOI 10.1038/s41597-024-03105-6. Full methods, credits, and validation are included in the project.',48,y-12,style=small)
    c.save();print(OUT)


if __name__=='__main__':main()
