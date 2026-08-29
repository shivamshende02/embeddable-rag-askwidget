import ollama

response = ollama.chat(
    model="llama3.2:1b",
    messages=[{"role": "user", "content": "Say hello in one sentence."}],
)
print(response["message"]["content"])