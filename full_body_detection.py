# import libraries
import mediapipe as mp
import cv2
from tkinter import *
from tkinter import ttk
import threading


# Init MediaPipe and OpenCV

#Init Mediapipe that combines pose, face, and hand landmarks into one Holistic model
mp_drawing = mp.solutions.drawing_utils # A util for drawing landmarks and connections
mp_holistic = mp.solutions.holistic # This var is used to visualize the landmarks and connections in the Mediapipe holistic model

def start_scan():
    #Start video capture from the webcam (0 is default camera, 1 is external camera)
    cap = cv2.VideoCapture(0) #if camera doesn't open, try changing to 0 or 1

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()

    #Init the mediapipe holistic model with minimum confidence thresholds
    with mp_holistic.Holistic(min_detection_confidence =0.5, min_tracking_confidence=0.5) as holistic:
        #As long as the webcam is open, read frames from it
        while cap.isOpened():
            ret, frame = cap.read() #Read current frame from webcam

            #Convert BGR (OpenCV format) to RGB (Mediapipe format)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            #Process the frame using mediapipe holistic model to detect landmarks
            results = holistic.process(image)
            #result = includes landmarks for face, pose, left and right hands

            #Convert the RGB back to BGR for rendering
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


            #Visualize the detected landmarks on the frame
            #This renders the detected landmarks and connections on the live video feed for easy visualization.
            
            # Draw face landmarks
            mp_drawing.draw_landmarks(
                image,
                results.face_landmarks,
                mp_holistic.FACEMESH_CONTOURS,
                mp_drawing.DrawingSpec(color=(80, 110, 10), thickness=1, circle_radius=1),
                mp_drawing.DrawingSpec(color=(80, 256, 121), thickness=1, circle_radius=1)
            )

            # Draw right hand landmarks
            mp_drawing.draw_landmarks(
                image,
                results.right_hand_landmarks,
                mp_holistic.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(80, 22, 10), thickness=2, circle_radius=4),
                mp_drawing.DrawingSpec(color=(80, 44, 121), thickness=2, circle_radius=2)
            )

            # Draw left hand landmarks
            mp_drawing.draw_landmarks(
                image,
                results.left_hand_landmarks,
                mp_holistic.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                mp_drawing.DrawingSpec(color=(121, 44, 250), thickness=2, circle_radius=2)
            )

            # Draw pose landmarks
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_holistic.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=4),
                mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
            )

            #Display the processed frame in a window
            cv2.imshow('Full Body Detection', image)
            #Press 'q' to exit the loop and close the application
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break


    #Release resources: 

    #Release webcam
    cap.release()
    #Close all OpenCV windows
    cv2.destroyAllWindows()




#Tkinter GUI setup - create user interface
root = Tk()
root.title("ErgoScan")

# #creating the parent frame to hold all the children widgets in the UI
mainframe = ttk.Frame(root, padding= (10, 10, 10, 10))

mainframe.grid(column= 0, row=0, sticky=(N, W, E, S))

start_scan_action = ttk.Button(mainframe, text = "Start Scan", default="active", command=lambda: threading.Thread(target=start_scan).start()).grid(column=1, row=1, sticky=W)

# Quit Button
quit_button = ttk.Button(mainframe, text="Quit", command=root.destroy)
quit_button.grid(column=1, row=2, pady=10)

# Run the GUI event loop
root.mainloop()