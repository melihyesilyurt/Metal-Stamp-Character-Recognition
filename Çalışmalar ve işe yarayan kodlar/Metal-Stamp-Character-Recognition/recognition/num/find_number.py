# TrainAndTest.py
import cv2
import numpy as np
import operator
import os

class my_recognizer():
    def find(image_to_rec):
        #fin fonksiyonu tanımlanmış fotoğraf buna gönderiliyor 
        #         # module level variables ##########################################################################
        MIN_CONTOUR_AREA = 100
        #minimum kontur bölgesi değişkeni 100 tanımlanmış
        RESIZED_IMAGE_WIDTH = 20
        #yeniden bouytlandırılmış resmin genişliği 20 verilmiş
        RESIZED_IMAGE_HEIGHT = 30
        #yeniden bouytlandırılmış resmin yüksekliği 30 verilmiş
        ###################################################################################################
        class ContourWithData():
            #datalı kontur adında bir class tanımlanmış
            # member variables ############################################################################
            npaContour = None           # contour
            boundingRect = None         # bounding rect for contour
            intRectX = 0                # bounding rect top left corner x location
            intRectY = 0                # bounding rect top left corner y location
            intRectWidth = 0            # bounding rect width
            intRectHeight = 0           # bounding rect height
            fltArea = 0.0               # area of contour
            #Bazı değişkenler tanımlanmış
            def calculateRectTopLeftPointAndWidthAndHeight(self):              # calculate bounding rect info
                #hesaplaDoğruÜstSolNokta ve Genişlik ve Yükseklik adında fonfsiyon tanımlanmış
                [intX, intY, intWidth, intHeight] = self.boundingRect
                #boundingRect opencvdekinden farklı yukarıda tanımlamış self objesinin çerçeve noktalarını hesaplayıp yukarıda değerlere atama yapıyor
                self.intRectX = intX
                self.intRectY = intY
                self.intRectWidth = intWidth
                self.intRectHeight = intHeight
                #sonra bu değerleri self objesinin içindeki benzer değerlere aktarıyor

            def checkIfContourIsValid(self):                            # this is oversimplified, for a production grade program
                #konturun geçerli olup olmadaığını kontrol etmek için fonksiyon yapmış
                if self.fltArea < MIN_CONTOUR_AREA: return False        # much better validity checking would be necessary
                #MIN_CONTOUR_AREA 100 olarak tanımlanmıştı eğerself objesinin fltareası küçükse o obje geçerli değildir.
                return True

        ###################################################################################################
        def work(digit_img):
            allContoursWithData = []                # declare empty lists,
            validContoursWithData = []              # we will fill these shortly
            #boş listeler tanımlamış
            try:
                npaClassifications = np.loadtxt("recognition/num/classifications_for_questions.txt", np.float32)                  # read in training classifications
                #load() fonksiyonu ise kaydedilmiş .npy nesne dosyasının içeriğine erişmek için kullanılmaktadır.
                #eğitilmiş sınıflandırmaları okur
            except:
                print ("error, unable to open classifications_for_questions.txt, exiting program\n")
                #konsola yazı yazdırıyor
                os.system("pause")
                #sistemi durduyor
                return
            # end try

            try:
                npaFlattenedImages = np.loadtxt("recognition/num/flattened_images_for_questions.txt", np.float32)                 # read in training images
                #load() fonksiyonu ise kaydedilmiş .npy nesne dosyasının içeriğine erişmek için kullanılmaktadır.
                #eğitilmiş fotoğrafları okur
            except:
                print ("error, unable to open flattened_images_for_questions.txt, exiting program\n")
                os.system("pause") #ben ekledim
                return
            # end try

            npaClassifications = npaClassifications.reshape((npaClassifications.size, 1))       # reshape numpy array to 1d, necessary to pass to call to train
            #dizinin şeklini değiştiriyor npaClassifications boyutuna 1 yapıyor yani satır sayısı npaClassifications kadar sütün sayısı 1 olan matris oluyor
            kNearest = cv2.ml.KNearest_create()                   # instantiate KNN object
            #En yakın komşu algoritması kullanıyor. KNN oluşturuyor
            #https://docs.opencv.org/3.4/dc/dd6/ml_intro.html
            #https://docs.opencv.org/3.4/dd/de1/classcv_1_1ml_1_1KNearest.html
            kNearest.train(npaFlattenedImages, cv2.ml.ROW_SAMPLE, npaClassifications)
            #Eğitim için ilk olarak eğitim örnekleri 2. olarak layout burada row sample kullanmış(her eğitim örneği bir dizi örnektir) 3. eğitim örnekleriyle ilişkili yanıtların vektörü.
            #https://docs.opencv.org/3.4/db/d7d/classcv_1_1ml_1_1StatModel.html#af96a0e04f1677a835cc25263c7db3c0c
            #_number_ = "fn"
            #_path_ = str("temp_photos/" + _number_ +".png")
            #imgTestingNumbers = cv2.imread(_path_)          # read in testing numbers image
            imgTestingNumbers = digit_img
            #digit_img verilerini imgTestingNumbers içine atmış (yani resmi)
            if imgTestingNumbers is None:                           # if image was not read successfully
                print ("error: image not read from file \n\n")        # print error message to std out
                os.system("pause")                                  # pause so user can see error message
                return                                              # and exit function (which exits program)
            # end if

            imgGray = cv2.cvtColor(imgTestingNumbers, cv2.COLOR_BGR2GRAY)       # get grayscale image
            #Renk paletini gri tonlu hale getiriyor
            imgBlurred = cv2.GaussianBlur(imgGray, (5,5), 0)                    # blur
            #Gauss bulanıklaştırması uygulanıyor kullanım şekli aşağıdaki linkte var 
	        #https://www.tutorialkart.com/opencv/python/opencv-python-gaussian-image-smoothing/
                                                                # filter image from grayscale to black and white
            imgThresh = cv2.adaptiveThreshold(imgBlurred,                           # input image
                                              255,                                  # make pixels that pass the threshold full white
                                              cv2.ADAPTIVE_THRESH_GAUSSIAN_C,       # use gaussian rather than mean, seems to give better results
                                              cv2.THRESH_BINARY_INV,                # invert so foreground will be white, background will be black
                                              11,                                   # size of a pixel neighborhood used to calculate threshold value
                                              2)                                    # constant subtracted from the mean or weighted mean

            imgThreshCopy = imgThresh.copy()        # make a copy of the thresh image, this in necessary b/c findContours modifies the image

            npaContours, npaHierarchy = cv2.findContours(imgThresh.copy(),             # input image, make sure to use a copy since the function will modify this image in the course of finding contours
                                                         cv2.RETR_EXTERNAL,         # retrieve the outermost contours only
                                                         cv2.CHAIN_APPROX_SIMPLE)   # compress horizontal, vertical, and diagonal segments and leave only their end points

            for npaContour in npaContours:                             # for each contour
                contourWithData = ContourWithData()                                             # instantiate a contour with data object
                contourWithData.npaContour = npaContour                                         # assign contour to contour with data
                contourWithData.boundingRect = cv2.boundingRect(contourWithData.npaContour)     # get the bounding rect
                contourWithData.calculateRectTopLeftPointAndWidthAndHeight()                    # get bounding rect info
                contourWithData.fltArea = cv2.contourArea(contourWithData.npaContour)           # calculate the contour area
                allContoursWithData.append(contourWithData)                                     # add contour with data object to list of all contours with data
            # end for

            for contourWithData in allContoursWithData:                 # for all contours
                if contourWithData.checkIfContourIsValid():             # check if valid
                    validContoursWithData.append(contourWithData)       # if so, append to valid contour list
                # end if
            # end for

            validContoursWithData.sort(key = operator.attrgetter("intRectX"))         # sort contours from left to right

            strFinalString_num1 = ""         # declare final string, this will have the final number sequence by the end of the program

            for contourWithData in validContoursWithData:            # for each contour
                                                        # draw a green rect around the current char
                cv2.rectangle(imgTestingNumbers,                                        # draw rectangle on original testing image
                              (contourWithData.intRectX, contourWithData.intRectY),     # upper left corner
                              (contourWithData.intRectX + contourWithData.intRectWidth, contourWithData.intRectY + contourWithData.intRectHeight),      # lower right corner
                              (0, 255, 0),              # green
                              2)                        # thickness

                imgROI = imgThresh[contourWithData.intRectY : contourWithData.intRectY + contourWithData.intRectHeight,     # crop char out of threshold image
                                   contourWithData.intRectX : contourWithData.intRectX + contourWithData.intRectWidth]

                imgROIResized = cv2.resize(imgROI, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))             # resize image, this will be more consistent for recognition and storage

                npaROIResized = imgROIResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))      # flatten image into 1d numpy array

                npaROIResized = np.float32(npaROIResized)       # convert from 1d numpy array of ints to 1d numpy array of floats

                retval, npaResults, neigh_resp, dists = kNearest.findNearest(npaROIResized, k = 1)     # call KNN function find_nearest

                strCurrentChar_num1 = str(chr(int(npaResults[0][0])))                                             # get character from results

                strFinalString_num1 = strFinalString_num1 + strCurrentChar_num1            # append current char to full string
            # end for

            #print ("\n" + strFinalString + "\n")                  # show the full string
            #run_status = 0
            #print("Run Status: " + str(run_status)+" Times")
            num = strFinalString_num1
            #print("the first recognized integer number is")
            #print(num1)
            #print(str(num))

            return num

        #====================================================================================================
        try:
            #print(str(image_to_rec))
            #digit = cv2.imread('temp_photos/'+str(image_to_rec))
            digit = image_to_rec
            num1 = work(digit)
            #print(str(num1))
            return num1
        except Exception as e:
        	print('Error occured')
        	print(e)


#====================================================================================================
#os.system('pause')
'''
###################################################################################################
if __name__ == "__main__":
    main()
# end if
'''
