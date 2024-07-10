import cv2      # Uvezi biblioteku OpenCV

cam_port = 0    # Port na kojem se nalazi kamera 
video_capture = cv2.VideoCapture(cam_port)  # Otvori novi tok s kamere

# Petlja koje se ponavlja beskonačno mnogo puta
while True:
    # Dohvati sliku s kamere
    # Result je istina, ako je operacija uspjela, a laž ako nije
    # Varijabla image sadrži sliku koju smo dohvatili
    result, image = video_capture.read() 

    # Provjeri je li slika uspješno dohvaćena
    if result: 
        # Ako je, prikaži ju
        cv2.imshow('Window', image)

        # Provjeri treba li završiti program
        if cv2.waitKey(1) == ord('q'):
            break
    else: 
        # Ako nije, završi
        break

# Zatvori sve prozore
cv2.destroyAllWindows()