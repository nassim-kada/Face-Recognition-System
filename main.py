# import cv2
# IMG_PATH="/home/nsm-kil3r/Desktop/wall/1.jpg"
# image=cv2.imread(IMG_PATH)

# cv2.imshow('CLOWN',image)
# cv2.waitKey(0)

# import cv2
# video =cv2.VideoCapture(0) # 0 for local webcam 1 external webcam 2 external webcam 2
# while True:
#     grabbed,frame =video.read()
#     frame=cv2.resize(frame, (800, 500))
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#     cv2.imshow('video',frame)
# video.release()
# cv2.destroyAllWindows()

# import numpy as np
# import cv2 
# image= cv2.imread("/home/nsm-kil3r/Desktop/wall/1.jpg")
# cv2.imshow('AI',image)
# cv2.waitKey(0)

import pickle
import cv2
import face_recognition
import numpy as np
cap=cv2.VideoCapture(0)
#import the encoded images
file = open('EncodedImages.p','rb')
encodeListKnownWithIds=pickle.load(file)
file.close()
encodeListKnown,modelsIds = encodeListKnownWithIds

#camera open
while True:
    grabbed,frame = cap.read()
    frameS=cv2.resize(frame,(0,0),None,0.25,0.25)
    frameS = cv2.cvtColor(frameS,cv2.COLOR_BGR2RGB)
    faceCurntFrame= face_recognition.face_locations(frameS)
    encodeCurntFrame=face_recognition.face_encodings(frameS,faceCurntFrame)
    
    for encodeFace,faceLoc in zip(encodeCurntFrame,faceCurntFrame):
        match = face_recognition.compare_faces(encodeListKnown,encodeFace)
        faceDistance =face_recognition.face_distance(encodeListKnown,encodeFace)
        # print("matches",match)
        # print("faceDistance",faceDistance)
        matchIndex =np.argmin(faceDistance)
        # print("match index is:",matchIndex)
        if match[matchIndex]:
            print("known face detectedand it's id is:"+modelsIds[matchIndex])
            top,right,bottom,left=faceLoc
            top, right, bottom, left = top*4,right*4,bottom*4,left*4
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 1)
        else:
            print("the face is not in the database")
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    cv2.imshow("face",frame)
cap.release()
cv2.destroyAllWindows()