import os
import azure.cognitiveservices.speech as speechsdk
import base64
import asyncio

def handler(event, context):
    return asyncio.run(async_handler(event, context))

async def async_handler(event, context):
    # --- 1. 安全防护设置 ---
    # 【必须修改】把下面引号里的网址换成你真正的 Vercel 访问网址
    # 注意：末尾不要带斜杠 /
    ALLOWED_ORIGIN = "https://www.myenglishstudy.cn"
    
    params = event.get('queryStringParameters', {})
    
    # 【暗号校验】确保和前端网页里的 secret 参数一致
    if params.get('secret') != "my2026":
        return {"statusCode": 403, "body": "Access Denied"}

    text = params.get('text', '')
    if not text:
        return {"statusCode": 400, "body": "Text is empty"}

    # --- 2. 读取你在 Netlify 后台设置的钥匙 ---
    speech_key = os.environ.get('AZURE_KEY')
    service_region = os.environ.get('AZURE_REGION')
    voice = params.get('voice', 'en-US-AriaNeural')

    # --- 3. Azure SDK 核心逻辑 ---
    try:
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        speech_config.speech_synthesis_voice_name = voice
        # 设置输出格式为 MP3
        speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)

        # 内存合成（不产生临时文件）
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "audio/mpeg",
                    "Access-Control-Allow-Origin": ALLOWED_ORIGIN
                },
                "body": base64.b64encode(result.audio_data).decode('utf-8'),
                "isBase64Encoded": True
            }
        else:
            return {"statusCode": 500, "body": f"Azure Error: {result.reason}"}
            
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
