import cv2
import threading
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk 

class BodyCalibrationInstructions:
    def __init__(self, root):
        self.root = root
        self.root.title("Body Calibration Instructions")

        mainframe = ttk.Frame(root, padding=20)
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        mainframe.columnconfigure(0, weight=1)
        for i in range(6):  # all rows that have widgets
            mainframe.rowconfigure(i, weight=1)

        # Title
        ttk.Label(
            mainframe,
            text="Prepare Your Body Calibration",
            font=("Helvetica", 18, "bold"),
            anchor="center",
            justify="center"
        ).grid(column=0, row=0, pady=(0, 20), sticky="ew")

        #Ergo scan label

        ergoscan_label = ttk.Label(
            mainframe,
            text="ErgoScan",
            font=("Helvetica", 25, "bold"),
            justify="center",
            anchor="center"
        )
        ergoscan_label.grid(column=0, row=0, columnspan=2, pady=(0, 20), sticky="ew")

        #Bold and Center the title
        title_label = ttk.Label(
            mainframe,
            text="Prepare Your Body Calibration",
            font=("Helvetica", 14, "bold"),
            anchor="center",
            justify="center"
        )
        title_label.grid(column=0, row=1, columnspan=2, pady=(0, 20), sticky="ew")

        self.subtitle_label = ttk.Label(
            mainframe,
            text="Body calibration helps ErgoScan understand your unique posture and body proportions. This ensures more accurate movement tracking and feedback during scans.",
            font=("Helvetica", 14),
            anchor="center",
            justify="center",
            wraplength=400

        )
        self.subtitle_label.grid(column = 0, row = 2, columnspan=2, pady=(0,20), sticky="ew")

        # Instructions text
        self.instructions = ttk.Label(
            mainframe,
            text=(
                "1. Make sure you are in a well-lit area with enough space to move freely.\n\n" \
                "2. Adjust your camera to ensure your entire body, from head to toe, is visible in the frame.\n\n" \
                "3. Get ready to hold still poses as prompted during the calibration process. A countdown will guide you.\n\n" \
            ),
            font=("Helvetica", 12),
            anchor="center",
            justify="center",
            wraplength=400
        )
        self.instructions.grid(column=0, row=3, columnspan=2, pady=(0,10))

        # Button Instructions
        ttk.Label(
            mainframe,
            text="Click 'Start Calibration' to open the camera feed below.",
            justify="center",
            anchor="center",
            wraplength=400
        ).grid(column=0, row=4, pady=(0, 10), sticky="ew")

        # Start and Stop buttons
        button_frame = ttk.Frame(mainframe)
        button_frame.grid(column=0, row=5, pady=20)


        self.start_button = ttk.Button(
            button_frame, text="Start Calibration", command=self.start_camera
        )
        self.start_button.grid(column=0, row=0, padx=10)

        self.stop_button = ttk.Button(
            button_frame, text="Stop", command=self.stop_camera, state=DISABLED
        )
        self.stop_button.grid(column=1, row=0, padx=10)

        # Camera display area
        self.video_label = Label(mainframe)
        self.video_label.grid(column=0, row=6, pady=20)

        # Camera setup
        self.cap = None
        self.running = False

    # Start camera feed
    def start_camera(self):

        #hide instructions after start calibration
        self.instructions.grid_forget()
        self.subtitle_label.grid_forget()


        if not self.running:
            self.cap = cv2.VideoCapture(0)
            self.running = True
            self.start_button.config(state=DISABLED)
            self.stop_button.config(state=NORMAL)
            threading.Thread(target=self.update_frame, daemon=True).start()

    # Stop camera feed
    def stop_camera(self):
        self.running = False
        self.start_button.config(state=NORMAL)
        self.stop_button.config(state=DISABLED)
        if self.cap:
            self.cap.release()

    # Continuously update the camera frame in Tkinter
    def update_frame(self):
        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            # Flip horizontally for a mirror effect 
            frame = cv2.flip(frame, 1)

            # Get frame dimensions
            height, width, _ = frame.shape

            # Define rectangle dimensions
            rect_width = 300
            rect_height = 440
            x1 = (width - rect_width) // 2
            y1 = 100
            x2 = x1 + rect_width
            y2 = y1 + rect_height


            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Draw a simple UI overlay (OpenCV style)
            cv2.putText(frame, "Align your body in the frame",
                        (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (0, 255, 0), 2, cv2.LINE_AA)
            # cv2.rectangle(frame, (50, 100), (400, 540), (0, 255, 0), 2)

            # Convert frame to Tkinter-compatible image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)

            # Update the label image
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        # Clean up if stopped
        if self.cap:
            self.cap.release()

# Run the app
root = Tk()
BodyCalibrationInstructions(root)
root.mainloop()
