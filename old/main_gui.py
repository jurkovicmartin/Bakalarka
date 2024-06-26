# Main window

# SpS = samples per symbol, Rs = symbol rate, Fs sampling frequency, Ts sampling period

import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from scripts.parameters_window import ParametersWindow
from scripts.plots_window import PlotWindow
from scripts.simulation import simulate, getValues, getPlot
from scripts.parameters_functions import convertNumber
import matplotlib.pyplot as plt

class Gui:
    def __init__(self):
        self.root = tk.Tk()

        self.root.wm_state("zoomed")
        #self.root.geometry("1000x600")
        self.root.title("Optical modulaton simulation application")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Design
        charset="Helvetica"
        myGrey = "light grey"
        myBlue = "#adadeb"
        self.root.option_add("*Font", (charset, 14))

        ### VARIABLES
        
        # Inicial parameters
        self.sourceParameters = {"Power": 0, "Frequency": 0, "Linewidth": 0, "RIN": 0, "Ideal": False}
        self.modulatorParameters = {"Type": "PM"}
        self.channelParameters = {"Length": 0, "Attenuation": 0, "Dispersion": 0, "Ideal": False}
        self.recieverParameters = {"Type": "Photodiode", "Bandwidth": 0, "Resolution": 0, "Ideal": False}
        self.amplifierParameters = {"Position": "start", "Gain": 0, "Noise": 0, "Detection": 0, "Ideal": False}
        # Store initial parameters to check for simulation start
        self.initialParameters = {"Source": self.sourceParameters, "Modulator": self.modulatorParameters, 
                                  "Channel": self.channelParameters, "Reciever": self.recieverParameters, "Amplifier": self.amplifierParameters}

        self.generalParameters = {"SpS":8}

        # Default parameters (testing)
        self.sourceParameters = {"Power": 10, "Frequency": 191.7, "Linewidth": 1, "RIN": 0, "Ideal": True}
        self.modulatorParameters = {"Type": "MZM"}
        self.channelParameters = {"Length": 40, "Attenuation": 0, "Dispersion": 0, "Ideal": True}
        self.recieverParameters = {"Type": "Photodiode", "Bandwidth": "inf", "Resolution": "inf", "Ideal": True}
        self.amplifierParameters = {"Position": "start", "Gain": 0, "Noise": 0, "Detection": 0, "Ideal": False}



        # Simulation results variables
        self.plots = {}
        self.simulationResults = None

        # Notebook tabs frame
        self.notebookFrame = ttk.Notebook(self.root)
        self.notebookFrame.grid(row=0, column=0, sticky="nsew")

        # Tabs
        self.optionsFrame = tk.Frame(self.notebookFrame, bg=myGrey)
        self.outputsFrame = tk.Frame(self.notebookFrame)

        self.optionsFrame.pack(padx=10)
        self.outputsFrame.pack()

        self.notebookFrame.add(self.optionsFrame, text="Input options")
        self.notebookFrame.add(self.outputsFrame, text="Outputs")

        

        ### OPTIONS TAB

        # Create a custom style
        style = ttk.Style()
        style.theme_use("default")  # Use the default theme
        style.configure("Custom.TCombobox", background=myGrey)  # Set the background color
        
        # Options tab frames
        self.generalFrame = tk.Frame(self.optionsFrame, bg=myBlue, borderwidth=1, relief="solid")
        self.schemeFrame = tk.Frame(self.optionsFrame, bg=myBlue, borderwidth=1, relief="solid")

        # Create a canvas to draw the rounded border
        self.generalFrame.pack(fill="both", padx=10, pady=10)
        self.schemeFrame.pack(fill="both", padx=10, pady=10, expand=True)


        # General frame

        # General label
        generalLabelFrame = tk.Frame(self.generalFrame, bg="white", borderwidth=1, relief="solid")
        generalLabelFrame.grid(row=0, column=0, columnspan=4, padx=10, pady=10)
        self.generalLabel = tk.Label(generalLabelFrame, text="General parameters", bg=myGrey, font=(charset, 20))
        self.generalLabel.pack(padx=3, pady=3)

        # Choosing modulation format to map
        self.mFormatLabel = tk.Label(self.generalFrame, text="Modulation format", bg=myBlue)
        self.mFormatComboBox = ttk.Combobox(self.generalFrame, values=["OOK", "PAM", "PSK", "QAM"], state="readonly", width=10, justify="center")
        self.mFormatComboBox.set("OOK")
        self.mFormatComboBox.bind("<<ComboboxSelected>>", self.modulationFormatChange)
        self.mFormatLabel.grid(row=1, column=0, padx=10, pady=10)
        self.mFormatComboBox.grid(row=2, column=0, padx=10, pady=10)

        # Choosing modulation order to map
        self.mOrderLabel = tk.Label(self.generalFrame, text="Order of modulation", bg=myBlue)
        self.mOrderCombobox = ttk.Combobox(self.generalFrame, values=["2"], state="disabled", width=10, justify="center")
        self.mOrderCombobox.set("2")
        self.mOrderLabel.grid(row=1, column=1, padx=10, pady=10)
        self.mOrderCombobox.grid(row=2, column=1, padx=10, pady=10)

        # Symbol rate
        self.symbolRateLabel = tk.Label(self.generalFrame, text="Symbol rate [symbols/s]", bg=myBlue)
        self.symbolRateEntry = tk.Entry(self.generalFrame, bg=myGrey, width=10)
        self.symbolRateEntry.insert(0, "1")
        self.symbolRateCombobox = ttk.Combobox(self.generalFrame, values=["M (10^6)", "G (10^9)"], state="readonly", width=10, justify="center")
        self.symbolRateCombobox.set("M (10^6)")
        self.symbolRateLabel.grid(row=1, column=2, columnspan=2, padx=10, pady=10)
        self.symbolRateEntry.grid(row=2, column=2, padx=3, pady=10)
        self.symbolRateCombobox.grid(row=2, column=3, pady=10)

        

        # Scheme frame
        # Configure grid ro expand
        self.schemeFrame.grid_columnconfigure(0, weight=1)  
        self.schemeFrame.grid_columnconfigure(1, weight=1)  
        self.schemeFrame.grid_columnconfigure(2, weight=1)  
        self.schemeFrame.grid_columnconfigure(3, weight=1)  
        self.schemeFrame.grid_columnconfigure(4, weight=1)  
        self.schemeFrame.grid_columnconfigure(5, weight=1)

        schemeLabelFrame = tk.Frame(self.schemeFrame, bg="white", borderwidth=1, relief="solid")
        schemeLabelFrame.grid(row=0, column=0, columnspan=6, padx=10, pady=10)
        self.schemeLabel = tk.Label(schemeLabelFrame, text="Optical communication chain parameters", bg=myGrey, font=(charset, 20))
        self.schemeLabel.pack(padx=3, pady=3)

        # Source
        self.sourceFrame = tk.Frame(self.schemeFrame, bd=1, relief="solid", bg=myGrey)
        self.sourceFrame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

        self.sourceLabel = tk.Label(self.sourceFrame, text="Optical source", bg=myGrey)
        self.sourceLabel.pack(padx=5, pady=5)

        self.sourceButton = tk.Button(self.sourceFrame, text="", command=lambda: self.showParametersPopup(self.sourceButton), bg=myGrey)
        self.sourceButton.pack(padx=5, pady=5, fill="both", expand=True)

        # Modulator
        self.modulatorFrame = tk.Frame(self.schemeFrame, bd=1, relief="solid", bg=myGrey)
        self.modulatorFrame.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")

        self.modulatorLabel = tk.Label(self.modulatorFrame, text="Modulator", bg=myGrey)
        self.modulatorLabel.pack(padx=5, pady=5)

        self.modulatorButton = tk.Button(self.modulatorFrame, text="", command=lambda: self.showParametersPopup(self.modulatorButton), bg=myGrey)
        self.modulatorButton.pack(padx=5, pady=5, fill="both", expand=True)

        # Channel
        self.channelFrame = tk.Frame(self.schemeFrame, bd=1, relief="solid", bg=myGrey)
        self.channelFrame.grid(row=2, column=2, padx=5, pady=5, sticky="nsew")

        self.channelLabel = tk.Label(self.channelFrame, text="Communication channel", bg=myGrey)
        self.channelLabel.pack(padx=5, pady=5)

        self.channelButton = tk.Button(self.channelFrame, text="", command=lambda: self.showParametersPopup(self.channelButton), bg=myGrey)
        self.channelButton.pack(padx=5, pady=5, fill="both", expand=True)

        # Reciever
        self.recieverFrame = tk.Frame(self.schemeFrame, bd=1, relief="solid", bg=myGrey)
        self.recieverFrame.grid(row=2, column=3, padx=5, pady=5, sticky="nsew")

        self.recieverLabel = tk.Label(self.recieverFrame, text="Detector", bg=myGrey)
        self.recieverLabel.pack(padx=5, pady=5)

        self.recieverButton = tk.Button(self.recieverFrame, text="", command=lambda: self.showParametersPopup(self.recieverButton), bg=myGrey)
        self.recieverButton.pack(padx=5, pady=5, fill="both", expand=True)

        # Amplifier button initially hidden
        self.amplifierFrame = tk.Frame(self.schemeFrame, bd=1, relief="solid", bg=myGrey)

        self.amplifierLabel = tk.Label(self.amplifierFrame, text="Optical amplifier", bg=myGrey)
        self.amplifierLabel.pack(padx=5, pady=5)

        self.amplifierButton = tk.Button(self.amplifierFrame, text="", command=lambda: self.showParametersPopup(self.amplifierButton), bg=myGrey)
        self.amplifierButton.pack(padx=5, pady=5, fill="both", expand=True)

        # Channel with amplifier
        self.amplfierChannelFrame = tk.Frame(self.schemeFrame, bd=1, relief="solid", bg=myGrey)
        self.amplfierChannelFrame.grid_columnconfigure(0, weight=1)  
        self.amplfierChannelFrame.grid_columnconfigure(1, weight=1) 

        self.channelLabel = tk.Label(self.amplfierChannelFrame, text="Communication channel", bg=myGrey)
        self.channelLabel.grid(row=0, column=0, padx=10, pady=10) 
        self.comboChannelButton = tk.Button(self.amplfierChannelFrame, text="", command=lambda: self.showParametersPopup(self.channelButton), bg=myGrey)
        self.comboChannelButton.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.amplifierLabel = tk.Label(self.amplfierChannelFrame, text="Optical amplifier", bg=myGrey)
        self.amplifierLabel.grid(row=0, column=1, padx=10, pady=10)
        self.comboAmplifierButton = tk.Button(self.amplfierChannelFrame, text="", command=lambda: self.showParametersPopup(self.amplifierButton), bg=myGrey)
        self.comboAmplifierButton.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        

        # Show default parameters
        self.setButtonText("all")     


        # Checkbutton for including / excluding channel pre-amplifier
        self.amplifierCheckVar = tk.BooleanVar()
        self.amplifierCheckbutton = tk.Checkbutton(self.schemeFrame, text="Add amplifier", variable=self.amplifierCheckVar, command=self.amplifierCheckbuttonChange, bg=myBlue, activebackground=myBlue)
        self.amplifierCheckbutton.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # Attention label for adding pre-amplifier
        # self.attentionLabel = tk.Label(self.generalFrame, text="")
        # self.attentionLabel.grid(row=2, column=1, columnspan=2)


        # Other

        # Start simulation
        self.simulateButton = tk.Button(self.optionsFrame, text="Simulate", command=self.startSimulation)
        self.simulateButton.pack(padx=10, pady=10)

        # Quit
        self.quitButton = tk.Button(self.optionsFrame, text="Quit", command=self.terminateApp)
        self.quitButton.pack(padx=10, pady=10)


        ### OUTPUTS TAB

        # Frames

        self.valuesFrame = tk.Frame(self.outputsFrame)
        self.plotsFrame = tk.Frame(self.outputsFrame)

        self.valuesFrame.pack()
        self.plotsFrame.pack()

        # Values frame

        self.powerTxWLabel = tk.Label(self.valuesFrame, text="Average Tx power:")
        self.powerTxdBmLabel = tk.Label(self.valuesFrame, text="Average Tx power:")
        self.powerRxWLabel = tk.Label(self.valuesFrame, text="Average Rx power:")
        self.powerRxdBmLabel = tk.Label(self.valuesFrame, text="Average Rx power:")
        self.powerTxWLabel.grid(row=0, column=0)
        self.powerTxdBmLabel.grid(row=0, column=1)
        self.powerRxWLabel.grid(row=1, column=0)
        self.powerRxdBmLabel.grid(row=1, column=1)

        self.transSpeedLabel = tk.Label(self.valuesFrame, text="Transmission speed:")
        self.snrLabel = tk.Label(self.valuesFrame, text="SNR:")
        self.berLabel = tk.Label(self.valuesFrame, text="BER:")
        self.serLabel = tk.Label(self.valuesFrame, text="SER:")
        self.transSpeedLabel.grid(row=2, column=0)
        self.snrLabel.grid(row=2, column=1)
        self.berLabel.grid(row=3, column=0)
        self.serLabel.grid(row=3, column=1)

        # Plots Frame

        # Electrical
        self.electricalButton = tk.Button(self.plotsFrame, text="Show information signals", command=lambda: self.showPlots(self.electricalButton))
        self.electricalButton.grid(row=0, column=0)
        # Optical
        self.opticalButton = tk.Button(self.plotsFrame, text="Show optical signals", command=lambda: self.showPlots(self.opticalButton))
        self.opticalButton.grid(row=1, column=0)
        # Spectrum
        self.spectrumButton = tk.Button(self.plotsFrame, text="Show spectum of signals", command=lambda: self.showPlots(self.spectrumButton))
        self.spectrumButton.grid(row=2, column=0)
        # Constellation diagrams
        self.constellationButton = tk.Button(self.plotsFrame, text="Show constellation diagrams", command=lambda: self.showPlots(self.constellationButton))
        self.constellationButton.grid(row=3, column=0)
        # Eye diagrams
        self.eyeButton = tk.Button(self.plotsFrame, text="Show eye diagrams", command=lambda: self.showPlots(self.eyeButton))
        self.eyeButton.grid(row=4, column=0)


        # Frames with buttons that will be disabled when doing configuration
        self.buttonFrames = [self.optionsFrame, self.plotsFrame, self.sourceFrame, self.modulatorFrame, self.channelFrame, self.recieverFrame, self.amplifierFrame, self.amplfierChannelFrame]

        self.root.mainloop()



    ### METHODS

    def terminateApp(self):
        """
        Terminate the app. Closes main window and all other opened windows.
        """
        # Toplevels windows (graphs)
        self.closeGraphsWindows()
        # Main window
        self.root.destroy()

    def startSimulation(self):
        """
        Start of simulation.
        Main function button.
        """
        # Get values of general parameters
        if not self.updateGeneralParameters(): return

        # Not all parameters provided
        if not self.checkParameters(): return

        # Amplifier with ideal channel
        # if self.amplifierCheckVar.get() and self.channelParameters.get("Ideal"):
        #    messagebox.showwarning("Simulation warning", "Amplifier will be ignored because of ideal channel.")
        
        # Clear plots for new simulation (othervise old graphs would be shown)
        self.plots.clear()

        # Simulation
        self.simulationResults = simulate(self.generalParameters, self.sourceParameters, self.modulatorParameters,
                                           self.channelParameters, self.recieverParameters, self.amplifierParameters)
        
        # Signal power is too low for amplifier detection
        if self.simulationResults.get("recieverSignal") is None:
            messagebox.showerror("Simulation error", "Signal power is too low to be detected by amplifier !")
            # Clear simulation results (bcs of graphs)
            self.simulationResults = None

            return
        # Showing results
        else:
            # Values to show
            outputValues = getValues(self.simulationResults, self.generalParameters)
            # Actual showing in the app
            self.showValues(outputValues)

            messagebox.showinfo("Simulation status", "Simulation succesfully completed")


    def amplifierCheckbuttonChange(self):
        """
        Including / exluding amplifier from the scheme.
        """
        # Show amplifier button
        if self.amplifierCheckVar.get():
            # Postion
            amplifierPosition = self.amplifierParameters.get("Position")

            if amplifierPosition == "start":
                self.amplfierChannelFrame.grid_forget()
                self.amplifierFrame.grid(row=2, column=2, padx=5, pady=5, sticky="nsew")
                self.channelFrame.grid(row=2, column=3, padx=5, pady=5, sticky="nsew")
                self.recieverFrame.grid(row=2, column=4, padx=5, pady=5, sticky="nsew")

            elif amplifierPosition == "middle":
                self.channelFrame.grid_forget()
                self.amplifierFrame.grid_forget()
                self.amplfierChannelFrame.grid(row=2, column=2, padx=5, pady=5, sticky="nsew")
                self.recieverFrame.grid(row=2, column=3, padx=5, pady=5, sticky="nsew")


            elif amplifierPosition =="end":
                self.amplfierChannelFrame.grid_forget()
                self.channelFrame.grid(row=2, column=2, padx=5, pady=5, sticky="nsew")
                self.amplifierFrame.grid(row=2, column=3, padx=5, pady=5, sticky="nsew")
                self.recieverFrame.grid(row=2, column=4, padx=5, pady=5, sticky="nsew")

            else:
                raise Exception("Unexpected error")
            
            # self.attentionCheck()
        else:
            # Remove amplifier button
            self.amplfierChannelFrame.grid_forget()
            self.amplifierFrame.grid_forget()
            self.channelFrame.grid(row=2, column=2, padx=5, pady=5, sticky="nsew")
            self.recieverFrame.grid(row=2, column=3, padx=5, pady=5, sticky="nsew")

            # self.attentionCheck()

        self.setButtonText("channel")
        self.setButtonText("amplifier")


    def showParametersPopup(self, clickedButton):
        """
        Show Toplevel popup window to set parametrs.
        """
        # Some general parameter was not ok
        if not self.updateGeneralParameters():
            return

        # Disable the other buttons when a popup is open
        self.disableButtons()

        # Open a new popup
        if clickedButton == self.sourceButton:
            ParametersWindow(self, clickedButton, "source", self.getParameters, self.sourceParameters, self.generalParameters)
        elif clickedButton == self.modulatorButton:
            ParametersWindow(self, clickedButton, "modulator", self.getParameters, self.modulatorParameters, self.generalParameters)
        elif clickedButton == self.channelButton:
            ParametersWindow(self, clickedButton, "channel", self.getParameters, self.channelParameters, self.generalParameters)
        elif clickedButton == self.recieverButton:
            ParametersWindow(self, clickedButton, "reciever", self.getParameters, self.recieverParameters, self.generalParameters)
        elif clickedButton == self.amplifierButton:
            ParametersWindow(self, clickedButton, "amplifier", self.getParameters, self.amplifierParameters, self.generalParameters)
        else: raise Exception("Unexpected error")

        
    def disableButtons(self):
        """
        Disable buttons when window to set parameters is opened
        """
        for frame in self.buttonFrames:
            for button in frame.winfo_children():
                if isinstance(button, tk.Button):
                    button.config(state="disabled")


    def enableButtons(self):
        """
        Enable buttons when parameters have been set
        """
        for frame in self.buttonFrames:
            for button in frame.winfo_children():
                if isinstance(button, tk.Button):
                    button.config(state="normal")


    def getParameters(self, parameters: dict, buttonType: str):
        """
        Get parameters from popup window.

        Parameters
        -----
        parameters: variable to get

        buttonType: type of button pressed

            "source" / "modulator" / "channel" / "reciever" / "amplifier"
        """
        if buttonType == "source":
            self.sourceParameters = parameters
        elif buttonType == "modulator":
            self.modulatorParameters = parameters
        elif buttonType == "channel":
            self.channelParameters = parameters
        elif buttonType == "reciever":
            self.recieverParameters = parameters
        elif buttonType == "amplifier":
            self.amplifierParameters = parameters
            # Update amplifier position
            self.amplifierCheckbuttonChange()
        else: raise Exception("Unexpected error")

        # Update showed parameters
        self.setButtonText(buttonType)


    def checkParameters(self) -> bool:
        """
        Checks if all needed parameters are set
        """
        # There is only 1 general paramete (Fs), means some problem with setting other parameters
        if len(self.generalParameters) == 1:
            return False
        # Source parameters are same as initial
        elif self.sourceParameters == self.initialParameters.get("Source"):
            messagebox.showerror("Simulation error", "You must set source parameters.")
            return False
        # elif self.modulatorParameters == self.initialParameters.get("Modulator"):
        #     messagebox.showerror("Simulation error", "You must set modulator parameters.")
        #     return False
        elif self.channelParameters == self.initialParameters.get("Channel"):
            messagebox.showerror("Simulation error", "You must set channel parameters.")
            return False
        elif self.recieverParameters == self.initialParameters.get("Reciever"):
            messagebox.showerror("Simulation error", "You must set reciever parameters.")
            return False
        # Only if amplifier is included
        elif self.amplifierCheckVar.get() and self.amplifierParameters == self.initialParameters.get("Amplifier"):
            messagebox.showerror("Simulation error", "You must set amplifier parameters.")
            return False
        else: return True


    def modulationFormatChange(self, event):
        """
        Change modulation order options when modulation format is changed
        """
        # Setting order options for selected modulation format
        if self.mFormatComboBox.get() == "OOK":
            orderOptions = ["2"]
            # Disable modulation order combobox for OOK format
            self.mOrderCombobox.config(state="disabled")
        elif self.mFormatComboBox.get() == "PAM":
            orderOptions = ["4"]
            # Enable modulation order combobox
            self.mOrderCombobox.config(state="readonly")
        elif self.mFormatComboBox.get() == "PSK":
            orderOptions = ["2", "4", "8", "16"]
            # Enable modulation order combobox
            self.mOrderCombobox.config(state="readonly")
        elif self.mFormatComboBox.get() == "QAM":
            orderOptions = ["4", "16", "64", "256"]
            # Enable modulation order combobox
            self.mOrderCombobox.config(state="readonly")
        else: raise Exception("Unexpected error")

        # Sets new options to modulation order combobox
        self.mOrderCombobox.config(values=orderOptions)
        self.mOrderCombobox.set(orderOptions[0])


    def updateGeneralParameters(self) -> bool:
        """
        Update general parameters with values from editable fields.

        Returns
        ----
        False: some parameter was not ok

        True: all general parameters are ok
        """
        # Modulation format and order
        self.generalParameters.update({"Format": self.mFormatComboBox.get().lower(), "Order": int(self.mOrderCombobox.get())})

        # OOK is created same as 2 order PAM
        if self.mFormatComboBox.get() == "OOK":
            self.generalParameters.update({"Format": "pam"})

        if not(self.checkSymbolRate()):
            # Symbol rate is not ok
            return False
        
        self.generalParameters.update({"Fs":self.generalParameters.get("SpS") * self.generalParameters.get("Rs")})
        self.generalParameters.update({"Ts":1 / self.generalParameters.get("Fs")})

        return True
    

    def checkSymbolRate(self) -> bool:
        """
        Checks if inputed symbol rate is valid and sets its if yes.
        """
        # Checks if it is a number and covert it
        Rs, isEmpty = convertNumber(self.symbolRateEntry.get())
        if Rs is None and isEmpty:
            messagebox.showerror("Symbol rate input error", "You must input symbol rate!")
            return False
        elif Rs is None and not isEmpty:
            messagebox.showerror("Symbol rate input error", "Symbol rate must be a number!")
            return False
        elif Rs != int(Rs):
            messagebox.showerror("Symbol rate input error", "Symbol rate must whole number!")
            return False
        # Rs is number
        else: pass
        
        # Set the rigth value
        if self.symbolRateCombobox.get() == "M (10^6)":
            Rs = Rs * 10**6
        elif self.symbolRateCombobox.get() == "G (10^9)":
            Rs = Rs * 10**9
        else:
            raise Exception("Unexpected error")

        # Checks size of the number
        if Rs < 1000000: # 1 M
            messagebox.showerror("Symbol rate input error", "Symbol rate is too low")
            return False
        elif self.generalParameters.get("Format") == "pam" and self.generalParameters.get("Order") == 2 and Rs >= 10**11: # 100G OOK
            messagebox.showerror("Symbol rate input error", "Symbol rate for OOK is too high")
            return False
        elif Rs >= 10**12: # 1T
            messagebox.showerror("Symbol rate input error", "Symbol rate is too high")
            return False
        # Symbol rate is ok
        else:
            self.generalParameters.update({"Rs":Rs})
            return True

    
    def showValues(self, outputValues: dict):
        """
        Show values from dictionary in the app.
        """
        # ' ' insted of " " because of f-string 
        self.powerTxWLabel.config(text=f"Average Tx power: {outputValues.get('powerTxW') / 1e-3:.3} mW")
        self.powerTxdBmLabel.config(text=f"Average Tx power: {outputValues.get('powerTxdBm'):.3} dBm")
        self.powerRxWLabel.config(text=f"Average Rx power: {outputValues.get('powerRxW') / 1e-3 :.3} mW")
        self.powerRxdBmLabel.config(text=f"Average Rx power: {outputValues.get('powerRxdBm'):.3} dBm")
        
        self.showTransSpeed(outputValues.get("Speed"))
        self.snrLabel.config(text=f"SNR: {outputValues.get('SNR'):.3} dB")
        self.berLabel.config(text=f"BER: {outputValues.get('BER'):.3}")
        self.serLabel.config(text=f"SER: {outputValues.get('SER'):.3}")


    def showTransSpeed(self, transmissionSpeed: float):
        """
        Shows transmission speed in the app with reasonable units
        """
        if transmissionSpeed >= 10**9:
            self.transSpeedLabel.config(text=f"Transmission speed: {transmissionSpeed / 10**9} Gb/s")
        elif transmissionSpeed >= 10**6:
            self.transSpeedLabel.config(text=f"Transmission speed: {transmissionSpeed / 10**6} Mb/s")
        elif transmissionSpeed >= 10**3:
            self.transSpeedLabel.config(text=f"Transmission speed: {transmissionSpeed / 10**3} kb/s")
        # Should not happen
        else:
            self.transSpeedLabel.config(text=f"Transmission speed: {transmissionSpeed} b/s")


    def showPlots(self, clickedButton):
        """
        Show plots in popup windows. Plots are defined by clickedButton.
        """
        # Trying to show plots without simulation data
        if self.simulationResults is None:
            messagebox.showerror("Showing error", "You must start simulation first.")
            return

        # Define which button was clicked to get rigth plot
        if clickedButton == self.electricalButton:
            type = "electrical"
            title = "Infromation signals"
        elif clickedButton == self.opticalButton:
            type = "optical"
            title = "Optical signals"
        elif clickedButton == self.spectrumButton:
            type = "spectrum"
            title = "Spectrum of signals"
        elif clickedButton == self.constellationButton:
            type = "constellation"
            title = "Constellation diagrams"
        elif clickedButton == self.eyeButton:
            type = "eye"
            title = "Eye diagrams"
        else: raise Exception("Unexpected error")

        plots = self.loadPlot(type)

        plotWindow = PlotWindow(type, title, plots)


    def loadPlot(self, type: str) -> tuple[plt.Figure, plt.Figure]:
        """
        Get figure objects to display.

        Returns
        ----
        tuple with figure (Tx, Rx, Source)
        ! source figure is returned only for optical and spectrum
        in other cases Source is None
        """
        if type == "electrical":
            keyTx = "electricalTx"
            keyRx = "electricalRx"
            titleTx = "Modulation signal"
            titleRx = "Detected signal"            
        elif type == "optical":
            keyTx = "opticalTx"
            keyRx = "opticalRx"
            keySc = "opticalSc"
            titleTx = "Modulated signal"
            titleRx = "Reciever signal"
            titleSc = "Source signal"  
        elif type == "spectrum":
            keyTx = "spectrumTx"
            keyRx = "spectrumRx"
            keySc = "spectrumSc"
            titleTx = "Tx spectrum signal"
            titleRx = "Rx spectrum signal"
            titleSc = "Source spectrum" 
        elif type == "constellation":
            keyTx = "constellationTx"
            keyRx = "constellationRx"
            titleTx = "Tx constellation diagram"
            titleRx = "Rx constellation diagram" 
        elif type == "eye":
            keyTx = "eyeTx"
            keyRx = "eyeRx"
            titleTx = "Tx eyediagram"
            titleRx = "Rx eyediagram" 
        else: raise Exception("Unexpected error")

        # Tx graph was once showed before
        if keyTx in self.plots:
            plotTx = self.plots.get(keyTx)
        else:
            plotTx = getPlot(keyTx, titleTx, self.simulationResults, self.generalParameters, self.sourceParameters)[0]
            self.plots.update({keyTx: plotTx})
        # Rx graph was once showed before
        if keyRx in self.plots:
            plotRx = self.plots.get(keyRx)
        else:
            plotRx = getPlot(keyRx, titleRx, self.simulationResults, self.generalParameters, self.sourceParameters)[0]
            self.plots.update({keyRx: plotRx})
        # Source graphs
        if type == "optical" or type == "spectrum":
            if keySc in self.plots:
                plotSc = self.plots.get(keySc)
            else:
                plotSc = getPlot(keySc, titleSc, self.simulationResults, self.generalParameters, self.sourceParameters)[0]
                self.plots.update({keySc: plotSc})
        else:
            plotSc = None

        return plotTx, plotRx, plotSc


    def closeGraphsWindows(self):
        """
        Closes all opened Toplevel windows.
        """
        for window in self.root.winfo_children():
            if isinstance(window, tk.Toplevel):
                window.destroy()


    def setButtonText(self, type: str) -> str:
        """
        Sets text of button represeting blocks of communication channel to its set parameters.

        Parameters
        -----
        type: button type (can be all fo all buttons)
        """
        if type == "source":
            rinText = self.correctRinOrder()
            text = f"Power: {self.sourceParameters.get('Power')} dBm\nFrequency: {self.sourceParameters.get('Frequency')} THz\nLinewidth: {self.sourceParameters.get('Linewidth')} Hz\nRIN: {rinText}"
            self.sourceButton.config(text=text)
        elif type =="modulator":
            text = f"{self.modulatorParameters.get('Type')}"
            self.modulatorButton.config(text=text)
        elif type == "channel":
            text = f"Length: {self.channelParameters.get('Length')} km\nAttenuation: {self.channelParameters.get('Attenuation')} dB/km\nChromatic dispersion: {self.channelParameters.get('Dispersion')} ps/nm/km"
            self.channelButton.config(text=text)
            self.comboChannelButton.config(text=text)
        elif type == "reciever":
            bandwidthText = self.correctBandwidthUnits()
            text = f"{self.recieverParameters.get('Type')}\nBandwidth: {bandwidthText}\nResolution: {self.recieverParameters.get('Resolution')} A/W"
            self.recieverButton.config(text=text)
        elif type == "amplifier":
            text = f"Position in channel: {self.amplifierParameters.get('Position')}\nGain: {self.amplifierParameters.get('Gain')} dB\nNoise figure: {self.amplifierParameters.get('Noise')} dB\n Detection limit: {self.amplifierParameters.get('Detection')} dBm"
            self.amplifierButton.config(text=text)
            self.comboAmplifierButton.config(text=text)
        elif type == "all":
            text = f"Power: {self.sourceParameters.get('Power')} dBm\nFrequency: {self.sourceParameters.get('Frequency')} THz\nLinewidth: {self.sourceParameters.get('Linewidth')} Hz\nRIN: {self.sourceParameters.get('RIN')}"
            self.sourceButton.config(text=text)

            text = f"{self.modulatorParameters.get('Type')}"
            self.modulatorButton.config(text=text)

            text = f"Length: {self.channelParameters.get('Length')} km\nAttenuation: {self.channelParameters.get('Attenuation')} dB/km\nChromatic dispersion: {self.channelParameters.get('Dispersion')} ps/nm/km"
            self.channelButton.config(text=text)

            text = f"{self.recieverParameters.get('Type')}\nBandwidth: {self.recieverParameters.get('Bandwidth')} Hz\nResolution: {self.recieverParameters.get('Resolution')} A/W"
            self.recieverButton.config(text=text)

            text = f"Position in channel: {self.amplifierParameters.get('Position')}\nGain: {self.amplifierParameters.get('Gain')} dB\nNoise figure: {self.amplifierParameters.get('Noise')} dB\n Detection limit: {self.amplifierParameters.get('Detection')} dBm"
            self.amplifierButton.config(text=text)
        else:
            raise Exception("Unexpected")
        

    def correctRinOrder(self) -> str:
        """
        Corrects RIN text to show a number * 10^x.

        Returns
        ----
        rin: str value
        """
        rin = self.sourceParameters.get("RIN")

        if rin == 0:
            return rin
        elif rin <= 10**-15:
            return f"{rin * 10**15} * 10^-15"
        elif rin <= 10**-12:
            return f"{rin * 10**12} * 10^-12"
        elif rin <= 10**-9:
            return f"{rin * 10**9} * 10^-9"
        elif rin <= 10**-6:
            return f"{rin * 10**6} * 10^-6"
        else:
            return f"{rin * 10**3} * 10^-3"
        

    def correctBandwidthUnits(self) -> str:
        """
        Corrects reciever text to show correct bandwidth unist.

        Returns
        ----
        bandwidth: str value
        """
        bandwidth = self.recieverParameters.get("Bandwidth")

        if bandwidth >= 10**9:
            return f"{bandwidth / 10**9} GHz"
        elif bandwidth >= 10**6:
            return f"{bandwidth / 10**6} MHz"
        elif bandwidth >= 10**3:
            return f"{bandwidth / 10**3} kHz"
        else:
            return f"{bandwidth} Hz"




    






    def attentionCheck(self):
        """
        Checks for attention for combination of ideal channel and amplifier. Also updates the attention label.
        """
        if self.channelParameters.get("Ideal") and self.amplifierCheckVar.get():
            self.attentionLabel.config(text="Attention, when using ideal channel the amplifier will be ignored!")
        else:
            self.attentionLabel.config(text="")