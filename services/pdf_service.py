from datetime import datetime


def _pdf_escape(value) -> str:
    text = "" if value is None else str(value)
    return (
        text.encode("latin-1", "replace")
        .decode("latin-1")
        .replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )


def _text_line(x: int, y: int, text, size: int = 10, font: str = "F1") -> str:
    return f"BT /{font} {size} Tf {x} {y} Td ({_pdf_escape(text)}) Tj ET"


def _wrap_text(text, max_chars: int = 92):
    words = _pdf_escape(text).split()
    lines = []
    current = ""

    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > max_chars and current:
            lines.append(current)
            current = word
        else:
            current = candidate

    if current:
        lines.append(current)
    return lines or ["-"]


def _build_pdf(content: str) -> bytes:
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",
    ]

    content_bytes = content.encode("latin-1", "replace")
    objects.append(
        f"<< /Length {len(content_bytes)} >>\nstream\n".encode("latin-1")
        + content_bytes
        + b"\nendstream"
    )

    pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]

    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("latin-1"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))

    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("latin-1")
    )
    return bytes(pdf)


def generate_rapor_pdf_bytes(balita_data: dict, antropometri_list: list) -> bytes:
    lines = []
    y = 792

    lines.append(_text_line(48, y, "Laporan Tumbuh Kembang Balita", 18, "F2"))
    y -= 24
    lines.append(_text_line(48, y, f"Dicetak: {datetime.now().strftime('%d-%m-%Y %H:%M')}", 9))
    y -= 26

    lines.append(_text_line(48, y, "Data Balita", 12, "F2"))
    y -= 18
    biodata = [
        ("Nama", balita_data.get("nama")),
        ("NIK", balita_data.get("nik")),
        ("Tanggal Lahir", balita_data.get("tanggal_lahir")),
        ("Jenis Kelamin", balita_data.get("jenis_kelamin")),
    ]
    for label, value in biodata:
        lines.append(_text_line(60, y, f"{label}: {value or '-'}", 10))
        y -= 15

    y -= 12
    lines.append(_text_line(48, y, "Riwayat Timbangan", 12, "F2"))
    y -= 20
    lines.append(_text_line(48, y, "Tanggal", 9, "F2"))
    lines.append(_text_line(145, y, "Berat", 9, "F2"))
    lines.append(_text_line(210, y, "Tinggi", 9, "F2"))
    lines.append(_text_line(280, y, "Z-Score", 9, "F2"))
    lines.append(_text_line(350, y, "Status Gizi", 9, "F2"))
    y -= 6
    lines.append("0.5 w 48 {} m 545 {} l S".format(y, y))
    y -= 16

    if antropometri_list:
        for item in antropometri_list:
            if y < 72:
                lines.append(_text_line(48, y, "Data lanjutan terpotong. Gunakan filter periode untuk laporan lebih ringkas.", 9))
                break
            lines.append(_text_line(48, y, item.get("tanggal_timbang", "-"), 9))
            lines.append(_text_line(145, y, f"{item.get('berat_badan', '-')} kg", 9))
            lines.append(_text_line(210, y, f"{item.get('tinggi_badan', '-')} cm", 9))
            lines.append(_text_line(280, y, item.get("z_score", "-"), 9))
            lines.append(_text_line(350, y, item.get("status_gizi", "-"), 9))
            y -= 16
    else:
        for wrapped in _wrap_text("Belum ada riwayat timbangan untuk balita ini."):
            lines.append(_text_line(48, y, wrapped, 9))
            y -= 14

    y -= 18
    lines.append(_text_line(48, y, "Catatan", 12, "F2"))
    y -= 16
    note = (
        "Laporan ini dibuat otomatis dari data pencatatan Posyandu. "
        "Gunakan hasil ini sebagai bahan pemantauan dan konsultasikan kondisi anak kepada tenaga kesehatan bila diperlukan."
    )
    for wrapped in _wrap_text(note, max_chars=88):
        lines.append(_text_line(48, y, wrapped, 9))
        y -= 13

    return _build_pdf("\n".join(lines))


def generate_rapor_pdf(balita_data: dict, antropometri_list: list) -> str:
    import os
    import tempfile

    fd, temp_pdf_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    with open(temp_pdf_path, "wb") as pdf_file:
        pdf_file.write(generate_rapor_pdf_bytes(balita_data, antropometri_list))
    return temp_pdf_path
