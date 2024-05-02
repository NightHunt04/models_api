from flask import Flask, request, jsonify
from lexica import Client, languageModels
import asyncio, os
from sydney import SydneyClient
from hugchat import hugchat
from hugchat.login import Login
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

EMAIL = '<EMAIL>'
PASSWD = '<PASSWD>'
cookie_path_dir = "./cookies/" 
sign = Login(EMAIL, PASSWD)
cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)

chatbot = hugchat.ChatBot(cookies=cookies.get_dict())

@app.route('/')
def hello_world():
    return "this is from admin's api"


@app.route('/models')
def chat_completion():
    client = Client()

    model_id = request.args.get('model_id')
    prompt = request.args.get('prompt')

    if model_id == '0':
        response = client.ChatCompletion(prompt, languageModels.openhermes)
        return jsonify({ 'response' : response })

    elif model_id == '1':
        response = client.ChatCompletion(prompt, languageModels.gpt)
        v = os.environ.get('YOUR_VARIABLE_NAME')
        return jsonify({ 'response' : response, 'env' : v })

    else:
        return jsonify({ 'error' : 'Invalid model id or prompt' })


async def bing_gen(prompt, search=True) -> None:
    async with SydneyClient() as client:
        response = await client.ask(prompt, search=search)
        return response

@app.route('/bing')
def chat_bing():
    prompt = request.args.get('prompt')
    search = request.args.get('search')

    response = asyncio.run(bing_gen(prompt, search))
    return jsonify({ 'response' : response })


@app.route('/hug')
def chat_hug():
    prompt = request.args.get('prompt')
    model = request.args.get('model')
    
    # cohere, zephyr, gemma, mistral 7b v0.2, phi
    if model == '0' or model == '2' or model == '5' or model == '6' or model == '7':
        chatbot.switch_llm(int(model))
        chatbot.new_conversation(switch_to=True)
        response = chatbot.chat(prompt)
        response = str(response)
        chatbot.delete_conversation()
        return jsonify({ 'response' : response })

if __name__ == '__main__':
    app.run()