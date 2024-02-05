import tkinter as tk #gui library
from tkinter import Label, Text, Button #Other imprtang part of the gui library
import requests #The requests module simplifies the process of working with HTTP, helps with web requests in Python
from PIL import Image, ImageTk #The statement from PIL import Image, ImageTk in Python is used to import specific classes (Image and ImageTk) from the PIL module. PIL stands for "Python Imaging Library," and it provides extensive capabilities for opening, manipulating, and saving many different image file formats.
import base64 #Base64 encoding is commonly used for encoding binary data, such as images or files, into a text format that can be safely transmitted in text-based protocols, like email or HTTP.
from datetime import datetime #Needed for converting a timestamp to a human readable date
import json
import time
import os
import openai
import textwrap
from PyPDF2 import PdfMerger
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import customtkinter

# DALL·E API endpoint
api_url = 'https://api.openai.com/v1/images/generations'

# Your API key, USE Your personal key. Make sure to check if you still have a key too! If not generate a new one.
api_key = "?"

def generate_quote(prompt, api_key):
    openai.api_key = api_key

    response = openai.Completion.create(
        engine = "text-davinci-003",  # You can use other engines if needed
        prompt = prompt,
        max_tokens = 60,  # You can adjust the number of tokens based on your needs
    )

    return response.choices[0].text


def create_dir(source_dir, timestamp): # Start create_dir
        # Function to create a new directory based on the timestamp
        date_time = datetime.fromtimestamp(timestamp)
        str_date_time = date_time.strftime("%d-%m-%Y__%H_%M_%S")
        new_directory = os.path.join(source_dir, str_date_time) 
        os.mkdir(new_directory)

        return str_date_time
    # End create_dir

source_dir = './'
testing_directory = create_dir(source_dir, time.time())
   
