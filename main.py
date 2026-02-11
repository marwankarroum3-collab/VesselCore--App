def engine_diagnostic(load, avg_temp, sfoc_actual, manufacturer="MAN B&W"):
    recommendations = []
    
    # 1. تحليل استهلاك الوقود
    design_sfoc = 165 # مثال لقيمة الصانع عند حمل 85%
    if sfoc_actual > design_sfoc * 1.05:
        recommendations.append("⚠️ ارتفاع في استهلاك الوقود: راجع كفاءة الحوافن أو ضغط الحقن.")
    
    # 2. تحليل درجات الحرارة
    if avg_temp > 400:
        recommendations.append("❌ تحذير حراري: درجات الحرارة مرتفعة جداً، افحص نظام التبريد أو الشاحن التوربيني.")
    
    return recommendations