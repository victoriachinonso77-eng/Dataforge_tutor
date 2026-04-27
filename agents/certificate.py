from typing import Optional
# agents/certificate.py
# Progress Certificate Generator — PDF certificate on pipeline completion

from datetime import datetime


def generate_certificate(student_name: str, score: int, total: int,
                          level: str, dataset_name: str = "your dataset") -> Optional[bytes]:
    """Generates a PDF certificate. Returns bytes or None if fpdf2 missing."""
    try:
        from fpdf import FPDF
        pct = int((score / max(total, 1)) * 100)
        grade = "Distinction" if pct >= 80 else "Merit" if pct >= 60 else "Pass"
        date_str = datetime.now().strftime("%d %B %Y")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(False)

        # Background
        pdf.set_fill_color(13, 17, 23)
        pdf.rect(0, 0, 210, 297, 'F')

        # Border
        pdf.set_draw_color(2, 195, 154)
        pdf.set_line_width(3)
        pdf.rect(8, 8, 194, 281)
        pdf.set_line_width(0.5)
        pdf.rect(11, 11, 188, 275)

        # Accent bars
        pdf.set_fill_color(2, 195, 154)
        pdf.rect(11, 11, 188, 4, 'F')
        pdf.rect(11, 282, 188, 4, 'F')

        # Title
        pdf.set_font("Helvetica", "B", 40)
        pdf.set_text_color(2, 195, 154)
        pdf.set_xy(0, 25)
        pdf.cell(210, 20, "DataForge", align="C")

        pdf.set_font("Helvetica", "", 13)
        pdf.set_text_color(148, 163, 184)
        pdf.set_xy(0, 47)
        pdf.cell(210, 8, "AI Data Science Tutor", align="C")

        pdf.set_draw_color(2, 195, 154)
        pdf.line(40, 60, 170, 60)

        pdf.set_font("Helvetica", "I", 14)
        pdf.set_text_color(148, 163, 184)
        pdf.set_xy(0, 68)
        pdf.cell(210, 10, "Certificate of Completion", align="C")

        pdf.set_font("Helvetica", "", 12)
        pdf.set_text_color(200, 210, 220)
        pdf.set_xy(0, 85)
        pdf.cell(210, 8, "This certifies that", align="C")

        pdf.set_font("Helvetica", "B", 26)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(0, 96)
        pdf.cell(210, 14, student_name or "Data Science Student", align="C")

        pdf.set_font("Helvetica", "", 12)
        pdf.set_text_color(200, 210, 220)
        pdf.set_xy(0, 116)
        pdf.cell(210, 8, "has successfully completed the", align="C")

        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(2, 195, 154)
        pdf.set_xy(0, 128)
        pdf.cell(210, 10, "DataForge Data Science Pipeline", align="C")

        pdf.set_font("Helvetica", "", 12)
        pdf.set_text_color(200, 210, 220)
        pdf.set_xy(0, 142)
        pdf.cell(210, 8, f"at {level.title()} level", align="C")

        pdf.line(50, 158, 160, 158)

        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(148, 163, 184)
        pdf.set_xy(0, 165)
        pdf.cell(210, 8, "Demonstrating proficiency in:", align="C")

        for i, skill in enumerate(["Data Cleaning & Validation",
                                    "Statistical Analysis & EDA",
                                    "Data Visualisation",
                                    "Machine Learning (AutoML)"]):
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(200, 210, 220)
            pdf.set_xy(0, 176 + i * 9)
            pdf.cell(210, 8, f"• {skill}", align="C")

        # Score box
        pdf.set_fill_color(22, 30, 50)
        pdf.set_draw_color(2, 195, 154)
        pdf.rect(60, 216, 90, 28, 'FD')
        pdf.set_font("Helvetica", "B", 22)
        pdf.set_text_color(2, 195, 154)
        pdf.set_xy(60, 220)
        pdf.cell(90, 12, f"{pct}%", align="C")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(148, 163, 184)
        pdf.set_xy(60, 232)
        pdf.cell(90, 8, f"Quiz Score — {grade}", align="C")

        pdf.set_font("Helvetica", "I", 10)
        pdf.set_text_color(100, 116, 139)
        pdf.set_xy(0, 252)
        pdf.cell(210, 6, f"Dataset: {dataset_name}", align="C")
        pdf.set_xy(0, 262)
        pdf.cell(210, 6, f"Date: {date_str}", align="C")

        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(71, 85, 105)
        pdf.set_xy(0, 274)
        pdf.cell(210, 6, "DataForge — AI Data Science Tutor", align="C")

        return bytes(pdf.output())
    except Exception as e:
        print(f"Certificate error: {e}")
        return None


def show_certificate_section(st, student_name, score, total,
                               level, dataset_name, steps_completed):
    """Shows certificate section in Streamlit when student completes all steps."""
    all_steps = ["upload","clean","analyse","visualise","automl","chat"]
    pct = int((score / max(total, 1)) * 100)
    done = all(s in (steps_completed or []) for s in all_steps)
    passed = pct >= 50

    if not done:
        remaining = [s for s in all_steps if s not in (steps_completed or [])]
        st.info(f"Complete {len(remaining)} more step(s) to earn your certificate: "
                f"{', '.join(r.title() for r in remaining)}")
        st.progress(len(steps_completed or []) / 6)
        return

    if not passed:
        st.warning(f"You scored {pct}% — need 50%+ for your certificate. "
                   "Review quiz explanations and try again!")
        return

    grade = "Distinction" if pct >= 80 else "Merit" if pct >= 60 else "Pass"
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0D2137,#1E3A5F);
                border:2px solid #02C39A;border-radius:12px;
                padding:2rem;text-align:center;margin:1rem 0;">
        <div style="font-size:3rem;">🏆</div>
        <h2 style="color:#02C39A;margin:.5rem 0;">Congratulations!</h2>
        <p style="color:#E6EDF3;font-size:1.1rem;">
            You completed the DataForge Data Science Pipeline — Grade: {grade}
        </p>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    c1.metric("Final Score", f"{pct}%")
    c2.metric("Grade", grade)
    c3.metric("Level", level.title())

    with st.spinner("Generating certificate..."):
        pdf_bytes = generate_certificate(student_name or "Student",
                                          score, total, level, dataset_name)
    if pdf_bytes:
        name_safe = (student_name or "Student").replace(" ","_")
        st.download_button("📜 Download Certificate (PDF)", pdf_bytes,
                           f"DataForge_Certificate_{name_safe}.pdf",
                           "application/pdf", use_container_width=True)
    else:
        st.warning("Install fpdf2 for PDF certificates: pip install fpdf2")