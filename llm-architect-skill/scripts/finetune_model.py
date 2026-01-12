"""
Fine-tuning Automation with PEFT and LoRA
Automates model fine-tuning pipeline
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import json

try:
    from transformers import (
        AutoTokenizer, AutoModelForCausalLM,
        TrainingArguments, Trainer,
        DataCollatorForLanguageModeling
    )
    from peft import LoraConfig, get_peft_model, TaskType, PeftModel
    from datasets import Dataset
except ImportError:
    raise ImportError("transformers and peft required: pip install transformers peft datasets")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FinetuningConfig:
    model_name: str
    output_dir: str
    train_file: str
    validation_file: Optional[str] = None

    # Training parameters
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 4
    per_device_eval_batch_size: int = 4
    gradient_accumulation_steps: int = 1
    learning_rate: float = 2e-4
    warmup_steps: int = 100
    logging_steps: int = 10
    save_steps: int = 500
    eval_steps: int = 500

    # LoRA parameters
    use_lora: bool = True
    lora_r: int = 8
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: List[str] = None

    # Data parameters
    max_seq_length: int = 512
    preprocessing_num_workers: int = 4

    def __post_init__(self):
        if self.lora_target_modules is None:
            self.lora_target_modules = ["q_proj", "v_proj"]

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> 'FinetuningConfig':
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        return cls(**config)


class ModelFinetuner:
    def __init__(self, config: FinetuningConfig):
        self.config = config
        self.tokenizer = None
        self.model = None
        self.trainer = None

        self._setup_directories()

    def _setup_directories(self):
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)

    def load_model(self):
        logger.info(f"Loading model: {self.config.model_name}")

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.model_name,
            trust_remote_code=True
        )

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            trust_remote_code=True,
            torch_dtype="auto",
            device_map="auto"
        )

        if self.config.use_lora:
            self._apply_lora()

    def _apply_lora(self):
        logger.info("Applying LoRA adapters")

        lora_config = LoraConfig(
            r=self.config.lora_r,
            lora_alpha=self.config.lora_alpha,
            target_modules=self.config.lora_target_modules,
            lora_dropout=self.config.lora_dropout,
            bias="none",
            task_type=TaskType.CAUSAL_LM
        )

        self.model = get_peft_model(self.model, lora_config)
        self.model.print_trainable_parameters()

    def load_data(self) -> Dataset:
        logger.info(f"Loading training data from {self.config.train_file}")

        with open(self.config.train_file, 'r') as f:
            data = json.load(f)

        dataset = Dataset.from_list(data)
        tokenized = dataset.map(
            self._tokenize_function,
            batched=True,
            num_proc=self.config.preprocessing_num_workers,
            remove_columns=dataset.column_names
        )

        return tokenized

    def _tokenize_function(self, examples: Dict[str, List[str]]) -> Dict[str, List]:
        texts = []
        for i in range(len(examples['text'])):
            texts.append(examples['text'][i])

        tokenized = self.tokenizer(
            texts,
            truncation=True,
            max_length=self.config.max_seq_length,
            padding=False
        )

        return tokenized

    def prepare_trainer(self, train_dataset: Dataset, eval_dataset: Optional[Dataset] = None):
        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.num_train_epochs,
            per_device_train_batch_size=self.config.per_device_train_batch_size,
            per_device_eval_batch_size=self.config.per_device_eval_batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            warmup_steps=self.config.warmup_steps,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            eval_steps=self.config.eval_steps,
            evaluation_strategy="steps" if eval_dataset else "no",
            save_total_limit=3,
            fp16=True,
            optim="adamw_torch",
            report_to=["tensorboard"],
        )

        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )

        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator
        )

    def train(self):
        logger.info("Starting training")

        train_dataset = self.load_data()
        eval_dataset = None

        if self.config.validation_file:
            eval_dataset = self.load_validation_data()

        self.prepare_trainer(train_dataset, eval_dataset)
        self.trainer.train()

        logger.info("Training completed")

    def load_validation_data(self) -> Dataset:
        logger.info(f"Loading validation data from {self.config.validation_file}")

        with open(self.config.validation_file, 'r') as f:
            data = json.load(f)

        dataset = Dataset.from_list(data)
        tokenized = dataset.map(
            self._tokenize_function,
            batched=True,
            num_proc=self.config.preprocessing_num_workers,
            remove_columns=dataset.column_names
        )

        return tokenized

    def save_model(self, path: Optional[str] = None):
        output_path = path or self.config.output_dir
        logger.info(f"Saving model to {output_path}")

        self.model.save_pretrained(output_path)
        self.tokenizer.save_pretrained(output_path)

        logger.info("Model saved")

    def load_finetuned_model(self, path: Optional[str] = None):
        load_path = path or self.config.output_dir
        logger.info(f"Loading fine-tuned model from {load_path}")

        self.tokenizer = AutoTokenizer.from_pretrained(load_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            torch_dtype="auto",
            device_map="auto"
        )

        if self.config.use_lora:
            self.model = PeftModel.from_pretrained(self.model, load_path)

        logger.info("Fine-tuned model loaded")

    def generate(self, prompt: str, **kwargs) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        with open(self.config.output_dir + "/generation_config.json", 'w') as f:
            json.dump(kwargs, f)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=kwargs.get('max_new_tokens', 100),
            temperature=kwargs.get('temperature', 0.7),
            do_sample=True,
            pad_token_id=self.tokenizer.pad_token_id
        )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)


def create_sample_data(output_path: str):
    """Create sample training data for demonstration"""
    data = [
        {"text": "The capital of France is Paris."},
        {"text": "Python is a programming language."},
        {"text": "Machine learning is a subset of AI."},
        {"text": "The Earth orbits around the Sun."},
        {"text": "Water boils at 100 degrees Celsius."}
    ]

    for _ in range(100):
        data.extend(data[:5])

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)


def main():
    create_sample_data("train_data.json")

    config = FinetuningConfig(
        model_name="gpt2",
        output_dir="./finetuned_model",
        train_file="train_data.json",
        use_lora=True,
        num_train_epochs=1,
        per_device_train_batch_size=2
    )

    finetuner = ModelFinetuner(config)
    finetuner.load_model()
    finetuner.train()
    finetuner.save_model()


if __name__ == "__main__":
    main()
