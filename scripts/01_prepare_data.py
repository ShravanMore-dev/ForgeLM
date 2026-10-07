import json
from datasets import Dataset

# Simulated raw IT data (In a real project, scrape your API docs/Runbooks here)
raw_data = [
    {
        "instruction": "Explain how to troubleshoot an HTTP 503 error in the Payment Service.",
        "context": "The Payment Service exposes /health and /ready endpoints on port 8080. It depends on a Redis cache.",
        "response": "An HTTP 503 indicates the service is unavailable. First, verify the Kubernetes pods are running. Check the /health endpoint on port 8080. If the service is healthy but still throwing 503s, verify the connection to the Redis cache, as connection timeouts will force the service into an unavailable state."
    },
    {
        "instruction": "What is the procedure for restarting the user authentication service?",
        "context": "Auth service runs as a systemd service named 'auth-gateway'.",
        "response": "To restart the authentication service, SSH into the gateway node and execute: `sudo systemctl restart auth-gateway`. Monitor the logs immediately after using `sudo journalctl -u auth-gateway -f` to ensure it binds successfully."
    }
]

def format_prompt(sample):
    """
    Formats the data into a standard instruction prompt.
    Using the ChatML format or a standard Alpaca prompt works well for small models.
    """
    return f"""### Instruction:
{sample['instruction']}

### Context:
{sample['context']}

### Response:
{sample['response']}"""

def main():
    print("Formatting dataset...")
    formatted_data = [{"text": format_prompt(d)} for d in raw_data]
    
    # Create HuggingFace Dataset
    dataset = Dataset.from_list(formatted_data)
    
    # Save to disk
    dataset.save_to_disk("data/processed_it_dataset")
    print(f"Dataset prepared and saved. Total samples: {len(dataset)}")

if __name__ == "__main__":
    main()