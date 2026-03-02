import os
import json
import sys
from datetime import datetime

def prepare_fine_tuning_data(input_file):
    """Prepare fine-tuning data from training examples"""
    print(f"Preparing fine-tuning data from {input_file}...")
    
    # Load examples
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    examples = data.get("examples", [])
    if not examples:
        print("No examples found in input file")
        return None
    
    print(f"Processing {len(examples)} examples")
    
    # Create system prompt
    system_prompt = """You are an expert advertising copywriter with 15+ years of experience creating high-performing ads across multiple platforms. You craft compelling, persuasive copy that converts and engages target audiences."""
    
    # Create fine-tuning data in OpenAI format
    fine_tuning_data = []
    
    for example in examples:
        if "input" not in example or "output" not in example:
            print("Skipping invalid example (missing input or output)")
            continue
        
        # Create messages format
        fine_tuning_example = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": example["input"]},
                {"role": "assistant", "content": (
                    json.dumps(example["output"]) 
                    if isinstance(example["output"], (dict, list)) 
                    else str(example["output"])
                )}
            ]
        }
        
        fine_tuning_data.append(fine_tuning_example)
    
    # Save to JSONL file
    output_dir = "data/training/fine_tuning"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = f"{output_dir}/feedback_fine_tuning_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for example in fine_tuning_data:
            f.write(json.dumps(example) + '\n')
    
    print(f"Saved {len(fine_tuning_data)} fine-tuning examples to {output_path}")
    return output_path

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        # Find most recent training examples file
        training_dir = "data/training/feedback_examples"
        if not os.path.exists(training_dir):
            print(f"Directory not found: {training_dir}")
            sys.exit(1)
            
        files = [os.path.join(training_dir, f) for f in os.listdir(training_dir) 
                if f.startswith("feedback_training_examples_") and f.endswith(".json")]
        
        if not files:
            print("No training examples files found")
            sys.exit(1)
            
        # Sort by modification time (newest first)
        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        input_file = files[0]
        print(f"Using most recent file: {input_file}")
    
    prepare_fine_tuning_data(input_file)