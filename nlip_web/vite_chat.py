from nlip_web.genai import StatefulGenAI
from nlip_web  import nlip_ext as nlip_ext 
from nlip_web.env import read_digits, read_string
from nlip_server import server
from nlip_sdk import nlip

from website_modules import main_module as mm

class ChatApplication(nlip_ext.SafeStatefulApplication):
    def __init__(self):
        super().__init__()
        self.local_port = read_digits("LOCAL_PORT",8030)
        self.model = read_string("CHAT_MODEL", "llava")
        self.host = read_string("CHAT_HOST", "localhost")
        self.port = read_digits("CHAT_PORT", 11434)
    

    def create_stateful_session(self) -> server.NLIP_Session:
        genAI = StatefulGenAI(self.host, self.port,self.model)
        session = ChatSession()
        session.set_correlator()
        self.store_session_data(session.get_correlator(), genAI)
        return session


class ChatSession(nlip_ext.StatefulSession):

    def execute(
        self, msg: nlip.NLIP_Message
    ) -> nlip.NLIP_Message:
        text = msg.extract_text()
        images = list()
        binary_contents = msg.extract_field_list("binary")
        for base64_content in binary_contents:
            images.append(base64_content)

        chat_server = self.nlip_app.retrieve_session_data(self.get_correlator())
        if chat_server is None: 
            return nlip.NLIP_Factory.create_text("Error: Can't find my chat server")

        response = chat_server.chat("\"" + text + "\"" + "\nSummarize the search query and convert into a command like 'Find me X'. Be concise.")
        print("Summary: ", response)
        response = chat_server.chat("\"" + response + "\"" + "\nGive me the product that we are searching for. Be very concise, just a 1-2 words.")
        print("Shortened search: " ,response)
        # pass search term to website_modules main search function
        results = mm.search_product(response)
        # print(results)

        # print(f'Received text {text[0:10]}...')
        # response = chat_server.chat_multimodal(text, images = images)
        # print(f'Received response {response[0:10]}...')
        ## response_data = '{"Best Buy":[{"name":"Dell XPS 15","price":1299.99,"description":"15.6-inch FHD display, Intel Core i7, 16GB RAM, 512GB SSD"},{"name":"HP Pavilion 14","price":649.99,"description":"14-inch HD display, AMD Ryzen 5, 8GB RAM, 256GB SSD"}],"Amazon":[{"name":"Lenovo ThinkPad X1 Carbon","price":1549.99,"description":"14-inch 2K display, Intel Core i7, 16GB RAM, 1TB SSD, Business laptop"},{"name":"ASUS VivoBook 15","price":529.99,"description":"15.6-inch FHD display, Intel Core i5, 12GB RAM, 512GB SSD"}],"Walmart":[{"name":"Acer Aspire 5","price":479.99,"description":"15.6-inch FHD display, AMD Ryzen 3, 8GB RAM, 256GB SSD"},{"name":"Microsoft Surface Laptop 5","price":1199.99,"description":"13.5-inch PixelSense touchscreen, Intel Core i5, 8GB RAM, 256GB SSD"}]}'
        return nlip.NLIP_Factory.create_json(results)



if __name__ == "__main__":
    chatapp = ChatApplication()
    webapp = nlip_ext.WebApplication(indexFile="client/dist/index.html", static_dir="client/dist")
    app = webapp.setup_webserver(chatapp, port=chatapp.local_port)