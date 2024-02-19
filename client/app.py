# Bibliothèque
import os
import customtkinter
from PIL import Image



## Classe Application

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()        

        self.title("Application VARIAN 634")
        self.geometry("700x450")
        logo_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "logo_gp.ico")
        self.iconbitmap(logo_path)

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "frontend//Images_App")
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "Polytech_clermont_logo.ico")), size=(30, 30))
        self.large_test_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "optique_spectro.png")), size=(441, 200))
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_icon_light.png")), size=(20, 20))
        self.home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))
        self.chat_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "scanning.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "scanning.png")), size=(20, 20))
        self.add_user_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "timer_light.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "timer_light.png")), size=(20, 20))

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  VARIAN 634", image=self.logo_image,
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Accueil",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.home_image, anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.frame_2_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Balayage",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.chat_image, anchor="w", command=self.frame_2_button_event)
        self.frame_2_button.grid(row=2, column=0, sticky="ew")

        self.frame_3_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Continu",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.add_user_image, anchor="w", command=self.frame_3_button_event)
        self.frame_3_button.grid(row=3, column=0, sticky="ew")

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["Light", "Dark", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # create home frame
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)

        self.home_frame_large_image_label = customtkinter.CTkLabel(self.home_frame, text="", image=self.large_test_image)
        self.home_frame_large_image_label.grid(row=0, column=0, padx=10, pady=10)

        self.home_frame_button_1 = customtkinter.CTkButton(self.home_frame, text="INFORMATIONS", image=self.image_icon_image)
        self.home_frame_button_1.grid(row=1, column=0, padx=10, pady=10)

        self.home_frame_port_arduino = customtkinter.CTkEntry(self.home_frame, width=200, placeholder_text="Numéro de port arduino ('COM')")
        self.home_frame_port_arduino.grid(row=2, column=0, padx=30, pady=10)

        # create second frame (page balayage)
        self.second_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        
        self.second_frame = customtkinter.CTkTabview(self, width=250)
        self.second_frame.grid(row=0, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.second_frame.add("Acquisition blanc")
        self.second_frame.add("Acquisition échantillon")
        self.second_frame.tab("Acquisition blanc").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
        self.second_frame.tab("Acquisition échantillon").grid_columnconfigure(0, weight=1)

        # Bontons page Balayage
        self.second_frame_button_Distance_vis = customtkinter.CTkEntry(self.second_frame.tab("Acquisition blanc"), width=200, placeholder_text="Distance parcouru par la vis")
        self.second_frame_button_Distance_vis.grid(row=2, column=0, padx=30, pady=(15, 15))        
        self.second_frame_button_acquisition_blanc = customtkinter.CTkButton(self.second_frame.tab("Acquisition blanc"), text="Acquisition blanc",
                                                           command=self.baseline_button_event)
        self.second_frame_button_acquisition_blanc.grid(row=3, column=0, padx=20, pady=(10, 10))

        


        self.second_frame_button_Distance_vis = customtkinter.CTkEntry(self.second_frame.tab("Acquisition échantillon"), width=200, placeholder_text="Distance parcouru par la vis")
        self.second_frame_button_Distance_vis.grid(row=2, column=0, padx=30, pady=(15, 15))
        
        self.second_frame_button_acquisition_blanc = customtkinter.CTkButton(self.second_frame.tab("Acquisition échantillon"), text="Acquisition échantillon",
                                                           command=self.baseline_button_event)
        self.second_frame_button_acquisition_blanc.grid(row=3, column=0, padx=20, pady=(10, 10))




        # create third frame (page continu)
        self.third_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # Bouton Page Continu
        self.third_frame = customtkinter.CTkTabview(self, width=250)
        self.third_frame.grid(row=0, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.third_frame.add("Acquisition blanc")
        self.third_frame.add("Acquisition échantillon")
        self.third_frame.tab("Acquisition blanc").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
        self.third_frame.tab("Acquisition échantillon").grid_columnconfigure(0, weight=1)

        # Bontons page continu
        self.third_frame_button_Temps = customtkinter.CTkEntry(self.third_frame.tab("Acquisition blanc"), width=200, placeholder_text="Temps d'acquisition")
        self.third_frame_button_Temps.grid(row=2, column=0, padx=30, pady=(15, 15))
        
        self.third_frame_button_longueur_d_onde = customtkinter.CTkEntry(self.third_frame.tab("Acquisition blanc"), width=200, placeholder_text="longueur d'onde")
        self.third_frame_button_longueur_d_onde.grid(row=2, column=1, padx=30, pady=(15, 15))
        self.third_frame_button_acquisition_blanc = customtkinter.CTkButton(self.third_frame.tab("Acquisition blanc"), text="Acquisition blanc",
                                                           command=self.baseline_button_event)
        self.third_frame_button_acquisition_blanc.grid(row=3, column=0, padx=20, pady=(10, 10))

        


        self.third_frame_button_Temps = customtkinter.CTkEntry(self.third_frame.tab("Acquisition échantillon"), width=200, placeholder_text="Temps d'acquisition")
        self.third_frame_button_Temps.grid(row=2, column=0, padx=30, pady=(15, 15))
        
        self.third_frame_button_longueur_d_onde = customtkinter.CTkEntry(self.third_frame.tab("Acquisition échantillon"), width=200, placeholder_text="Longueur d'onde")
        self.third_frame_button_longueur_d_onde.grid(row=2, column=1, padx=30, pady=(15, 15))
        
        self.second_frame_button_acquisition_echantillon = customtkinter.CTkButton(self.third_frame.tab("Acquisition échantillon"), text="Acquisition échantillon",
                                                           command=self.baseline_button_event)
        self.second_frame_button_acquisition_echantillon.grid(row=3, column=0, padx=20, pady=(10, 10))     

        # select default frame
        self.select_frame_by_name("home")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "frame_2" else "transparent")
        self.frame_3_button.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")

        # show selected frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "frame_2":
            self.second_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.second_frame.grid_forget()
        if name == "frame_3":
            self.third_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.third_frame.grid_forget()


    def home_button_event(self):
        self.select_frame_by_name("home")

    def frame_2_button_event(self):
        self.select_frame_by_name("frame_2")

    def frame_3_button_event(self):
        self.select_frame_by_name("frame_3")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def sidebar_button_event(self):
        print("sidebar_button click")    

    def baseline_button_event(self):
        print("Hello") 

    

if __name__ == "__main__":
    app = App()
    app.mainloop()






