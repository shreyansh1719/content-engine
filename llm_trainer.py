import os
import json
import logging
import time
from typing import List, Dict

import openai
from dotenv import load_dotenv

class LLMTrainer:
    def __init__(self):
        """
        Initialize LLM Training utility
        """
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('llm_trainer.log', encoding='utf-8')
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Load environment variables
        load_dotenv()
        
        # Initialize OpenAI client
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Create directories
        os.makedirs('models', exist_ok=True)
    
    def prepare_training_data(self, input_file: str) -> List[Dict]:
        """
        Prepare and validate training data for OpenAI fine-tuning
        
        Args:
            input_file: Path to input training JSON file
        
        Returns:
            List of processed training examples
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate and transform data
            prepared_data = []
            for entry in data:
                # Ensure required fields exist
                if not entry.get('input') or not entry.get('output'):
                    continue
                
                # Create OpenAI-compatible training example
                prepared_entry = {
                    "messages": [
                        {"role": "system", "content": "You are an expert ad copywriter."},
                        {"role": "user", "content": entry['input']},
                        {"role": "assistant", "content": json.dumps(entry['output'])}
                    ]
                }
                prepared_data.append(prepared_entry)
            
            # Save prepared data
            output_file = 'models/prepared_training_data.jsonl'
            with open(output_file, 'w', encoding='utf-8') as f:
                for entry in prepared_data:
                    f.write(json.dumps(entry) + '\n')
            
            self.logger.info(f"Prepared {len(prepared_data)} training examples")
            return prepared_data
        
        except Exception as e:
            self.logger.error(f"Data preparation error: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def upload_training_file(self, file_path: str):
        """
        Upload training file to OpenAI
        
        Args:
            file_path: Path to prepared JSONL file
        
        Returns:
            File ID for fine-tuning
        """
        try:
            with open(file_path, 'rb') as f:
                file_upload = openai.files.create(
                    file=f,
                    purpose='fine-tune'
                )
            
            self.logger.info(f"Training file uploaded: {file_upload.id}")
            return file_upload.id
        
        except Exception as e:
            self.logger.error(f"File upload error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_fine_tuning_job(self, file_id: str, model: str = 'gpt-3.5-turbo'):
        """
        Create fine-tuning job
        
        Args:
            file_id: ID of uploaded training file
            model: Base model to fine-tune (default: gpt-3.5-turbo)
        
        Returns:
            Fine-tuning job ID
        """
        try:
            job = openai.fine_tuning.jobs.create(
                training_file=file_id, 
                model=model
            )
            
            self.logger.info(f"Fine-tuning job created: {job.id}")
            return job.id
        
        except Exception as e:
            self.logger.error(f"Fine-tuning job creation error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def monitor_fine_tuning_job(self, job_id: str):
        """
        Monitor the status of a fine-tuning job
        
        Args:
            job_id: ID of the fine-tuning job
        """
        try:
            while True:
                job = openai.fine_tuning.jobs.retrieve(job_id)
                
                self.logger.info(f"Job Status: {job.status}")
                
                if job.status in ['succeeded', 'failed']:
                    if job.status == 'succeeded':
                        fine_tuned_model = job.fine_tuned_model
                        self.logger.info(f"Fine-tuning completed. Model: {fine_tuned_model}")
                        return fine_tuned_model
                    else:
                        self.logger.error("Fine-tuning job failed")
                        return None
                
                # Wait for 1 minute before checking again
                time.sleep(60)
        
        except Exception as e:
            self.logger.error(f"Job monitoring error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

def main():
    """
    Main function to run LLM fine-tuning process
    """
    trainer = LLMTrainer()
    
    # Path to training data
    training_data_path = 'data/processed/ad_training_data.json'
    
    # Prepare training data
    prepared_data = trainer.prepare_training_data(training_data_path)
    
    if prepared_data:
        # Upload training file
        file_id = trainer.upload_training_file('models/prepared_training_data.jsonl')
        
        if file_id:
            # Create fine-tuning job
            job_id = trainer.create_fine_tuning_job(file_id)
            
            if job_id:
                # Monitor job
                trainer.monitor_fine_tuning_job(job_id)

if __name__ == "__main__":
    main()