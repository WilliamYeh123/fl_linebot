from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
 
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage
from . import fl
 
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
ETF_id = ['1','2'] 

    
    
@csrf_exempt
def callback(request):
 
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
 
        try:
            events = parser.parse(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
 
        for event in events:
            if isinstance(event, MessageEvent):  # 如果有訊息事件
                if event.message.text == 'check': #查看服務
                    line_bot_api.reply_message(  
                    event.reply_token,
                    TextSendMessage(text='選擇基金:\n1 : 國內成分證券ETF \n2 : 國外成分證券ETF')
                )
                elif event.message.text in ETF_id:
                    etf_id = int(event.message.text)
                    reply = fl.fiveline(etf_id)
                    line_bot_api.reply_message(  
                    event.reply_token,
                    TextSendMessage(text=reply)
                )
                else:
                    line_bot_api.reply_message(  # 回復傳入的訊息文字
                    event.reply_token,
                    TextSendMessage(text='error')
                )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()