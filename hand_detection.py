from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast,POINTER
import screen_brightness_control as sbc
import cv2
import mediapipe as mp
import math
import pyautogui
import time
cap=cv2.VideoCapture(0)
mp_hands= mp.solutions.hands
hands=mp_hands.Hands()
mp_draw=mp.solutions.drawing_utils   
screen_w,screen_h=pyautogui.size() #to get screen width and height(Webcam coordinates ≠ Screen coordinates)
prev_x=0
prev_y=0
last_click=0 #stores time of last click
prev_scroll_y=0
devices=AudioUtilities.GetSpeakers()
volume=devices.EndpointVolume
vol_min,vol_max=volume.GetVolumeRange()[:2]

while 1:
    
    success,frame=cap.read()
    if not success:
        break
    frame=cv2.flip(frame,1)
    frame_rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    results=hands.process(frame_rgb)
    
    if results.multi_hand_landmarks:
        for hand in results.multi_hand_landmarks:
            fingers=0
            h,w,c=frame.shape
            
            x=int(hand.landmark[8].x*w) #x coordinate is multiplied with WIDTH
            y=int(hand.landmark[8].y*h) #y coordinate is multiplied with HEIGHT
            x1 = int(hand.landmark[4].x * w)#FOR THUMB  
            y1 = int(hand.landmark[4].y * h)
            x2 = int(hand.landmark[12].x*w)
            y2 = int(hand.landmark[12].y*h)
            #counting fingers
            if hand.landmark[8].y < hand.landmark[6].y: #counting index finger 8=fingertip, 6=lower joint
                fingers+=1
            if hand.landmark[12].y<hand.landmark[10].y: #middle finger
                fingers+=1
            if hand.landmark[16].y <hand.landmark[14].y: #ring finger
                fingers+=1
            if hand.landmark[20].y< hand.landmark[18].y: #little finger
                fingers+=1
            cv2.putText(
                frame,
                f"fingers: {fingers}",
                (50,100),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255,0,0),
                3
            )
            #scroll up/down:
            if fingers==2:
                if y<prev_scroll_y-20:  #+-20 act as a buffer for random hand movements
                    pyautogui.scroll(100)
                elif y>prev_scroll_y+20:
                    pyautogui.scroll(-100)

                prev_scroll_y=y

            if fingers==3:
                volume_distance=math.hypot(
                    x-x1,
                    y-y1
                )
                volume_percent=min(
                    100,
                    max(
                        0,
                        int(volume_distance/3)

                    )
                )
                volume_level=vol_min+(
                    volume_percent/100
                )*(vol_max-vol_min)
                volume.SetMasterVolumeLevel(
                    volume_level,
                    None
                )
                cv2.putText(
                    frame,
                    f"Volume:{volume_percent}%",
                    (50,150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,(0,255,255),
                    3
                )


            
           
            cv2.circle(frame,(x,y),10,(0,255,0),cv2.FILLED)
            cv2.circle(frame,(x1,y1),10,(255,0,0),cv2.FILLED)
            cv2.line(frame,(x1,y1),(x,y),(255,255,0),3) #for drawing a line b/w thumb and index finger eventually calculating distance b/w them
            distance=math.hypot(x-x1,y-y1)
            right_distance=math.hypot(x1-x2,y1-y2)
            current_time=time.time()
            mouse_x=screen_w/w*x #Convert Finger Coordinates to Screen Coordinates
            mouse_y=screen_h/h*y
            curr_x=prev_x+(mouse_x-prev_x)/5 #making mouse movement smooth
            curr_y=prev_y+(mouse_y-prev_y)/5 #Move only 1/k th of the distance(for smoothness)
            pyautogui.moveTo(curr_x,curr_y)
            prev_x=curr_x
            prev_y=curr_y
            if right_distance<50 and current_time-last_click>0.5:
                cv2.putText(
                    frame,
                    "Right Click",
                    (200,100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0,255,0),
                    3                 
                    
                )
                pyautogui.rightClick()
                last_click=current_time
            elif distance<50 and current_time-last_click>0.5: #elif prevents left click and right click simultaneously
                cv2.putText(
                    frame,
                    "CLICK",
                    (200,100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0,255,0),
                    3
                )

                pyautogui.click()
                last_click=current_time
            
            cv2.putText(
                frame,
                f"({x},{y})",
                (x+10,y-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255,0,0),
                2
            )
            cv2.putText(
                frame,
                str(int(distance)),
                (50,50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,0,255),
                2
            )
         
            mp_draw.draw_landmarks(
                frame,
                hand,
                mp_hands.HAND_CONNECTIONS
            )
                

    cv2.imshow("Webcam",frame)
    if cv2.waitKey(1)==27:
        break
cap.release()
cv2.destroyAllWindows()