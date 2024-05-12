import openai
import configparser
from datetime import datetime
import os

class GPT3CustomerService:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.api_key = self.config['openai']['apikey']
        self.sessions = {}
        self.log_directory = 'logs'
        os.makedirs(self.log_directory, exist_ok=True)

    def start_session(self, user_id):
        #result_string = status.check(user_id)
        system_message = {
            "role": "system",
            "content": """You are an AI customer service assistant.
            You are being deployed on the webpage of a communications company.
            If the user does not start the conversation with their customer ID, ask for it.
            If, after a few attempts, you come to the conclusion that you cannot help the user:
            Direct them to https://www.dqecom.com/contact-us/support/
            and/or provide them with the customer service number 1-866-463-4237
            and/or the email support@dqe.com.
            You must only answer user queries that are related to customer service.
            If you are missing infomation, do not use placeholders.
            If you do not have specific details, refuse the query and apologize to the user.
            All of your answers must be respectful and concise.
            You can reference the following internal information if it will help the customer:
            PRIMARY NETWORK STATUS: ONLINE
            BACKUP NETWORK STATUS: OFFLINE
            ACCOUNT STATUS/NOTICES: NONE
            """  #{result_string}
        }
        self.sessions[user_id] = {"messages": [system_message]}
        self.log_message(user_id, system_message)
 
    def ask_question(self, user_id, question):
        if user_id not in self.sessions:
            self.start_session(user_id)
        
        user_message = {"role": "user", "content": question}
        self.sessions[user_id]["messages"].append(user_message)
        self.log_message(user_id, user_message)
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.sessions[user_id]["messages"],
            api_key=self.api_key
        )
        
        message_content = response['choices'][0]['message']['content']
        assistant_message = {"role": "assistant", "content": message_content}
        self.sessions[user_id]["messages"].append(assistant_message)
        self.log_message(user_id, assistant_message)
        
        return message_content

    def log_message(self, user_id, message):
        timestamp = datetime.now().isoformat()
        filename = os.path.join(self.log_directory, f"{user_id}.txt")
        with open(filename, 'a') as file:
            file.write(f"{timestamp} {message['role'].title()}: {message['content']}\n")

def main():
    config_file = 'config.ini'
    with open('user_id.txt', 'r') as file: # Reading user_id from a file
        user_id = file.read().strip()  # Ensure any extraneous whitespace is removed

    customer_service_bot = GPT3CustomerService(config_file)
    
    print("Welcome to the Customer Service Chat. Type 'quit' to exit.")
    print()
    print("Can I please have your customer ID so I can assist you?")
    print()
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
        response = customer_service_bot.ask_question(user_id, user_input)
        print("Assistant:", response)
        print()

if __name__ == "__main__":
    main()