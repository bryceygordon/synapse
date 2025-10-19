import subprocess
import sys
import time

def check_qdrant_status():
    """Checks if Qdrant container is running."""
    result = subprocess.run(
        ['docker', 'ps', '--filter', 'name=qdrant', '--format', '{{.Status}}'],
        capture_output=True, text=True
    )
    return result.stdout.strip()

def start_qdrant():
    """Starts the Qdrant container."""
    print("Attempting to start Qdrant container...")
    subprocess.run(['docker', 'start', 'qdrant'])

def main():
    status = check_qdrant_status()
    if status and 'Up' in status:
        print("✅ Qdrant service is running.")
        sys.exit(0)
    else:
        print("⚠️ Qdrant service not running. Starting it now...")
        start_qdrant()
        # Verify it started
        time.sleep(3) # Give it a moment to boot
        if 'Up' in check_qdrant_status():
            print("✅ Qdrant service started successfully.")
            sys.exit(0)
        else:
            print("❌ Failed to start Qdrant service. Please check Docker.")
            sys.exit(1)

if __name__ == "__main__":
    main()
