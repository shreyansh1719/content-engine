"""
12-ad portfolio generation — fine-tuned model drives everything.
"""
import json
import traceback
from ad_generator.generator import AdGenerator

g = AdGenerator()
print(f"Fine-tuned model: {g.fine_tuned_model_id}")

portfolio = [
    "Rolex Submariner luxury dive watch",
    "Chanel No. 5 perfume fragrance",
    "Nike Air Jordan 1 Retro streetwear sneakers",
    "Levi's 501 Original jeans denim",
    "Apple AirPods Pro 3 wireless earbuds",
    "Sony PlayStation 5 Pro gaming console",
    "Tesla Model S electric luxury sedan",
    "Porsche 911 Turbo S sports car",
    "Oatly oat milk plant-based dairy alternative",
    "Nespresso Vertuo coffee machine",
    "Dyson Airwrap hair styling tool",
    "The Ordinary Niacinamide serum skincare",
]

results = []
for i, product in enumerate(portfolio):
    print(f"\n{'='*60}")
    print(f"[{i+1}/12] {product}")
    try:
        result = g.create_ad(product)
        print(f"  Headline      : {result.get('headline')}")
        print(f"  Design        : {result.get('design_approach')}")
        print(f"  Tone          : {result.get('tone')}")
        print(f"  Visual style  : {result.get('visual_style')}")
        print(f"  Typography    : {result.get('typography_style', 'N/A')}")
        print(f"  Color scheme  : {result.get('color_scheme', 'N/A')}")
        print(f"  Image         : {result.get('final_path')}")
        results.append({
            'product': product,
            'headline': result.get('headline'),
            'design_approach': result.get('design_approach'),
            'tone': result.get('tone'),
            'visual_style': result.get('visual_style'),
            'typography_style': result.get('typography_style'),
            'color_scheme': result.get('color_scheme'),
            'final_path': result.get('final_path'),
            'status': 'ok',
        })

        img_path = result.get('final_path', '')
        if img_path:
            meta_path = img_path.replace('.png', '_metadata.json')
            safe = {k: v for k, v in result.items() if k not in ('image', 'overlay_html')}
            safe['has_overlay_html'] = bool(result.get('overlay_html'))
            with open(meta_path, 'w') as f:
                json.dump(safe, f, indent=2, default=str)

    except Exception as e:
        print(f"  ERROR: {e}")
        traceback.print_exc()
        results.append({'product': product, 'status': 'error', 'error': str(e)})

print(f"\n\n{'='*60}")
print(f"Done. Check output/images/final/ for all ads.\n")

ok = [r for r in results if r.get('status') == 'ok']
err = [r for r in results if r.get('status') == 'error']
print(f"Success: {len(ok)}/12   Errors: {len(err)}/12")

if ok:
    fonts_used = set()
    designs_used = []
    for r in ok:
        designs_used.append(r.get('design_approach', ''))
    print(f"\nDesign approaches:")
    for r in ok:
        print(f"  [{r['product'][:30]:30}] {r.get('design_approach','?')}")

if err:
    print(f"\nFailed:")
    for r in err:
        print(f"  {r['product']} — {r.get('error','?')[:100]}")
