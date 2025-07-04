import os
import sys
import argparse
from memvid import MemvidChat

try:
    from memvid import MemvidChat
except ModuleNotFoundError:
    print("🛑  The 'memvid' package is not installed in this Python environment.")
    print("   ➤ Fix: activate your virtualenv then run 'pip install -r requirements.txt' or simply 'pip install memvid'.")
    sys.exit(1)

# --- Configuration ---
VIDEO_FILE = "manim_memory.mp4"
INDEX_FILE = "manim_memory_index.json"
# -------------------

def chat_session():
    """
    Starts an interactive chat session with the Manim documentation memory.
    """
    parser = argparse.ArgumentParser(description="Chat with the Manim documentation memory")
    parser.add_argument("--provider", choices=["openai", "google"], default="openai", help="Which LLM provider to use (default: openai)")
    args = parser.parse_args()

    provider = args.provider
    api_env_var = "OPENAI_API_KEY" if provider == "openai" else "GOOGLE_API_KEY"

    api_key = os.getenv(api_env_var)
    if not api_key:
        print("----------------------------------------------------------------")
        print(f"🛑 ERROR: LLM API key not found.\n   Please set the {api_env_var} environment variable.")
        example_var = "OPENAI_API_KEY" if provider == "openai" else "GOOGLE_API_KEY"
        print(f"   For example: $env:{example_var}='your-key' (PowerShell)")
        print(f"   or export {example_var}='your-key' (Bash)")
        print("----------------------------------------------------------------")
        sys.exit(1)

    if not os.path.exists(VIDEO_FILE) or not os.path.exists(INDEX_FILE):
        print("----------------------------------------------------------------")
        print(f"🛑 ERROR: Memory files not found!")
        print(f"   Make sure '{VIDEO_FILE}' and '{INDEX_FILE}' are in this directory.")
        print(f"   Run 'python build_manim_memory.py' first to create them.")
        print("----------------------------------------------------------------")
        sys.exit(1)

    print("---------------------------------")
    print("🤖 Manim Code Assistant Initialized")
    print(f"   LLM provider: {provider.capitalize()}")
    print("---------------------------------")
    print("Ask me anything about Manim, or type 'exit' to end.")

    memchat = MemvidChat(
        video_file=VIDEO_FILE,
        index_file=INDEX_FILE,
        llm_api_key=api_key,
        llm_provider=provider
    )
    memchat.start_session()

    while True:
        try:
            user_msg = input("\n👤 You: ")
            if user_msg.strip().lower() == "exit":
                print("\n🤖 Assistant: Goodbye!")
                break
            
            print("\n🤖 Assistant: Thinking...")
            reply = memchat.chat(user_msg)
            print(f"\r🤖 Assistant: {reply}")

        except (KeyboardInterrupt, EOFError):
            print("\n🤖 Assistant: Session ended. Goodbye!")
            break

if __name__ == "__main__":
    chat_session() 