class DALLEApp: # Start DALLEEApp Class
        # Class representing the main application
    def __init__(self, root): # Start GUI
        self.root = root
        root.geometry("550x740")
        root.resizable(True, True)
        self.root.title("ColorWhiz: Coloring Book Generator")
        frame = customtkinter.CTkFrame(master=root, width=550,
                                       height=740, corner_radius=10,
                                       border_width=1)
        frame.pack(padx=10,pady=10)

        # Text Keyword input area
        self.text_label = customtkinter.CTkLabel(frame, text="Enter your subject of the coloring book page:", text_color="black", font=('Courier', 13))
        self.text_label.pack(padx=10,pady=10)
        self.text_keyword_entry = customtkinter.CTkTextbox(frame, wrap=tk.WORD, width=400, height=40, border_width=1)
        self.text_keyword_entry.pack(padx=10,pady=10)

        # Text input area
        self.text_label = customtkinter.CTkLabel(frame, text="Enter the style of the coloring book:", text_color="black", font=('Courier', 17))
        self.text_label.pack(padx=10,pady=10)
        self.text_label = customtkinter.CTkLabel(frame, text="Examples: In the style of animation for coloring book,", text_color="black", font=('Courier', 15))
        self.text_label.pack(padx=10,pady=10)
        self.text_label = customtkinter.CTkLabel(frame, text="Mandela coloring book image", text_color="black", font=('Courier', 15))
        self.text_label.pack(padx=10,pady=10)
        self.text_entry = customtkinter.CTkTextbox(frame, wrap=tk.WORD, width=500, height=100, border_width=1)
        self.text_entry.pack(padx=10,pady=10)

        # Number of images input
        self.number_label = customtkinter.CTkLabel(frame, text="Number of images:", text_color="black", font=('Courier', 17),)
        self.number_label.pack(padx=10,pady=10)
        self.number_entry = customtkinter.CTkTextbox(frame, width=10, height=1, border_width=1)
        self.number_entry.insert(tk.END, "1")  # Default to 1 image
        self.number_entry.pack(padx=10,pady=10)
       
        # Image size selection radio buttons
        self.size_label = customtkinter.CTkLabel(frame, text="Image size:", text_color="black", font=('Courier', 17))
        self.size_label.pack(padx=10, pady=10)

        self.image_size = tk.IntVar()  # Variable to store the selected image size

        # Create radio buttons for image size
        image_size_options = [("256", 256), ("512", 512), ("1024", 1024)]

        # Create a frame to hold the radio buttons and pack it horizontally
        radio_frame = customtkinter.CTkFrame(frame)
        radio_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        for option, size in image_size_options:
            radio_button = customtkinter.CTkRadioButton(radio_frame, text=option, variable=self.image_size, value=size, font=('Courier', 14))
            radio_button.pack(side=tk.LEFT, padx=10, pady=10)


        # Set the default selected image size
        self.image_size.set(256)
        
        # Generate Images button
        self.generate_button = customtkinter.CTkButton(frame, text="Generate Images and Seperate PDFs", command=self.generate_image_and_individual_pdfs, text_color="white", font=('Courier', 16), fg_color="#3b8ed0", border_width=1)
        self.generate_button.pack(padx=10,pady=15)
        
        # Generate Single and Output PDF button
        self.generate_button = customtkinter.CTkButton(frame, text="Create the Book from the Single PDFs", command=self.button_for_merging, text_color="white", font=('Courier', 16), fg_color="#3b8ed0", border_width=1)
        self.generate_button.pack(padx=10,pady=20) 
        
    """
        # Image display area
        self.image_label = customtkinter.CTkLabel(frame)
        self.image_label.pack()
    """

    # End GUI

    def generate_image_and_individual_pdfs(self): # Start generate_image_and_add_to_pdf
         # Function to generate images and individual PDFs
        keyword_text = self.text_keyword_entry.get("1.0", "end-1c")
        prompt_text = self.text_entry.get("1.0", "end-1c")
        num_images = int(self.number_entry.get("1.0", "end-1c"))
        image_size = self.image_size.get() 

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        for num_in_loop in range(num_images):
            data = {
                "prompt": keyword_text + " " + prompt_text,
                "n": 1,
                "size": f"{image_size}x{image_size}",
                "response_format": "b64_json"
            }

            response = requests.post(api_url, data=json.dumps(data), headers=headers)

            if response.status_code == 200:
            #if 200 == 200:
                response_data = json.loads(response.text)
                img_file_name = self.save_image(response_data['data'][0]['b64_json'], num_in_loop, time.time(), testing_directory )
                #img_file_name = "testFolder/1024_1024.png"
                self.create_pdf_from_image(img_file_name, keyword_text)
                
            else:
                self.display_error("Image generation failed.")
                print("API response content:")
                print(response.text)
        # End for loop for number of images
        
    # End generate_image_and_add_to_pdf
    
    def button_for_merging(self):
         # Function to handle button click for merging individual PDFs
        self.merge_all_individual_pdf(testing_directory)

    def merge_all_individual_pdf(self, testing_directory):
        # Function to merge all individual PDFs into a single PDF
        pdf_merger = PdfMerger()

        for item in os.listdir(testing_directory):
            if item.endswith('.pdf'):
                pdf_file_path = os.path.join(testing_directory, item)
                try:
                   pdf_merger.append(pdf_file_path)
                except Exception as e:
                    print(f"Error appending {pdf_file_path}: {str(e)}")

        output_pdf_path = os.path.join(testing_directory, 'output.pdf')
        pdf_merger.write(output_pdf_path)
        pdf_merger.close()
    
    def save_image(self, b64_image, num_in_loop, timestamp, testing_directory): # Start save_image
         # Function to save an image from base64 data
        image_data = base64.urlsafe_b64decode(b64_image)
        img_file_name = f'{testing_directory}/image_{num_in_loop}_{timestamp}.png'

         # Save the image as PNG
        with open(img_file_name, 'wb') as f:
            f.write(image_data)

        return img_file_name
    # End save_image

    def create_pdf_from_image(self, img_file_name, keyword_text): 

        # Create a new PDF page with the image
        new_pdf_name = img_file_name + '.pdf'  # Added '.pdf' extension
        c = canvas.Canvas(new_pdf_name, pagesize=letter)
        image_path = os.path.join(os.getcwd(), img_file_name)
        c.drawImage(image_path, 16, 100, width=580, height=580) #This line of code.
        
        text_for_chatGPT = "Please give me a fun fact about  "  + keyword_text + ".It must be appropiate for children. Keep it short and sweet."

        quote = generate_quote(text_for_chatGPT, api_key) # Make the quote be optional.
        
        c.setFont("Helvetica", 14)

        # Generate a long response text (for demonstration purposes)
        # long_response_text = "This is a long response text. It needs to be wrapped to fit within the page. " * 10
        
        # Split the long response into smaller chunks
        # wrapped_text = textwrap.fill(long_response_text, width=95)
        wrapped_text = textwrap.fill(quote, width=94)

        # Split the wrapped text into lines
        lines = wrapped_text.split('\n')

        # Starting y position for the text
        y = 80

        # Iterate over the lines and add them to the PDF
        for line in lines:
            c.drawString(16, y, line)
            y -= 14  # Adjust the vertical position for the next line

    
        #quote = generate_quote(text_for_chatGPT, api_key)
        c.showPage()  # Start a new page
        c.save()
    

if __name__ == "__main__": #? Makes the gui, display? And it keeps looping until a user exits or closes the gui?
    root = tk.Tk()
    app = DALLEApp(root)
    root.mainloop()
# End if __name__ == "__main__"


# End DALLEApp Class
