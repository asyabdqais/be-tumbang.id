import google.generativeai as genai
from database import GEMINI_API_KEY
from typing import Optional

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')


async def generate_intervensi_resep(
    nama_balita:      str,
    status_gizi:      str,
    berat_badan:      float,
    tinggi_badan:     float,
    umur_bulan:       int,
    jenis_kelamin:    str,
    kondisi_geografis: Optional[str]   = "Daratan/Umum",
    lila:             Optional[float]  = None,
    lingkar_kepala:   Optional[float]  = None,
    status_imunisasi: Optional[str]    = None,
    asi_eksklusif:    Optional[bool]   = None,
) -> str:
    lila_info     = f"LiLA: {lila} cm" if lila else "LiLA: tidak diukur"
    lk_info       = f"Lingkar Kepala: {lingkar_kepala} cm" if lingkar_kepala else "Lingkar Kepala: tidak diukur"
    imunisasi_info = f"Status Imunisasi: {status_imunisasi}" if status_imunisasi else "Status Imunisasi: tidak tercatat"
    asi_info       = f"ASI Eksklusif: {'Ya' if asi_eksklusif else 'Tidak'}" if asi_eksklusif is not None else "ASI Eksklusif: tidak tercatat"

    prompt = f"""
Anda adalah seorang Dokter Spesialis Anak dan Ahli Gizi Klinis yang bekerja untuk program Posyandu Puskesmas Indonesia.
Berikan rekomendasi intervensi gizi yang **spesifik, praktis, dan berbasis bukti ilmiah** untuk balita berikut ini.

--- DATA BALITA ---
Nama          : {nama_balita}
Usia          : {umur_bulan} bulan
Jenis Kelamin : {jenis_kelamin}
Berat Badan   : {berat_badan} kg
Tinggi Badan  : {tinggi_badan} cm
{lila_info}
{lk_info}
{imunisasi_info}
{asi_info}
Kondisi Geografis     : {kondisi_geografis}
Status Gizi (Z-Score) : **{status_gizi}**

--- INSTRUKSI ---
Buatkan laporan intervensi dengan format berikut (gunakan Bahasa Indonesia yang mudah dipahami orang tua):

**1. Analisis Kondisi**
Jelaskan kondisi gizi anak secara singkat dan apa risikonya.

**2. Rekomendasi Pola Makan (7 Hari)**
Berikan contoh menu harian yang realistis. **WAJIB mempertimbangkan kondisi geografis "{kondisi_geografis}"** — prioritaskan bahan pangan lokal yang mudah didapat di daerah tersebut.

**3. Suplemen & Intervensi Medis**
Rekomendasikan suplemen yang diperlukan (contoh: PMT, Vitamin A, Zinc, Fe) sesuai pedoman Kemenkes RI.

**4. Saran untuk Orang Tua**
Berikan 3-5 tips praktis yang bisa langsung dilakukan di rumah.

**5. Tanda Bahaya (Red Flags)**
Sebutkan kondisi yang harus segera dibawa ke Puskesmas atau Rumah Sakit.

**PENTING: Gaya Bahasa**
Gunakan gaya bahasa yang hangat, natural, dan empati layaknya manusia asli (seorang dokter sungguhan yang peduli pada pasiennya). JANGAN gunakan pembukaan khas AI, gaya bahasa kaku, atau kalimat klise robotik. Hindari penggunaan markdown berlebihan jika tidak perlu, buat senatural mungkin.
"""
    try:
        response = await model.generate_content_async(prompt)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "Terjadi kesalahan saat menghubungi layanan AI. Silakan periksa koneksi dan API Key, lalu coba lagi."
