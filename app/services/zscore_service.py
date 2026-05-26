def calculate_zscore(berat_badan: float, tinggi_badan: float, umur_bulan: int, jenis_kelamin: str) -> tuple[float, str]:
    # TODO: Implement actual WHO / Kemenkes Z-Score tables
    # This is a simplified mock for demonstration purposes
    
    # Calculate BMI
    tinggi_m = tinggi_badan / 100
    bmi = berat_badan / (tinggi_m ** 2)
    
    # Mock z-score based on BMI
    z_score = 0.0
    status_gizi = "Normal"
    
    if bmi < 14:
        z_score = -3.0
        status_gizi = "Gizi Buruk"
    elif bmi < 16:
        z_score = -2.0
        status_gizi = "Kurang"
    elif bmi > 25:
        z_score = 2.0
        status_gizi = "Lebih"
    else:
        z_score = 0.0
        status_gizi = "Normal"
        
    return z_score, status_gizi
