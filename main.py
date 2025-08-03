import cv2
import mediapipe as mp
import math
import time

# Initialize Mediapipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1)

class Button:
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text

    def draw(self, img):
        x, y = self.pos
        w, h = self.size
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 255, 255), cv2.FILLED)
        cv2.rectangle(img, (x, y), (x+w, y+h), (50, 50, 50), 3)
        cv2.putText(img, self.text, (x+20, y+60),
                    cv2.FONT_HERSHEY_PLAIN, 2.5, (0, 0, 0), 3)

    def check_inside(self, x, y):
        bx, by = self.pos
        bw, bh = self.size
        return bx < x < bx + bw and by < y < by + bh

# Create buttons
button_list = [
    ['7', '8', '9', '/'],
    ['4', '5', '6', '*'],
    ['1', '2', '3', '-'],
    ['0', '.', '%', '+'],
    ['C', 'sqrt', '=', '']
]

buttons = []
for i in range(len(button_list)):
    for j in range(len(button_list[i])):
        if button_list[i][j] != '':
            buttons.append(Button([100*j + 50, 100*i + 150], button_list[i][j]))

expression = ''
result = ''

# Hover detection state
hover_start_time = 0
current_hover_button = None
hover_duration_required = 1.8  # seconds

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    for button in buttons:
        button.draw(img)

    # Hand detection
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            lmList = []
            for id, lm in enumerate(handLms.landmark):
                h, w, _ = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append((cx, cy))
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

            if lmList:
                x, y = lmList[8]  # Index fingertip
                cv2.circle(img, (x, y), 10, (0, 255, 0), cv2.FILLED)

                hovered_button = None
                for button in buttons:
                    if button.check_inside(x, y):
                        hovered_button = button
                        break

                if hovered_button:
                    if current_hover_button != hovered_button:
                        current_hover_button = hovered_button
                        hover_start_time = time.time()
                    else:
                        if time.time() - hover_start_time >= hover_duration_required:
                            value = hovered_button.text
                            if value == 'C':
                                expression = ''
                                result = ''
                            elif value == '=':
                                try:
                                    result = str(eval(expression))
                                except:
                                    result = 'Error'
                            elif value == 'sqrt':
                                try:
                                    result = str(math.sqrt(float(expression)))
                                except:
                                    result = 'Error'
                            else:
                                expression += value
                            hover_start_time = time.time() + 2  # Prevent double detection
                            current_hover_button = None
                else:
                    current_hover_button = None
                    hover_start_time = 0

    else:
        current_hover_button = None
        hover_start_time = 0

    # Display expression
    cv2.rectangle(img, (50, 50), (550, 130), (255, 255, 255), cv2.FILLED)
    cv2.rectangle(img, (50, 50), (550, 130), (50, 50, 50), 3)
    cv2.putText(img, expression, (60, 90), cv2.FONT_HERSHEY_PLAIN,
                3, (0, 0, 0), 3)
    cv2.putText(img, result, (60, 125), cv2.FONT_HERSHEY_PLAIN,
                2.5, (100, 0, 100), 2)

    cv2.imshow("Gesture Calculator", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
