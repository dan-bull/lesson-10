import json

def lambda_handler(event, context):
    print("Validating data...")
    print("Input:", json.dumps(event))

    return {
        "status": "ok",
        "step": "validation",
        "input": event
    }