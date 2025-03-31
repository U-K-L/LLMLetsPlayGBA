import time
import socket
import cv2
import os
import base64
from openai import OpenAI
import json

client = OpenAI()

HOST = "127.0.0.1"
PORT = 5000  # Choose an open port
screenshot_path = "GBA/screenshot.png"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
print(f"Listening on {HOST}:{PORT}")
conn, addr = server.accept()
print(f"Connected by {conn}")

def encode_image(image_file):
    return base64.b64encode(image_file).decode("utf-8")
    
def recieveData():
    data = conn.recv(1024).decode()
    #print("Received:", data)
    response = f"Python got: {data}"
    return response

def sendButton(response):
    #turn response to string
    print("Sending:", response)
    response = str(response)
    conn.send(response.encode())

def drawGrid(image):
    height, width, _ = image.shape
    # Define grid size
    rows, cols = 8, 8
    cell_width = width // cols
    cell_height = height // rows

    # Draw grid
    for i in range(rows + 1):
        y = i * cell_height
        cv2.line(image, (0, y), (width, y), (0, 255, 0), 1)

    for j in range(cols + 1):
        x = j * cell_width
        cv2.line(image, (x, 0), (x, height), (0, 255, 0), 1)

    # Label cells with (row, col) format
    font = cv2.FONT_HERSHEY_SIMPLEX
    for i in range(rows):
        for j in range(cols):
            x = j * cell_width + 5
            y = i * cell_height + 20
            #cv2.putText(image, f"({i},{j})", (x, y), font, 0.21, (0, 0, 255), 1)


def getImage():
    img = None
    if os.path.exists(screenshot_path):
        img = cv2.imread(screenshot_path)
    return img

def updateImages(img):
    scale_x = 4
    scale_y = 4
    resized_img = cv2.resize(img, None, fx=scale_x, fy=scale_y, interpolation=cv2.INTER_LINEAR)
    cv2.imshow("mGBA Screenshot", resized_img)
        
def call_gpt_vision(image):

    prompt = "What is in this image?"

    system_message = (
        "You are playing a video game"
        "Your goal is to get to the end of the stage. Which is typically towards the right. You need to go right and jump over obstacles. and enemies"
        "ALWAYS CHOOSE A BUTTON. You can have a controller, You can press multiple buttons. Your options are: 0=LEFT, 1=RIGHT, 2=DOWN, 3=UP, 4=JUMP, 5=ATTACK"
        "Enemies make you take damage, that's basically all living creatures on screen."
        "Obstacles you need to jump over, you can fly."
        "Give a detail description of what's on the screen and where it's positioned. The screen is 8x8 grid. Say what is in each grid position. No new line characters, just a string."
        "Your goal is to reach black door with stars on it. Press UP to enter the door. AND WIN THE GAME"
    )

    function_schema = {
        "name": "make_decision",
        "description": "Select the next action and provide reasoning.",
        "parameters": {
            "type": "object",
            "properties": {
                "buttonPressed": {
                    "type": "array",
                    "items": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 5
                    },
                    "description": "Buttons in the game. Choose multiple if needed. Each element is an integer: 0=LEFT, 1=RIGHT, 2=DOWN, 3=UP, 4=A, 5=B"
                },
                "action": {"type": "string", "description": "The name of the action to take: move <direction>, attack, jump"},
                "confidence": {"type": "string", "description": "How confident are you of this decision, float from 0-1."},
                "screemDscription": {"type": "string", "description": "Detailed explanation of what's on the screen and where its positioned"},
            },
            "required": ["buttonPressed", "action", "confidence", "screemDscription"],
        },
    }

    full_prompt = f"{system_message}\n\nUser: {prompt}"

    response = client.chat.completions.create(
        model="o1",
        messages=[
            {
                "role": "user",
                "content": full_prompt
            }
        ],
        #response_format={"type": "json_object"},
        functions=[function_schema],
        function_call={"name": "make_decision"},
        #temperature=0.5,  # Controls randomness (lower = more deterministic)
        #max_tokens=12000,  # Maximum tokens in the response
        #top_p=0.9,  # Nucleus sampling parameter
        #frequency_penalty=0.1,  # Penalizes repeated tokens
        #presence_penalty=0.2,  # Encourages introducing new topics
    )

    function_response = response.choices[0].message.function_call.arguments
    print(response.choices[0].message.function_call.arguments)
    data_json = json.loads(function_response)
    print(data_json["action"])
    return data_json

def runServer():
    while True:
        #print("Waiting for connection...")
        #response = recieveData()

        img = getImage()
        if img is None:
            continue

        drawGrid(img)
        updateImages(img)

        success, buffer = cv2.imencode('.jpg', img)
        if not success:
            raise Exception("Image encoding failed!")

        base64_image = encode_image(buffer)

        full_response = call_gpt_vision(base64_image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        response = full_response['buttonPressed']

        #loop through each button pressed
        for button in response:
            sendButton(button)
            time.sleep(0.1)


runServer()
cv2.destroyAllWindows()
conn.close()
