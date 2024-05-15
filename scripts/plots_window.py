# Popup window to show graphs

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import matplotlib.pyplot as plt

class PlotWindow:
    def __init__(self, type: str, title: str, plots: tuple):
        """
        Class to creates popup window to show graphical outputs.

        Parameters
        ----
        type: type of output (electrical / optical / spectrum / ...)

        plots: tuple with figure objects (Tx, RX)
        """
        self.type = type
        self.title = title
        self.plots = plots
        self.popupGui()



    def popupGui(self):
        """
        Creates popup gui for setting parameters.
        """
        
        self.popup = ctk.CTkToplevel()
        self.popup.geometry("1000x700")
        self.popup.minsize(1000,700)
        self.popup.title(self.title)
        self.popup.after(100, self.popup.lift)

        generalFont = ("Helvetica", 16, "bold")
        headFont = ("Helvetica", 24, "bold")

        self.mainFrame = ctk.CTkScrollableFrame(self.popup)
        self.mainFrame.pack(fill="both", expand=True)

        self.titleLabel = ctk.CTkLabel(self.mainFrame, text=self.title, font=headFont)
        self.titleLabel.pack(padx=20, pady=20)

        self.plotsFrame = ctk.CTkFrame(self.mainFrame)
        self.plotsFrame.pack(padx=10, pady=10, fill="both", expand=True)

        # Show 3 plots
        if self.type == "optical" or self.type == "spectrum":
            # Source plot
            self.canvasTx = FigureCanvasTkAgg(figure= self.plots[2], master=self.plotsFrame)
            self.canvasTx.draw()
            self.canvasTx.get_tk_widget().pack(padx=10, pady=10)

            # Tx plot
            self.canvasTx = FigureCanvasTkAgg(figure= self.plots[0], master=self.plotsFrame)
            self.canvasTx.draw()
            self.canvasTx.get_tk_widget().pack(padx=10, pady=10)

            # Rx plot
            self.canvasRx = FigureCanvasTkAgg(figure= self.plots[1], master=self.plotsFrame)
            self.canvasRx.draw()
            self.canvasRx.get_tk_widget().pack(padx=10, pady=10)
        
        # Show 2 plots
        elif self.type == "constellation":
            # Tx plot
            self.canvasTx = FigureCanvasTkAgg(figure= self.plots[0], master=self.plotsFrame)
            self.canvasTx.draw()
            self.canvasTx.get_tk_widget().pack(padx=10, pady=10)

            # Rx plot
            self.canvasRx = FigureCanvasTkAgg(figure= self.plots[1], master=self.plotsFrame)
            self.canvasRx.draw()
            self.canvasRx.get_tk_widget().pack(padx=10, pady=10)
        
        else:
            # Tx plot
            self.canvasTx = FigureCanvasTkAgg(figure= self.plots[0], master=self.plotsFrame)
            self.canvasTx.draw()
            self.canvasTx.get_tk_widget().pack(padx=10, pady=10)

            # Rx plot
            self.canvasRx = FigureCanvasTkAgg(figure= self.plots[1], master=self.plotsFrame)
            self.canvasRx.draw()
            self.canvasRx.get_tk_widget().pack(padx=10, pady=10)

        self.closeButton = ctk.CTkButton(self.popup, text="Close", command=self.closePopup, font=generalFont)
        self.closeButton.pack(padx=20, pady=20)


    def closePopup(self):
        """
        Closes popup window.
        """
        self.popup.destroy()