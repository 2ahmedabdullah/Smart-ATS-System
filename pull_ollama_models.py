from ollama import Client
import sys

def direct_hardware_pull():
    print("🎯 Target Locking Local AI Engine Port...")
    client = Client(host='http://127.0.0.1:11434')
    
    # Swapped target name to Meta's heavy-duty model
    # model_name = 'qwen2.5vl'
    model_name = 'nomic-embed-text'
    
    
    print(f"📥 Pulling '{model_name}' (~7.9 GB) onto your RTX 3050...")
    print("⏳ This model reads full tables accurately. Live tracker below:\n")
    
    try:
        for progress in client.pull(model_name, stream=True):
            status = progress.get('status', '')
            
            if 'downloading' in status and 'completed' in progress and 'total' in progress:
                completed = progress['completed'] / (1024 * 1024)
                total = progress['total'] / (1024 * 1024)
                percentage = (progress['completed'] / progress['total']) * 100
                
                sys.stdout.write(f"\r⚡ Downloading Layers: [{percentage:3.1f}%] {completed:.1f}MB / {total:.1f}MB")
                sys.stdout.flush()
            else:
                if status:
                    print(f"\n✨ Status Update: {status}")
                    
        print(f"\n\n🎉 SUCCESS! '{model_name}' is fully cached into your hardware!")
        print("🚀 Next: You are ready to extract the full table structure!")

    except Exception as e:
        print(f"\n❌ Pipeline link interrupted: {e}")

if __name__ == "__main__":
    direct_hardware_pull()