import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel, PeftConfig

# Path to your saved adapter (from the training script)
adapter_path = "./mistral-finetuned/adapter"
# Original base model name
base_model_name = "mistralai/Mistral-7B-v0.3"

def load_fine_tuned_model():
    """Load the fine-tuned model with adapter weights"""
    print("Loading base model and adapter...")
    
    # Load the base model with the same quantization settings as during training
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        device_map="auto",
        torch_dtype=torch.float16,
        load_in_4bit=True,
    )
    
    # Load the adapter weights on top of the base model
    model = PeftModel.from_pretrained(base_model, adapter_path)
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    print("Model loaded successfully!")
    return model, tokenizer

def generate_response(model, tokenizer, user_message, max_new_tokens=256):
    """Generate a response to a user message"""
    # Format the input as expected by your fine-tuned model
    system_prompt = ("You are a Clash Royale expert who provides detailed, accurate strategic advice." 
    "Your responses should be clear, specific, and include card interactions, elixir costs, and timing considerations."
    "Your answer must be a maximum of 20 continues words written in a friendly tone."
    "Newlines are not allowed in the answer."
    "Roleplay is not allowed."
    "Never include information not related to Clash Royale.")
    prompt = f"<|system|>: {system_prompt}\n<|user|>: {user_message}\n<|assistant|>:"
    
    # Tokenize the input
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    
    # Generate text
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.5,
            top_p=0.5,
            repetition_penalty=1.2,
            do_sample=True,
        )
    
    # Decode the output
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    
    # Extract just the assistant's response (everything after the prompt)
    assistant_response = generated_text[len(prompt):].strip()
    
    return assistant_response

# Example usage
if __name__ == "__main__":
    model, tokenizer = load_fine_tuned_model()
    
    # Test with some Clash Royale related questions
    test_questions = [
        "Give me tips on how to use the Miner effectively.",
    ]
    
    for question in test_questions:
        print(f"\nUser: {question}")
        response = generate_response(model, tokenizer, question)
        print(f"Assistant: {response}")