import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_MODEL_ID = "Qwen/Qwen2.5-1.5B"
ADAPTER_PATH = "models/ForgeLM-v1-adapter"

# The exact format the model was trained on
PROMPT = """### Instruction:
Explain how to troubleshoot an HTTP 503 error in the Payment Service.

### Context:
The Payment Service exposes /health and /ready endpoints on port 8080. It depends on a Redis cache.

### Response:
"""

def generate_response(model, tokenizer, prompt):
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda:0")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            temperature=0.1,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id
        )
        
    full_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract only what the model generated after "### Response:"
    return full_text.split("### Response:\n")[-1].strip()

def main():
    print("--- 1. Loading Base Tokenizer ---")
    tokenizer = AutoTokenizer.from_pretrained(ADAPTER_PATH)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"--- 2. Loading Base Model ({BASE_MODEL_ID}) ---")
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_ID,
        dtype=torch.bfloat16
    ).to("cuda:0")

    print("\n[Base Model Output]")
    base_output = generate_response(base_model, tokenizer, PROMPT)
    print(base_output)
    print("-" * 50)

    print("\n--- 3. Attaching ForgeLM LoRA Adapters ---")
    # This wraps the base model with your trained weights
    forgelm_model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)

    print("\n[ForgeLM Output]")
    forgelm_output = generate_response(forgelm_model, tokenizer, PROMPT)
    print(forgelm_output)
    print("-" * 50)

if __name__ == "__main__":
    main()