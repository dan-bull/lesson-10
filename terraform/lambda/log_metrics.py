import json

def lambda_handler(event, context):
    print("Logging metrics...")
    print("Received:", json.dumps(event))

    return {
        "status": "ok",
        "step": "log_metrics"
    }