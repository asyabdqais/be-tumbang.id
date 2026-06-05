# LMS parameters: age_months -> (L, M, S)
# Derived from WHO Growth Standards for Weight-for-Age (BB/U) and Height-for-Age (TB/U)
LMS_DATA = {
    "L": { # Laki-laki / Boys
        "BB/U": {
            0: (0.3487, 3.5353, 0.1523),
            3: (0.1982, 6.3535, 0.1264),
            6: (0.0543, 7.9000, 0.1215),
            9: (-0.0152, 8.9220, 0.1205),
            12: (-0.0611, 9.6765, 0.1206),
            18: (-0.1205, 10.9230, 0.1190),
            24: (-0.1601, 12.1520, 0.1185),
            30: (-0.1912, 13.2500, 0.1198),
            36: (-0.2185, 14.3223, 0.1215),
            42: (-0.2330, 15.3500, 0.1238),
            48: (-0.2452, 16.3279, 0.1264),
            54: (-0.2490, 17.3100, 0.1292),
            60: (-0.2520, 18.2813, 0.1325),
        },
        "TB/U": {
            0: (1.0, 49.88, 0.0379),
            3: (1.0, 59.78, 0.0355),
            6: (1.0, 67.62, 0.0345),
            9: (1.0, 72.01, 0.0344),
            12: (1.0, 75.73, 0.0347),
            18: (1.0, 82.25, 0.0350),
            24: (1.0, 87.14, 0.0354),
            30: (1.0, 91.95, 0.0360),
            36: (1.0, 96.09, 0.0368),
            42: (1.0, 99.85, 0.0376),
            48: (1.0, 103.30, 0.0384),
            54: (1.0, 106.70, 0.0392),
            60: (1.0, 110.01, 0.0401),
        }
    },
    "P": { # Perempuan / Girls
        "BB/U": {
            0: (0.4046, 3.3991, 0.1463),
            3: (0.2435, 5.8420, 0.1245),
            6: (0.1042, 7.3000, 0.1205),
            9: (0.0125, 8.2430, 0.1202),
            12: (-0.0935, 8.9486, 0.1207),
            18: (-0.1452, 10.1500, 0.1204),
            24: (-0.1873, 11.5122, 0.1208),
            30: (-0.2115, 12.6800, 0.1232),
            36: (-0.2312, 13.8821, 0.1261),
            42: (-0.2410, 14.9800, 0.1295),
            48: (-0.2478, 16.0969, 0.1332),
            54: (-0.2492, 17.1800, 0.1370),
            60: (-0.2505, 18.2322, 0.1411),
        },
        "TB/U": {
            0: (1.0, 49.15, 0.0385),
            3: (1.0, 58.17, 0.0360),
            6: (1.0, 65.74, 0.0354),
            9: (1.0, 70.15, 0.0356),
            12: (1.0, 74.00, 0.0361),
            18: (1.0, 80.68, 0.0364),
            24: (1.0, 85.73, 0.0368),
            30: (1.0, 90.35, 0.0375),
            36: (1.0, 95.07, 0.0384),
            42: (1.0, 98.95, 0.0392),
            48: (1.0, 102.68, 0.0401),
            54: (1.0, 106.10, 0.0410),
            60: (1.0, 109.39, 0.0418),
        }
    }
}

def calculate_zscore(
    berat_badan: float,
    tinggi_badan: float,
    umur_bulan: int,
    jenis_kelamin: str
) -> tuple[float, str]:
    """
    Menghitung Z-Score berdasarkan tabel LMS WHO / Kemenkes RI.
    Mengembalikan tuple (z_score, status_gizi).
    """
    # Normalisasi jenis kelamin
    jk = "L"
    if jenis_kelamin and jenis_kelamin.upper() in ["P", "PEREMPUAN"]:
        jk = "P"

    # Clamp umur_bulan antara 0 sampai 60 bulan
    age = max(0, min(umur_bulan, 60))

    # Fungsi bantu untuk interpolasi parameter LMS
    def get_lms(indicator: str) -> tuple[float, float, float]:
        table = LMS_DATA[jk][indicator]
        keys = sorted(table.keys())
        
        if age in table:
            return table[age]
            
        # Cari key yang mengapit age
        x1, x2 = keys[0], keys[-1]
        for k in keys:
            if k <= age:
                x1 = k
            if k >= age:
                x2 = k
                break
                
        if x1 == x2:
            return table[x1]
            
        L1, M1, S1 = table[x1]
        L2, M2, S2 = table[x2]
        
        # Interpolasi linear
        fraction = (age - x1) / (x2 - x1)
        L = L1 + fraction * (L2 - L1)
        M = M1 + fraction * (M2 - M1)
        S = S1 + fraction * (S2 - S1)
        return L, M, S

    # Hitung Z-Score Berat Badan menurut Umur (BB/U)
    L_bb, M_bb, S_bb = get_lms("BB/U")
    if abs(L_bb) < 1e-5:
        from math import log
        z_bb = log(berat_badan / M_bb) / S_bb
    else:
        z_bb = (((berat_badan / M_bb) ** L_bb) - 1.0) / (L_bb * S_bb)

    # Hitung Z-Score Tinggi Badan menurut Umur (TB/U)
    L_tb, M_tb, S_tb = get_lms("TB/U")
    if abs(L_tb) < 1e-5:
        from math import log
        z_tb = log(tinggi_badan / M_tb) / S_tb
    else:
        z_tb = (((tinggi_badan / M_tb) ** L_tb) - 1.0) / (L_tb * S_tb)

    # Diagnosis berdasarkan standard WHO / Kemenkes RI PMK No 2/2020:
    # 1. Stunting (Tinggi Badan menurut Umur TB/U < -2.0 SD)
    # 2. Gizi Buruk (Berat Badan menurut Umur BB/U < -3.0 SD)
    # 3. Gizi Kurang / Kurang (Berat Badan menurut Umur BB/U < -2.0 SD)
    # 4. Gizi Lebih / Lebih (Berat Badan menurut Umur BB/U > 2.0 SD)
    # 5. Normal (Lainnya)
    
    if z_tb < -2.0:
        return round(z_tb, 2), "Stunting"
    elif z_bb < -3.0:
        return round(z_bb, 2), "Gizi Buruk"
    elif z_bb < -2.0:
        return round(z_bb, 2), "Kurang"
    elif z_bb > 2.0:
        return round(z_bb, 2), "Lebih"
    else:
        return round(z_bb, 2), "Normal"
