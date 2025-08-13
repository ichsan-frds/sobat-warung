from rapidfuzz import process, fuzz
from api.core.database import product

async def find_similar_product(product_name: str, threshold: int = 75):
    # Ambil semua nama produk dari DB
    all_products = await product.find({}, {"_id": 1, "product_name": 1}).to_list(None)
    product_names = [p["product_name"] for p in all_products]

    # Cari yang paling mirip
    match = process.extractOne(
        product_name,
        product_names,
        scorer=fuzz.WRatio
    )

    if match and match[1] >= threshold:
        # Ambil data produk yang sesuai
        matched_product = next(
            (p for p in all_products if p["product_name"] == match[0]),
            None
        )
        return matched_product
    
    print(f"No similar product found for '{product_name}' with threshold {threshold} because match score is {match[1] if match else 'None'}")
    return None