from nlip_web.genai import StatefulGenAI
from nlip_web  import nlip_ext as nlip_ext 
from nlip_web.env import read_digits, read_string
from nlip_server import server
from nlip_sdk import nlip

from website_modules import main_module as mm
import re

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
        print ("\n\nUser Original text: ", text, "\n\n")

        search_term = ""
        # while search_term.replace(" ", "") == "":
        prompt_1 = (
            "\"" + text + "\"\n"
            "Analyze this shopping request. Extract the Product, Brand, and translate casual adjectives into technical specs. "
            "If the User provides their use case without knowing what product would fit their application, infer the appropriate technical attributes needed and recommend the product accordingly. "
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
        "Return MAXIMUM 6 words. "
        "Final returned optimized search term must be max 6 words long strict rule."
        "Example output: 'Power Drill DeWalt Heavy Duty' or 'Phone 128gb Android, or 'Lumber 2x4', 'Speaker Wire Cable Managment Drywall'."
        )
        #pass prompt 2 to optimize search term
        response = chat_server.chat(prompt_2)
        print("\n\nShortened Optimized search: " ,response, "\n\n")
        search_term = chat_server.chat("\"" + response + "\"\n"
                                       "summarize the provded search term to maximum 6 words only, remove all special characters and symbols, return only the optimized search term. no other text."
                                       )

            # match_product = re.search(r"Product:\s*(.+)\n", response)
            # product = match_product.group(1).strip() if match_product else ""

            # match_brand = re.search(r"Brand:\s*(.+)\n", response)
            # brand = match_brand.group(1).strip() if match_brand else ""
            # if brand.lower() in ["not specified", "not provided", "unknown", "none", "n/a"]:
            #     brand = ""
            # search_term = f"{brand} {product}".strip()
        
        print("Final Search Term is: ", search_term)
        results = mm.search_product(search_term)
        # results = mm.single_thread_search_product(response)

        products = nlip.NLIP_Factory.create_json(results)
        return products 


if __name__ == "__main__":
    chatapp = ChatApplication()
    webapp = nlip_ext.WebApplication(indexFile="client/dist/index.html", static_dir="client/dist")
    app = webapp.setup_webserver(chatapp, port=chatapp.local_port)