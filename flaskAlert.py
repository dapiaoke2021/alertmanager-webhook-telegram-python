import telegram, json, logging
from dateutil import parser
from flask import Flask
from flask import request
from flask_basicauth import BasicAuth

import urllib

app = Flask(__name__)
app.secret_key = 'lAlAlA123'
basic_auth = BasicAuth(app)

# Yes need to have -, change it!
chatID = "xchatIDx"

# Authentication conf, change it!
app.config['BASIC_AUTH_FORCE'] = False
app.config['BASIC_AUTH_USERNAME'] = 'XXXUSERNAME'
app.config['BASIC_AUTH_PASSWORD'] = 'XXXPASSWORD'

# Bot token, change it!
bots = {}

@app.route('/send/<chatId>/<botToken>', methods = ['POST'])
def postMessage(chatId, botToken):

    try:
        if botToken in bots:
            bot = bots[botToken]
        else:
            bot = telegram.Bot(botToken)
            bots[botToken] = bot
        content = request.get_data()
        app.logger.info("\t%s",content)
        bot.sendMessage(chat_id=chatId, text=content.decode("utf-8"))
        return "Alert OK", 200
    except Exception as error:       
        bot.sendMessage(chat_id=chatID, text="Error to read json: "+str(error))
        app.logger.info("\t%s",error)
        return "Alert fail", 200


@app.route('/alert', methods = ['POST'])
def postAlertmanager():

    try:
        content = json.loads(request.get_data())
        for alert in content['alerts']:
            message = "Status: "+alert['status']+"\n"
            if 'name' in alert['labels']:
                message += "Instance: "+alert['labels']['instance']+"("+alert['labels']['name']+")\n"
            else:
                message += "Instance: "+alert['labels']['instance']+"\n"
            if 'info' in alert['annotations']:
                message += "Info: "+alert['annotations']['info']+"\n"
            if 'summary' in alert['annotations']:
                message += "Summary: "+alert['annotations']['summary']+"\n"                
            if 'description' in alert['annotations']:
                message += "Description: "+alert['annotations']['description']+"\n"
            if alert['status'] == "resolved":
                correctDate = parser.parse(alert['endsAt']).strftime('%Y-%m-%d %H:%M:%S')
                message += "Resolved: "+correctDate
            elif alert['status'] == "firing":
                correctDate = parser.parse(alert['startsAt']).strftime('%Y-%m-%d %H:%M:%S')
                message += "Started: "+correctDate
            bot.sendMessage(chat_id=chatID, text=message)
            return "Alert OK", 200
    except Exception as error:       
        bot.sendMessage(chat_id=chatID, text="Error to read json: "+str(error))
        app.logger.info("\t%s",error)
        return "Alert fail", 200

@app.route('/callback', methods = ['POST'])
def postAlertmanager_callback():
    """阿里云报警webhook，尚未很好优化"""
    print(request.get_data())
    message = request.get_data()
    app.logger.info("\t%s",request.get_data())
    message = message.decode('utf-8') + "\n"
    app.logger.info("\t%s",message)
    bot.sendMessage(chat_id=chatID, text=urllib.parse.unquote(message),parse_mode='HTML')
    return urllib.parse.unquote(message,encoding='utf-8', errors='replace')     
    

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=9119)
