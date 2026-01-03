import asyncio
import edge_tts
import base64
import json

def handler(event, context):
    return asyncio.run(async_handler(event, context))

async def async_handler(event, context):
    params = event.get('queryStringParameters', {})
    text = params.get('text', 'Hello')
    voice = params.get('voice', 'en-US-AriaNeural')

    communicate = edge_tts.Communicate(text, voice)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "audio/mpeg",
            "Access-Control-Allow-Origin": "*"
        },
        "body": base64.b64encode(audio_data).decode('utf-8'),
        "isBase64Encoded": True
    }
