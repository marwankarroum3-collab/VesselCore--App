import re

def flexible_parser(text):
    data = {}
    # استخدام أنماط مرنة تتجاهل المسافات والحالات (Case Insensitive)
    patterns = {
        "dist": r"Dis.*?([\d\.]+)",
        "rpm": r"R.*?P.*?M.*?([\d\.]+)",
        "fuel": r"Fuel.*?oil.*?([\d\.]+)",
        "slip": r"Slip.*?([\-\d\.]+)%"
    }
    
    for key, pattern in patterns.items():
        try:
            match = re.search(pattern, text, re.I | re.S)
            data[key] = float(match.group(1)) if match else 0.0
        except Exception:
            data[key] = 0.0 # تجاوز الخطأ لضمان عدم توقف البرنامج
            
    return data