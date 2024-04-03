import cv2
 
circles = []
counter = 0
counter2 = 0
Clickpoint1 = []
Clickpoint2 = []
myCoordinates = []
 
# Function to store left-mouse click coordinates
def mouseClickPoints(event, x, y, flags, params):
    global counter, Clickpoint1, Clickpoint2, counter2, circles
    if event == cv2.EVENT_LBUTTONDOWN:
        # Draw circle in red color
        cv2.circle(img, (x, y), 3, (0,0,255), cv2.FILLED)
        if counter == 0:
            Clickpoint1 = int(x), int(y)
            counter += 1
        elif counter == 1:
            Clickpoint2 = int(x), int(y)
            myCoordinates.append([Clickpoint1, Clickpoint2])
            counter = 0
            circles.append([x, y])
            counter2 += 1
 
img = cv2.imread('')
 
# Resize image
height, width, channel = img.shape
img = cv2.resize(img, (width//2, height//2))
 
while True:
    # To Display clicked points
    for x, y in circles:
        cv2.circle(img, (x, y), 3, (0,0,255), cv2.FILLED)
    # Display original image
    cv2.imshow('Original Image', img)
    # Collect coordinates of mouse click points
    cv2.setMouseCallback('Original Image', mouseClickPoints)
    # Press 'esc' in keyboard to stop the program and print the coordinate values
    if cv2.waitKey(1) & 0xFF == 27:
        print(myCoordinates)
        break
