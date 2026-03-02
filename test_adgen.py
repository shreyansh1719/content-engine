# test_adgen.py

from ad_generator import AdGenerator
import os

if __name__ == "__main__":
    prompt = "Bombay Musk Perfume"
    product_image_path = r"C:\Users\RAZDAN\Desktop\test-2.jpg"  # Ensure this path exists

    generator = AdGenerator(openai_api_key=os.getenv("OPENAI_API_KEY"))
    result = generator.create_ad(prompt=prompt, product_image_path=product_image_path)

    print("=== AD GENERATED ===")
    print(f"Brand: {result['brand_name']}")
    print(f"Product: {result['product']}")
    print(f"Headline: {result['headline']}")
    print(f"Subheadline: {result['subheadline']}")
    print(f"CTA: {result['call_to_action']}")
    print(f"Final image path: {result['final_path']}")
