import json
import random
from datasets import Dataset

# Templates for procedural generation to simulate a large IT knowledge base
K8S_SERVICES = ["PaymentGateway", "AuthService", "InventoryService", "NotificationWorker", "OrderProcessor"]
DB_TYPES = ["PostgreSQL", "Redis", "MongoDB", "Elasticsearch"]
HTTP_ERRORS = [
    (502, "Bad Gateway", "Check the reverse proxy and upstream service health."),
    (503, "Service Unavailable", "Verify pod readiness probes and resource limits."),
    (504, "Gateway Timeout", "Investigate database query latency and upstream API response times."),
    (401, "Unauthorized", "Ensure the API token is valid and hasn't expired.")
]

raw_data = []

def generate_k8s_runbooks():
    for svc in K8S_SERVICES:
        raw_data.append({
            "instruction": f"How do I restart the {svc} deployment in Kubernetes?",
            "context": f"Service: {svc} | Namespace: production",
            "response": f"To restart the {svc}, authenticate to the production cluster and run: `kubectl rollout restart deployment/{svc.lower()} -n production`. Monitor the rollout status with `kubectl rollout status deployment/{svc.lower()} -n production`."
        })
        raw_data.append({
            "instruction": f"Troubleshoot CrashLoopBackOff for {svc}.",
            "context": f"Pod is crash looping. Service: {svc}",
            "response": f"First, grab the previous logs: `kubectl logs deploy/{svc.lower()} --previous`. Often this is caused by missing environment variables or failed DB connections. Verify the secrets are mounted correctly."
        })

def generate_http_troubleshooting():
    for svc in K8S_SERVICES:
        for code, name, action in HTTP_ERRORS:
            raw_data.append({
                "instruction": f"The {svc} API is returning {code} {name}.",
                "context": f"Endpoint monitoring alert triggered for {svc}.",
                "response": f"A {code} error indicates an infrastructure or upstream failure. {action} For {svc}, check the Datadog APM metrics for immediate spikes in latency or error rates."
            })

def generate_database_docs():
    for db in DB_TYPES:
        raw_data.append({
            "instruction": f"What is the connection string format for our internal {db} instances?",
            "context": "Internal developer documentation.",
            "response": f"Standard {db} connections should use the internal DNS format: `{db.lower()}://user:password@db-{db.lower()}.internal.corp:port/dbname`. Never hardcode credentials; fetch them via HashiCorp Vault."
        })

def format_prompt(sample):
    return f"### Instruction:\n{sample['instruction']}\n\n### Context:\n{sample['context']}\n\n### Response:\n{sample['response']}"

def main():
    print("Generating synthetic enterprise IT dataset...")
    
    # Generate the data
    generate_k8s_runbooks()
    generate_http_troubleshooting()
    generate_database_docs()
    
    # Add our original examples
    raw_data.append({
        "instruction": "Explain how to troubleshoot an HTTP 503 error in the Payment Service.",
        "context": "The Payment Service exposes /health and /ready endpoints on port 8080. It depends on a Redis cache.",
        "response": "An HTTP 503 indicates the service is unavailable. First, verify the Kubernetes pods are running. Check the /health endpoint on port 8080. If the service is healthy but still throwing 503s, verify the connection to the Redis cache, as connection timeouts will force the service into an unavailable state."
    })
    
    # Shuffle the dataset to prevent ordering bias during training
    random.shuffle(raw_data)
    
    formatted_data = [{"text": format_prompt(d)} for d in raw_data]
    dataset = Dataset.from_list(formatted_data)
    
    save_path = "data/full_it_dataset"
    dataset.save_to_disk(save_path)
    
    print(f"Dataset prepared and saved to {save_path}.")
    print(f"Total training examples: {len(dataset)}")
    
    # Save a JSON copy for easy inspection
    with open("data/full_it_dataset.json", "w") as f:
        json.dump(raw_data, f, indent=2)

if __name__ == "__main__":
    main()