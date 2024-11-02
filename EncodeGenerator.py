# EncodeGenerator.py
import os
import cv2
import face_recognition
import pickle

def generate_encoded_images():
    folderModpath = 'img/Modes'
    pathList = os.listdir(folderModpath)
    imgList = []
    modelsIds = []

    for path in pathList:
        imgList.append(cv2.imread(os.path.join(folderModpath, path)))
        modelsIds.append(os.path.splitext(path)[0])

    def findEncodings(imagesList):
        encodeList = []
        for img in imagesList:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList

    print("Encoding started")
    encodeListKnown = findEncodings(imgList)
    encodeListKnownWithIds = [encodeListKnown, modelsIds]
    print("Encoding finished")
    
    file = open("EncodedImages.p", 'wb')
    pickle.dump(encodeListKnownWithIds, file)
    file.close()

if __name__ == "__main__":
    generate_encoded_images()
