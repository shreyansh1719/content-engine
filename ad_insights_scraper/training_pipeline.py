"""
Pipeline for preparing training data and fine-tuning models
"""
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

class TrainingPipeline:
    def __init__(self, input_dir='data', output_dir='data/models', model_type='gpt'):
        """Initialize training pipeline with input/output directories and model type"""
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.model_type = model_type
        self.logger = logging.getLogger('TrainingPipeline')
        
        # Create required directories
        os.makedirs(output_dir, exist_ok=True)
    
    def prepare_training_data(self) -> List[Dict[str, Any]]:
        """Prepare training data from collected ad content"""
        from .training.data_formatter import DataFormatter
        
        self.logger.info(f"Preparing training data for {self.model_type} model")
        
        formatter = DataFormatter(
            input_dir=self.input_dir,
            output_dir=os.path.join(self.input_dir, 'training')
        )
        
        # Format data for specified model type
        examples = formatter.format_all_sources(model_type=self.model_type)
        self.logger.info(f"Generated {len(examples)} training examples for {self.model_type} model")
        
        return examples
    
    def train_model(self, epochs=3, batch_size=8, learning_rate=2e-5) -> Dict[str, Any]:
        """Train model using prepared training data"""
        from .training.llm_trainer import LLMTrainer
        
        self.logger.info(f"Training {self.model_type} model")
        
        trainer = LLMTrainer(
            model_type=self.model_type,
            training_dir=os.path.join(self.input_dir, 'training'),
            output_dir=self.output_dir
        )
        
        # Train model
        results = trainer.train(
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate
        )
        
        self.logger.info(f"Training complete: {results}")
        return results
    
    def run_full_pipeline(self) -> Optional[Dict[str, Any]]:
        """Run complete training pipeline from data preparation to model training"""
        self.logger.info(f"Starting full training pipeline for {self.model_type}")
        
        # Step 1: Prepare training data
        examples = self.prepare_training_data()
        if not examples:
            self.logger.error("Failed to generate training examples")
            return None
        
        # Step 2: Train the model
        results = self.train_model()
        
        # Step 3: Return the model info
        if results and 'training_loss' in results:
            return {
                'model_type': self.model_type,
                'training_time': datetime.now().isoformat(),
                'examples_count': len(examples),
                'training_results': results
            }
        else:
            self.logger.error("Training failed or returned no results")
            return None