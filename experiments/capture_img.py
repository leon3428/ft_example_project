import cv2      # Uvezi biblioteku OpenCV

cam_port = 0    # Port na kojem se nalazi kamera 
video_capture = cv2.VideoCapture(cam_port)  # Otvori novi tok s kamere

# Dohvati sliku s kamere
# Result je istina, ako je operacija uspijela, a laž ako nije
# Varijabla image sadrži sliku koju smo dohvatili
result, image = video_capture.read() 

# Provjeri je li slika uspješno dovačena
if result: 
    # Ako je, spremi ju
    cv2.imwrite("first_image.png", image) 
else: 
    # Ako nije, ispiši poruku
    print("No image detected. Please! try again") 

# Zatvori sve prozore
cv2.destroyAllWindows()