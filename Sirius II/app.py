from fastapi import FastAPI
from starlette.responses import RedirectResponse
import gradio as gr
from backend import *

app = FastAPI()


# @app.get("/")
# def read_main():
#     return {"message": "This is your main app"}
username, password = "", ""
api_key = ""
def welcome(name):
    return f"Welcome to Gradio, {name}!"
def auth(username1, password1):
    if username1 == "admin" or password1 == "admin":
        return True
    resp = login(username1, password1)
    if resp.status_code == 401:
        return False
    if resp.status_code != 200:
        return False
    global username, password
    username, password = username1, password1
    return True
def get_api():
    resp = check_api_key(username, password)
    print(resp)
    if type(resp)!= str:
        gr.Error("Something went wrong")
    return resp
def create_api_key_func():
    resp = create_api_key(username, password)
    if type(resp)!= str:
        gr.Error("Something went wrong")
    gr.Info("Success! You have API_key")
def update_message(request: gr.Request):
    return f"Welcome, {request.username}"
def registration_func(name,main_pass,conf_pass):
    if name=="":
        raise gr.Error("Enter your Name")
    if main_pass=="":
        raise gr.Error("Enter your Password")
    if main_pass!=conf_pass:
        raise gr.Error("Passwords do not match")
    #if пользователь с таким email уже существует
    resp = register(name, main_pass)
    if resp.status_code == 401:
        raise gr.Error("User already exists")
    if resp.status_code != 200:
        raise gr.Error("Something went wrong")
    gr.Info("Success! You have been registered")
    return gr.Button(visible=True)

    # email существует
def check_transaction_func(user_hash, transaction_hash):
    resp = get_trans_info(api_key, user_hash, transaction_hash)
    if type(resp)!= str:
        gr.Error("Something went wrong")
    return resp
with gr.Blocks() as regisration:
    with gr.Row():
        name = gr.Textbox(placeholder="Enter your Name", label="Name")
    with gr.Group():
        main_pass = gr.Textbox(placeholder="Enter your Password", label="Password", type="password")
        conf_pass = gr.Textbox(placeholder="Repeat your Password", type="password")
    reg_btn = gr.Button("Register")
    login_btn = gr.Button("Login", link="/gradio",visible=False)
    reg_btn.click(registration_func,[name,main_pass,conf_pass], login_btn)


with gr.Blocks() as demo:
    with gr.Tab("Demo"):
        crypto = gr.Radio(["BTC", "ETH", "USDT", "TON", "SOL"], label="Network", info="Select cryptocurrency")
        hash = gr.Textbox(label="Transaction hash",
                          placeholder="Enter transaction hash e.g. f42c5ad573370f70e806957955db646efb40f105f8691049c666d687b75f47e0")
        user_hash = gr.Textbox(label="User hash",
                          placeholder="Enter transaction hash e.g. f42c5ad573370f70e806957955db646efb40f105f8691049c666d687b75f47e0")
        detect_btn = gr.Button(value="Detect", variant="primary")
        result = gr.Textbox(label="Result", placeholder="Result will be displayed here")
        detect_btn.click(lambda x, y: [x, y], [user_hash, hash], result)
    with gr.Tab("Profile"):
        pass
    with gr.Tab("API"):
        api_key_t = gr.Textbox(interactive=False, show_copy_button=True, label="API key")
        get_api_btn = gr.Button(value="Create API", variant="primary")
        check_api_btn = gr.Button(value="Check API", variant="secondary")
        get_api_btn.click(create_api_key_func,[])
        check_api_btn.click(get_api, [], api_key_t)


io = demo
app = gr.mount_gradio_app(app, io, path='/gradio', auth=auth)
app = gr.mount_gradio_app(app, regisration, path='/reg')

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)

# Run this from the terminal as you would normally start a FastAPI app: `uvicorn run:app`
# and navigate to http://localhost:8000/gradio in your browser.
