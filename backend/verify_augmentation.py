from backend.ingestion import analyze_maturity, analyze_funding, analyze_founders, analyze_public_presence, analyze_hiring_signal, infer_design_opportunity
from datetime import date, timedelta

def test_maturity():
    print("Testing Maturity...")
    assert analyze_maturity("2024")["is_early_stage"] == True
    assert analyze_maturity("2015")["stage"] == "Established"
    print("Maturity OK")

def test_funding():
    print("Testing Funding...")
    details = analyze_funding({"industry": "Technology", "revenue_range": "$1 - $1,000,000"})
    assert "Prototype Validation" in details["bottlenecks"]
    print("Funding OK")

def test_inference():
    print("Testing Inference...")
    maturity = {"stage": "Early-Stage", "is_early_stage": True}
    funding = {"bottlenecks": ["Prototype Validation"]}
    founders = {}
    presence = {"website_status": "Missing"}
    hiring = {"hiring_velocity": "Deferring"}
    
    result = infer_design_opportunity(maturity, funding, founders, presence, hiring)
    print(f"Inferred: {result}")
    assert result["design_opportunity"]["priority"] == "High"
    print("Inference OK")

if __name__ == "__main__":
    test_maturity()
    test_funding()
    test_inference()
