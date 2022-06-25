# 必要モジュールの読み込み
from flask import Flask, request, abort
import os
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    PostbackEvent,FollowEvent,
    QuickReply, QuickReplyButton,
    ImageSendMessage
)

from linebot.models.actions import PostbackAction

import google_photos

# 変数appにFlaskを代入。インスタンス化
app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

# Herokuログイン接続確認のためのメソッド
# Herokuにログインすると「hello world」とブラウザに表示される
@app.route("/")
def hello_world():
    return "hello world!"

# ユーザーからメッセージが送信された際、LINE Message APIからこちらのメソッドが呼び出される。
@app.route("/callback", methods=['POST'])
def callback():
    # リクエストヘッダーから署名検証のための値を取得
    signature = request.headers['X-Line-Signature']

    # リクエストボディを取得
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 署名を検証し、問題なければhandleに定義されている関数を呼び出す。
    try:
        handler.handle(body, signature)
    # 署名検証で失敗した場合、例外を出す。
    except InvalidSignatureError:
        abort(400)
    # handleの処理を終えればOK
    return 'OK'

def makeImageMessage():
    # 画像のURLを回収
    photos_urls = google_photos.getPhotos()
    message = ImageSendMessage(
        original_content_url=photos_urls,
        preview_image_url=photos_urls
    )

    return message

# postback messageが返された時のアクション
@handler.add(PostbackEvent)
def on_postback(event):
    postback_msg = event.postback.data

    if postback_msg == "cats":
        make_quickreply_cats(event.reply_token, text="(=^・・^=)")
        message = makeImageMessage()
        line_bot_api.reply_message(event.reply_token, messages)
        

# 友達追加メッセージ
@handler.add(FollowEvent)
def follow(event):
    #if event.type == "follow":
    make_quickreply_cats(
        event.reply_token,
        text="(=^・・^=)")

# クイックリプライ, 鳴き声が書かれたテキストのボタン生成
def make_quickreply_cats(token, text):
    items = []
    items.append(QuickReplyButton(action=PostbackAction(label='にゃーん', data='cats')))
    messages = TextSendMessage(text=text,
                            quick_reply=QuickReply(items=items))
    line_bot_api.reply_message(token, messages=messages)

# LINEでMessageEvent（普通のメッセージを送信された場合）が起こった場合に、
# def以下の関数を実行します。
# reply_messageの第一引数のevent.reply_tokenは、イベントの応答に用いるトークンです。 
# 第二引数には、linebot.modelsに定義されている返信用のTextSendMessageオブジェクトを渡しています。

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextSendMessage(text=event.message.text))
    make_quickreply_cats(event.reply_token, text="(=^・・^=)")
        message = makeImageMessage()
        line_bot_api.reply_message(event.reply_token, messages)

# ポート番号の設定
if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)