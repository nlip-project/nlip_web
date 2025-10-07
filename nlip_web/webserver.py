import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from nlip_server import server
from nlip_sdk import nlip
from nlip_server.server import logger
import logging

from nlip_web.genai import SimpleGenAI

logger.setLevel(logging.INFO)


class ChatApplication(server.SafeApplication):
    def startup(self):
        self.model = os.environ.get("CHAT_MODEL", "llava")
        self.host = os.environ.get("CHAT_HOST", "localhost")
        self.port = os.environ.get("CHAT_PORT", 11434)

    def shutdown(self):
        return None

    def create_session(self) -> server.NLIP_Session:
        return ChatSession(host=self.host, port=self.port, model=self.model)


class ChatSession(server.NLIP_Session):

    def __init__(self, host: str, port: int, model: str):
        self.host = host
        self.port = port
        self.model = model

    def start(self):
        self.chat_server = SimpleGenAI(self.host, self.port)

    def execute(
        self, msg: nlip.NLIP_Message
    ) -> nlip.NLIP_Message:
        text = msg.extract_text()

        files = []
        binary_contents = msg.extract_field_list("binary")
        for base64_content in binary_contents:
            files.append(base64_content)
        
        # Generate response with optional files
        if files:
            response = self.chat_server.generate_with_files(self.model, text, files)
            logger.info("Processing message with base64 image files")
        else:
            response = self.chat_server.generate(self.model, text)
            
        return nlip.NLIP_Factory.create_text(response)

    def stop(self):
        self.server = None


app = server.setup_server(ChatApplication())
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)