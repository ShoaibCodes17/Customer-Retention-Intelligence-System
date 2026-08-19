from src.models.explain import explain_customer

for cid in ["16029", "12346", "13093"]:
    result = explain_customer(cid)
    print(f"\nCustomer {cid}:")
    for r in result["top_reasons"]:
        print(f"  {r['feature']}: value={r['value']}, shap={r['shap_value']}, {r['direction']}")