import json
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from transformers import BitsAndBytesConfig  # Import for quantization config
from transformers import DataCollatorForLanguageModeling  # Import data collator
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
import torch
import gc
import numpy as np

# Force garbage collection to free memory
gc.collect()
torch.cuda.empty_cache()

print("CUDA available:", torch.cuda.is_available())
print("CUDA version:", torch.version.cuda)

# === Config ===
model_name = "mistralai/Mistral-7B-v0.3"
data_path = "clash_royale_mistral_training_20250517_175154.jsonl"
output_dir = "./mistral-finetuned"

# === Memory-optimized settings ===
MAX_LENGTH = 1024  # Reduce from 1024 to save memory
GRADIENT_ACCUMULATION_STEPS = 16  # Increase from 16 to save memory (effectively smaller batch size)

# === Load Tokenizer ===
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token  # Make sure padding is handled

# === Load Dataset ===
dataset = load_dataset("json", data_files=data_path, split="train")
print(f"Dataset size: {len(dataset)}")

# === Format messages into prompt-style strings ===
def format_conversation(example):
    messages = example["messages"]
    prompt = ""
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            prompt += f"<|user|>: {content}\n"
        elif role == "assistant":
            prompt += f"<|assistant|>: {content}\n"
    return {"text": prompt.strip()}

formatted_dataset = dataset.map(format_conversation)

# === Tokenize for Causal LM ===
def tokenize_function(example):
    # Process a single example at a time to avoid collation issues
    tokenized_inputs = tokenizer(
        example["text"],
        truncation=True,
        max_length=MAX_LENGTH,  # Use shorter sequences
        padding="max_length",
        return_tensors=None
    )
    
    # Convert to numpy to avoid dict error
    return {
        "input_ids": np.array(tokenized_inputs["input_ids"]),
        "attention_mask": np.array(tokenized_inputs["attention_mask"]),
        "labels": np.array(tokenized_inputs["input_ids"])
    }

# Process examples one at a time
tokenized_dataset = formatted_dataset.map(
    tokenize_function,
    remove_columns=["text"],
    desc="Tokenizing dataset"
)

# === Load Model with LoRA ===
# More memory-efficient BitsAndBytesConfig
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,  # Use 4-bit instead of 8-bit to save more memory
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

# Free some memory before loading model
gc.collect()
torch.cuda.empty_cache()

try:
    print("Loading model...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        quantization_config=quantization_config,
        torch_dtype=torch.float16,  # Use mixed precision
    )
    
    # Prepare the model for k-bit training
    model = prepare_model_for_kbit_training(model)
    
    # Configure LoRA with fewer parameters to train
    lora_config = LoraConfig(
        r=16,  # Reduced from 8 to save memory
        lora_alpha=64,  # Reduced from 32
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.1,  # Reduced from 0.1
        bias="none",
        task_type=TaskType.CAUSAL_LM
    )
    
    # Get the PEFT model
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
except Exception as e:
    print(f"Error loading model: {e}")
    raise

# === Create a data collator ===
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)

# === Training Config with Memory Optimizations ===
training_args = TrainingArguments(
    output_dir=output_dir,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
    num_train_epochs=2,  # Reduced from 3
    learning_rate=1e-5,  # Lower learning rate
    logging_steps=10,
    save_strategy="steps",
    save_steps=100,
    fp16=True,
    report_to="none",
    logging_dir="./logs",
    overwrite_output_dir=True,
    label_names=["labels"],
    # Memory optimizations
    gradient_checkpointing=True,  # Use gradient checkpointing to save memory
    optim="adamw_torch_fused",  # Use more memory-efficient optimizer
    max_grad_norm=0.3,  # Lower max gradient norm for stability
    warmup_ratio=0.01  # Add warmup
)

# === Trainer ===
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator,
)

# === Start Training ===
if __name__ == "__main__":
    try:
        print("Starting training...")
        trainer.train()
        
        print("Saving model...")
        # Save adapter weights separately to save space
        model.save_pretrained(f"{output_dir}/adapter")
        
        # Save tokenizer
        tokenizer.save_pretrained(output_dir)
        
        print("Training complete!")
        
    except Exception as e:
        print(f"Error during training: {e}")
        # Print CUDA memory stats for debugging
        print(f"CUDA memory allocated: {torch.cuda.memory_allocated() / 1024**2:.2f} MB")
        print(f"CUDA memory reserved: {torch.cuda.memory_reserved() / 1024**2:.2f} MB")
        
        # Tips for the user
        print("\nTips to fix memory issues:")
        print("1. Reduce MAX_LENGTH further (e.g., to 256)")
        print("2. Use load_in_4bit=True (which we're already doing)")
        print("3. Try training on CPU if your GPU doesn't have enough memory")
        print("4. Reduce the size of your dataset")
        print("5. If none of these work, consider using a smaller base model")