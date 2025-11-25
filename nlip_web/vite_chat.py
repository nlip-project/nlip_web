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
        print ("\n\nUser Origional text: ", text, "\n\n")

        prompt_1 = (
            "\"" + text + "\"\n"
            "Analyze this shopping request. Extract the Product, Brand, and translate casual adjectives into technical specs. "
            "(e.g., change 'strong' to 'Heavy Duty', 'cheap' to 'Budget', 'fast' to 'High Speed'). "
            "CRITICAL: Do NOT add attributes (like price, speed, or budget) if the user did not explicitly mention them. "
            "Output ONLY the Brand, Product, and Valid Technical Attributes found in the text."
        )
        #pass prompt 1 to summarize search parameters
        response = chat_server.chat(prompt_1)
        print("Search Summary is: ", response)

        prompt_2 = (
            "\"" + response + "\"\n"
            "Convert this summary into a clean search bar string, for shopping wesites like Amazon Canada ,Home Depot Canada etc. "
            "Format as a space-separated string: [Product Category] [Brand] [Key Technical Adjective]."
            "Key Technical Adjective are derived from technical attributes and User Requirments interpret these to create meaningful Adjectives."
            "Do not use symbols like '+' or '-' or '-' etc. Remove filler words like 'capable of', 'for', 'with'. "
            "Max 6 words. "
            "Example output: 'Power Drill DeWalt Heavy Duty' or 'Phone 128gb Android."
        )
        #pass prompt 2 to optimize search term
        response = chat_server.chat(prompt_2)
        print("\n\nShortened Optimized search: " ,response, "\n\n")
        
        # pass search term to website_modules main search function
        # results = mm.search_product(response)
        results = mm.single_thread_search_product(response)
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