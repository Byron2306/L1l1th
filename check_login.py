from gradio_client import Client

client = Client("dphn/Dolphin-Mistral-24B-Venice-Edition")
result = client.predict(
    api_name="/predict",
    data=["Hello, how are you?"]
)
print(result)
