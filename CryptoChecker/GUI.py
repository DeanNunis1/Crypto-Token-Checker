import tkinter as tk
import customtkinter as ctk
from tkinter import ttk
from PIL import ImageTk,Image  
from ttkthemes import ThemedTk
from tkinter import messagebox
import threading
from functools import partial
import Checker

# Graphical User Interface for ERC-20 token analysis
class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        # initializing the frame
        self.title("Crypto Checker")
        self.geometry("1000x600")
        self.resizable(False,False)
        self.user_id = None
        self.home_frame = HomeFrame(self)
        self.home_frame.pack(expand=True, fill=tk.BOTH)

class HomeFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # Loads the image file and create a PhotoImage object
        self.image = Image.open("images/light.jpg")
        self.photo = ImageTk.PhotoImage(self.image)

        # Creates a Canvas widget and set the image as the background
        self.canvas = tk.Canvas(self, width=self.image.width, height=self.image.height)
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.canvas.create_text(500, 35, text="Crypto Checker", fill="white", font=('CenturyGothic 40 bold'))
        self.canvas.pack(fill="both", expand=True)

        self.frame=ctk.CTkFrame(self, width=600, height=110, corner_radius=15, bg_color =("blue"), fg_color= ("midnightblue"))
        self.frame.place(x = 200, y = 80)

        self.l1=ctk.CTkLabel(self.frame, text="Contract Address",font=('Century Gothic',20))
        self.l1.place(x=210, y=5)

        self.entry1=ctk.CTkEntry(self.frame, width=350, placeholder_text='                                 Enter a Contract Address', fg_color =("Slategray1"), placeholder_text_color= ("grey35"), text_color= ("grey1"))
        self.entry1.place(x=120, y=38)

        # Create check button
        self.button1 = ctk.CTkButton(self.frame, width=150, text="Check",  corner_radius=6, command=self.check)
        self.button1.place(x=223, y=75) 

        # Array to hold the result boxes
        self.result_boxes = []

    def check(self):
        # Runs the actual do_checks function in a new thread to avoid freezing the GUI
        threading.Thread(target=self.do_checks).start()
        # Disable the button immediately after starting the thread
        self.button1.configure(state="disabled")

    def do_checks(self):
        # Clear previous result boxes
        try:
            self.clear_result_boxes()
        except:
            pass

        contract_address = self.entry1.get()

        try:
            # Creates instance of Checker.py
            imported_class_instance = Checker.ERC20Checker(contract_address)
        except ConnectionError:
            if hasattr(self, 'completed_label'):
                self.canvas.delete(self.completed_label)
            if hasattr(self, 'note'):
                self.canvas.delete(self.note)
            self.completed_label = self.canvas.create_text(495, 205, text="Invalid API key(s) in .env file", fill = 'Red', font=('Century Gothic', 13, 'bold'))
            self.after(0, self._enable_button)
            return
        except ValueError:
            if hasattr(self, 'completed_label'):
                self.canvas.delete(self.completed_label)
            if hasattr(self, 'note'):
                self.canvas.delete(self.note)
            self.completed_label = self.canvas.create_text(498, 205, text="Invalid Token Address", fill = 'Red', font=('Century Gothic', 13, 'bold'))
            self.after(0, self._enable_button)
            return

        # Check and delete the existing completed_label before creating a new one
        if hasattr(self, 'completed_label'):
            self.canvas.delete(self.completed_label)
        if hasattr(self, 'note'):
            self.canvas.delete(self.note)

        self.completed_label = self.canvas.create_text(500, 205, text="Currently Analyzing...", fill = 'white', font=('Century Gothic', 13))
        # List of function names that are called from Checker.py
        function_names = ['get_name', 'is_ownership_renounced_or_no_owner', 'check_scam_patterns', 'scrape_honeypot', 'market_cap', 'get_top_holders']  # replace with your actual function names
        # Creates a label indicating the check has been completed
        for i, function_name in enumerate(function_names):
            # Call the function and get the result
            result = getattr(imported_class_instance, function_name)()
            # Uses the Tkinter-compatible method to update the GUI
            self.create_result_box(str(result), i)

        # Add DYOR note
        self.note = self.canvas.create_text(775, 300, text="Note:\nThis analysis is not a foolproof method, various factors including team, sentiment, and new code configuration can lead to improper analysis of tokens. Please be mindful of these factors and as always be sure to do your own research into the token and team! I hope you enjoy!", fill = 'white', font=('Century Gothic', 11, 'bold'), width= 285, justify="center")
        # Destroy the label
        self.canvas.delete(self.completed_label)
        # Create a new label
        self.completed_label = self.canvas.create_text(495, 205, text="Token Analysis Complete!", fill = 'white', font=('Century Gothic', 13))
        # At the end of do_search, re-enable the button
        self.after(0, self._enable_button)
    
    def create_result_box(self, result, i):
        # This method is called from the new thread, so we need to make it safe for use with Tkinter
        self.after(0, self._create_result_box, result, i)

    def _create_result_box(self, result, i):
        # This is the actual method that updates the GUI
        WIDTH = 80  # width of a box
        HEIGHT = 1.5  # height of a box
        LABEL_HEIGHT = 20  # height of the label
        LABEL_HEIGHT_FACTOR = 23
        LABEL_FONT_SIZE = 15  # font size of the label
        Label_Names = [' Name ', ' Owner ', ' Contract ', ' Honeypot ', ' Market Info ', ' Top 10 Holders ']

        # Calculate margins dynamically
        X_MARGIN = 20  # horizontal margin
        Y_MARGIN = 270  # vertical margin

        # Calculate the position of the box
        x = X_MARGIN
        if i == 0:
            y = Y_MARGIN + i * (HEIGHT * 22 + LABEL_HEIGHT) - 45
            HEIGHT /= 2.5
            label = ctk.CTkLabel(self, height=int(HEIGHT*LABEL_HEIGHT_FACTOR), text=Label_Names[i], font=('Century Gothic', LABEL_FONT_SIZE), fg_color="blue", text_color="grey99", corner_radius= 5)
            label.place(x=x, y=y)  # place the label to the left of the box
        elif i == 1:
            y = Y_MARGIN + i * (HEIGHT * 22 + LABEL_HEIGHT) - 60
            label = ctk.CTkLabel(self, height=int(HEIGHT*LABEL_HEIGHT_FACTOR), text=Label_Names[i], font=('Century Gothic', LABEL_FONT_SIZE-1), fg_color="blue", text_color="grey99", corner_radius= 5)
            label.place(x=x, y=y+2)  # place the label to the left of the box
        elif i == 5:
            y = Y_MARGIN + i * (HEIGHT * 22 + LABEL_HEIGHT) - 60
            HEIGHT *= 4  # make it six times as tall
            label = ctk.CTkLabel(self, height=int(HEIGHT*LABEL_HEIGHT_FACTOR)-40, text=Label_Names[i], font=('Century Gothic', LABEL_FONT_SIZE-1), fg_color="blue", text_color="grey99", corner_radius= 5)
            label.place(x=x, y=y)  # place the label to the left of the box
        else:
            y = Y_MARGIN + i * (HEIGHT * 22 + LABEL_HEIGHT) - 60
            label = ctk.CTkLabel(self, height=int(HEIGHT*LABEL_HEIGHT_FACTOR), text=Label_Names[i], font=('Century Gothic', LABEL_FONT_SIZE), fg_color="blue", text_color="grey99", corner_radius= 5)
            label.place(x=x, y=y+2)  # place the label to the left of the box

        # Create the result box
        result_box = tk.Text(self, height=HEIGHT, width=WIDTH, background='Slategray1', fg='gray1')
        result_box.insert(tk.END, result)
        # Disable the result box to prevent user editing
        result_box.config(state=tk.DISABLED)
        if i == 5:
            result_box.config(width=WIDTH)  # force width
        elif i == 4:
            result_box.config(width=WIDTH -7)  # force width
        else:
            result_box.config(width=WIDTH-30)  # force width

        result_box.place(x=x + LABEL_HEIGHT + 80 + 10 * i, y=y)

        # Save the result box and label in the array
        self.result_boxes.append((result_box, label))
    
    # Method to clear results upon new check
    def clear_result_boxes(self):
        # Delete previous result boxes and labels
        for result_box, label in self.result_boxes:
            result_box.destroy()
            label.destroy()
        self.result_boxes = []
        if hasattr(self, 'completed_label'):
            self.completed_label.destroy()
    
    # Method to enable Check button
    def _enable_button(self):
        self.button1.configure(state="normal")

if __name__ == "__main__":
    app = MyApp()
    app.mainloop()



            