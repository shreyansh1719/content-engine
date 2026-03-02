import os
import json
from datetime import datetime

def extract_training_examples_from_feedback():
    """Extract training examples from feedback for model fine-tuning"""
    print("Extracting training examples from feedback...")
    
    feedback_dir = "data/feedback"
    training_dir = "data/training/feedback_examples"
    os.makedirs(training_dir, exist_ok=True)
    
    # Find all feedback files
    feedback_files = []
    for filename in os.listdir(feedback_dir):
        if filename.startswith("feedback_") and filename.endswith(".json"):
            feedback_files.append(os.path.join(feedback_dir, filename))
    
    print(f"Found {len(feedback_files)} feedback files")
    
    # Extract high-rated examples (rating 4-5)
    training_examples = []
    for file_path in feedback_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                feedback = json.load(f)
                
            # Only use high-rated feedback
            if feedback.get("rating", 0) >= 4:
                # Get ad data
                ad_data = feedback.get("ad_data", {})
                if not ad_data:
                    continue
                
                # Create training example
                example = {
                    "input": f"Create a {ad_data.get('style', 'premium')} ad for {ad_data.get('prompt', '')} "
                            f"in the {ad_data.get('industry', 'general')} industry using the "
                            f"'{ad_data.get('principle', 'Emotional')}' principle",
                    "output": {
                        "headline": ad_data.get("headline", ""),
                        "subheadline": ad_data.get("subheadline", ""),
                        "body_text": ad_data.get("body_text", ""),
                        "call_to_action": ad_data.get("call_to_action", "")
                    },
                    "metadata": {
                        "source": "user_feedback",
                        "rating": feedback.get("rating"),
                        "feedback_id": feedback.get("id"),
                        "feedback": feedback.get("feedback_text", "")
                    }
                }
                
                training_examples.append(example)
                print(f"Added example from feedback {feedback.get('id')} with rating {feedback.get('rating')}")
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
    
    # Also extract A/B test winners
    ab_winners_dir = "data/training/ab_winners"
    if os.path.exists(ab_winners_dir):
        for filename in os.listdir(ab_winners_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(ab_winners_dir, filename), 'r', encoding='utf-8') as f:
                        winner = json.load(f)
                        training_examples.append(winner)
                        print(f"Added A/B test winner from {filename}")
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
    
    # Save the examples
    if training_examples:
        output_path = f"{training_dir}/feedback_training_examples_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                "examples": training_examples,
                "metadata": {
                    "source": "user_feedback",
                    "generated_at": datetime.now().isoformat(),
                    "count": len(training_examples)
                }
            }, f, indent=2)
        
        print(f"Saved {len(training_examples)} training examples to {output_path}")
        return output_path
    else:
        print("No suitable training examples found")
        return None

if __name__ == "__main__":
    extract_training_examples_from_feedback()