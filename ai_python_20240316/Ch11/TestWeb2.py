"""
from flask import Flask   
app = Flask(__name__) 
@app.route("/")           
def home():               
    return "<h1>hello world</h1>"   
app.run() 

"""
from flask import Flask, request, abort
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
from openai import OpenAI
import json

app = Flask(__name__)

# 設定您的 LINE 和 OpenAI 憑證
access_token = ''
channel_secret = ''
openAiKey = ''

configuration = Configuration(access_token=access_token)
handler = WebhookHandler(channel_secret)

@app.route("/", methods=['POST'])
def callback():
    # 獲取來自 LINE 的 X-Line-Signature 標頭值
    signature = request.headers['X-Line-Signature']

    # 獲取請求內容作為文本
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 處理 webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.error("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text
    messages = [{"role": "system", "content": "你好!"}]
    ai_msg = user_message[:6].lower()
    reply_msg = ''

    if ai_msg == 'hi ai:':
        app.logger.info("OpenAI!!!")
        messages.append({"role": "user", "content": user_message[6:]})
        client = OpenAI(api_key=openAiKey)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=256,
            temperature=0.5
        )
        reply_msg = response.choices[0].message.content.replace('\n', '')
        app.logger.info(f"Message: {reply_msg}")
    else:
        reply_msg = user_message

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_msg)]
            )
        )

if __name__ == "__main__":
    app.run(debug=True)
