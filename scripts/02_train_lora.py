import os

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import torch

from datasets import load_from_disk
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer, SFTConfig


MODEL_ID = "Qwen/Qwen2.5-1.5B"
DATA_PATH = "data/full_it_dataset"
OUTPUT_DIR = "models/ForgeLM-v1"
ADAPTER_DIR = "models/ForgeLM-v1-adapter"


def main():

    print(f"--- 1. Loading Tokenizer and Base Model: {MODEL_ID} ---")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        dtype=torch.bfloat16
    ).to("cuda:0")

    print("Model device:", next(model.parameters()).device)
    print("Model dtype:", next(model.parameters()).dtype)

    torch.cuda.empty_cache()

    print("\n--- 2. Configuring LoRA Adapter ---")

    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj"
        ],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = get_peft_model(model, lora_config)

    model.print_trainable_parameters()

    print(f"\n--- 3. Loading Dataset from {DATA_PATH} ---")

    dataset = load_from_disk(DATA_PATH)

    print(dataset)
    print("Training examples:", len(dataset))
    print("Columns:", dataset.column_names)

    # Verify that the dataset actually contains usable text.
    if "text" not in dataset.column_names:
        raise ValueError(
            "Dataset must contain a 'text' column."
        )

    for i in range(min(2, len(dataset))):
        print(f"\nExample {i}:")
        print(dataset[i]["text"][:500])

    print("\n--- 4. Setting up SFTConfig ---")

    training_args = SFTConfig(
        output_dir=OUTPUT_DIR,

        # Dataset
        dataset_text_field="text",
        max_length=1024,

        # Training
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        max_steps=40,

        # Precision
        bf16=True,
        fp16=False,

        # Logging / saving
        logging_steps=1,
        save_strategy="no",
        report_to="none",

        # Optimizer
        optim="adamw_torch",

        # Do not use packing for this initial test
        packing=False,

        completion_only_loss=False,
    )

    print("\n--- 5. Creating SFTTrainer ---")

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        processing_class=tokenizer,
    )

    print("\n--- 6. Executing LoRA Training ---")

    trainer.train()

    print(f"\n--- 7. Saving Trained Adapter to {ADAPTER_DIR} ---")

    os.makedirs(ADAPTER_DIR, exist_ok=True)

    trainer.model.save_pretrained(ADAPTER_DIR)
    tokenizer.save_pretrained(ADAPTER_DIR)

    print("\n==========================================")
    print("Fine-tuning complete!")
    print(f"Adapter saved to: {ADAPTER_DIR}")
    print("==========================================")


if __name__ == "__main__":
    main()