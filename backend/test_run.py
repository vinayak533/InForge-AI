import requests
import time
import json
import pandas as pd
import numpy as np

def run_test():
    print("1. Generating dummy classification dataset...")
    np.random.seed(42)
    n_samples = 100
    df = pd.DataFrame({
        "Age": np.random.randint(18, 70, size=n_samples),
        "Income": np.random.randint(20000, 150000, size=n_samples),
        "Score": np.random.rand(n_samples) * 100,
        "Purchased": np.random.choice([0, 1], size=n_samples, p=[0.7, 0.3])
    })
    csv_filename = "dummy_classification.csv"
    df.to_csv(csv_filename, index=False)
    print(f"Dataset saved to {csv_filename}")

    print("\n2. Uploading dataset to http://localhost:8000/upload...")
    with open(csv_filename, "rb") as f:
        response = requests.post("http://localhost:8000/upload", files={"file": (csv_filename, f, "text/csv")})
    
    if response.status_code != 200:
        print(f"Upload failed: {response.status_code} - {response.text}")
        return
        
    upload_res = response.json()
    session_id = upload_res["session_id"]
    print(f"Upload successful. Session ID: {session_id}")

    print("\n3. Polling for results...")
    results = None
    while True:
        res = requests.get(f"http://localhost:8000/results/{session_id}")
        if res.status_code != 200:
            print(f"Error checking results: {res.status_code} - {res.text}")
            break
            
        data = res.json()
        status = data.get("status")
        print(f"Current status: {status}")
        
        if status == "completed":
            results = data["results"]
            break
        elif status == "failed":
            print(f"Pipeline failed! Error: {data.get('error')}")
            break
            
        time.sleep(1.0)
        
    if results:
        print("\n4. Pipeline finished successfully!")
        ml_agent_results = results.get("ml_agent", {})
        print("\nML Agent results:")
        print(json.dumps(ml_agent_results, indent=2))
        
        # Save to file for further inspection
        with open("pipeline_results.json", "w") as out:
            json.dump(results, out, indent=2)
        print("\nFull results saved to pipeline_results.json")

if __name__ == "__main__":
    run_test()
