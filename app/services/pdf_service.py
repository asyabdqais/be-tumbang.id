from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
import os
import tempfile

def generate_rapor_pdf(balita_data: dict, antropometri_list: list) -> str:
    # Setup Jinja2 environment
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    # Create a basic template if it doesn't exist
    template_path = os.path.join(template_dir, 'rapor.html')
    if not os.path.exists(template_path):
        with open(template_path, 'w') as f:
            f.write('''
            <html>
            <head><title>Rapor Tumbuh Kembang</title></head>
            <body>
                <h1>Rapor Tumbuh Kembang Balita</h1>
                <p>Nama: {{ balita.nama }}</p>
                <p>NIK: {{ balita.nik }}</p>
                <p>Tanggal Lahir: {{ balita.tanggal_lahir }}</p>
                <p>Jenis Kelamin: {{ balita.jenis_kelamin }}</p>
                
                <h2>Riwayat Timbangan</h2>
                <table border="1">
                    <tr>
                        <th>Tanggal</th>
                        <th>Berat (kg)</th>
                        <th>Tinggi (cm)</th>
                        <th>Z-Score</th>
                        <th>Status Gizi</th>
                    </tr>
                    {% for antro in antropometris %}
                    <tr>
                        <td>{{ antro.tanggal_timbang }}</td>
                        <td>{{ antro.berat_badan }}</td>
                        <td>{{ antro.tinggi_badan }}</td>
                        <td>{{ antro.z_score }}</td>
                        <td>{{ antro.status_gizi }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </body>
            </html>
            ''')
            
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('rapor.html')
    
    html_out = template.render(balita=balita_data, antropometris=antropometri_list)
    
    # Generate PDF
    fd, temp_pdf_path = tempfile.mkstemp(suffix='.pdf')
    os.close(fd)
    
    HTML(string=html_out).write_pdf(temp_pdf_path)
    
    return temp_pdf_path
