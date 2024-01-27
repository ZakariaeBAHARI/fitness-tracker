import cv2
import mediapipe as mp
import tkinter as tk
from tkinter import filedialog
from threading import Thread
from PIL import Image, ImageTk



mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

def count_pull_ups(shoulder, elbow, wrist, in_pullup_position, pullup_count):
    
    if elbow < shoulder:
        in_pullup_position = True
    else:
        
        if in_pullup_position:
            pullup_count += 1
            print(f"Pull-Up Count: {pullup_count}")
            in_pullup_position = False

    return in_pullup_position, pullup_count

def process_frame(frame, in_pullup_position, pullup_count):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with the pose model
    result = pose.process(frame_rgb)

    # Extract landmarks from the result
    landmarks = result.pose_landmarks

    # Draw landmarks and pull-up count on the frame
    if landmarks:
        mp.solutions.drawing_utils.draw_landmarks(frame, landmarks, mp_pose.POSE_CONNECTIONS)

        left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y
        left_elbow = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW].y
        left_wrist = landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].y

        if None not in (left_shoulder, left_elbow, left_wrist):
            in_pullup_position, pullup_count = count_pull_ups(left_shoulder, left_elbow, left_wrist, in_pullup_position, pullup_count)

    # Display the pull-up count on the frame
    cv2.putText(frame, f"Pull-Up Count: {pullup_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    return in_pullup_position, pullup_count, frame

def process_video(input_path, output_path):
    # Open the video file
    cap = cv2.VideoCapture(input_path)

    # Get video properties
    width = int(cap.get(3))
    height = int(cap.get(4))
    fps = cap.get(5)

    # Define codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Initialize variables for pull-up counting
    in_pullup_position = False
    pullup_count = 0

    try:
        # Process each frame in the video
        while True:
            ret, frame = cap.read()
            if ret is False:
                break

            in_pullup_position, pullup_count, processed_frame = process_frame(frame, in_pullup_position, pullup_count)

            # Write the processed frame to the output video
            out.write(processed_frame)

            # Display the frame
            cv2.imshow('Video', processed_frame)

            # Break the loop when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # Release the video capture and writer objects
        cap.release()
        out.release()

        # Destroy all OpenCV windows
        cv2.destroyAllWindows()
    




class PullUpCounterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fitness Tracker")
        self.input_video_path = ''
        self.output_video_path = 'output_video.avi'

        bg_color = "#262626"  # Dark Grey
        fg_color = "#FFFFFF"  # White
        button_bg_color = "#FF4500"  # Orange-Red
        button_fg_color = "#FFFFFF"  # White


        self.root.configure(bg=bg_color)

        self.title_label = tk.Label(root, text="Fitness Exercises Tracker", font=("Helvetica", 24, "bold"), bg=bg_color, fg=fg_color)
        self.title_label.pack(pady=20)

        self.info_label = tk.Label(root, text="Video Information:", font=("Helvetica", 16), bg=bg_color, fg=fg_color)
        self.info_label.pack(pady=(0, 5))  

        self.canvas = tk.Canvas(root, width=800, height=600, bg=bg_color, highlightthickness=0)
        self.canvas.pack()

        self.buttons_frame = tk.Frame(root, bg=bg_color)
        self.buttons_frame.pack()

        button_style = {"padx": 15, "pady": 10, "bg": button_bg_color, "fg": button_fg_color, "font": ("Helvetica", 14)}

        self.start_button = tk.Button(self.buttons_frame, text="Track Exercise", command=self.start_processing, **button_style)
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.choose_file_button = tk.Button(self.buttons_frame, text="Select Video", command=self.choose_video_file, **button_style)
        self.choose_file_button.pack(side=tk.LEFT, padx=10)

        self.pullup_count_label = tk.Label(root, text="Pull-Up Count", font=("Helvetica", 16), bg=bg_color, fg=fg_color)
        self.pullup_count_label.pack(pady=10)

        self.buttons_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def start_processing(self):
        processing_thread = Thread(target=self.process_video)
        processing_thread.start()

    def choose_video_file(self):
        self.input_video_path = filedialog.askopenfilename(title="Select Video File", filetypes=[("Video files", "*.mp4;*.avi;*.mov")])
        if self.input_video_path:
            video_info = f"Video Information: {self.get_video_info(self.input_video_path)}"
            self.info_label.config(text=video_info)

    def process_video(self):
        if not self.input_video_path:
            print("Please choose a video file.")
            return

        pullup_count = process_video(self.input_video_path, self.output_video_path)

        self.pullup_count_label.config(text=f"Pull-Up Count: {pullup_count}")

    def update_canvas(self, image):
        self.photo = ImageTk.PhotoImage(image=Image.fromarray(image))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

    @staticmethod
    def get_video_info(video_path):
        cap = cv2.VideoCapture(video_path)
        width = int(cap.get(3))
        height = int(cap.get(4))
        fps = cap.get(5)
        return f"Resolution: {width}x{height}, Frame Rate: {fps:.2f} fps"

if __name__ == "__main__":
    root = tk.Tk()
    app = PullUpCounterApp(root)
    root.mainloop()
