import mss
import mss.tools
import time
import cv2
import numpy

from win32 import win32gui
import numpy


def windowEnumerationHandler(hwnd, top_windows):
    top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))


try:
    imageCounter = 0;
    while (True):
        # gtawin = win32gui.FindWindow(None,"War")
        print("Change to Foxhole")
        name = [];

        ## Check if correct program is started
        # while(name != 'Spyder (Python 3.7)'):
        #    time.sleep(0.1);
        #    name=win32gui.GetWindowText(win32gui.GetForegroundWindow());
        #    print(name)

        gtawin = win32gui.GetForegroundWindow()

        if not gtawin:
            raise Exception('Foxhole not running')
        # get the bounding box of the window
        left, top, x2, y2 = win32gui.GetWindowRect(gtawin)
        widthScreen = x2 - left + 1
        heightScreen = y2 - top + 1
        win32gui.ShowWindow(gtawin, 1);
        # win32gui.BringWindowToTop(gtawin);
        # win32gui.SetForegroundWindow(gtawin);
        windowName = 'Evaluation´of Cards';
        cv2.namedWindow(windowName, cv2.WINDOW_AUTOSIZE);
        cv2.moveWindow(windowName, 0, 0);

        with mss.mss() as sct:
            # The screen part to capture
            imageCounter = imageCounter + 1;
            monitor = {"top": top, "left": left, "width": widthScreen, "height": heightScreen}
            currentTime = int("{0:.0f}".format(time.time() * 1000));
            output = 'D:/images/' + "screenshot" + str(currentTime) + ".png".format(**monitor)

            # Grab the data
            sct_img = sct.grab(monitor)

            # Get raw pixels from the screen, save it to a Numpy array
            imgScreen = numpy.array(sct.grab(monitor))
            imgScreenGray = cv2.cvtColor(imgScreen, cv2.COLOR_BGR2GRAY)
            wScreen, hScreen = imgScreenGray.shape[::-1]
            templateCornerGray = cv2.imread('cardCorner.png', 0)
            wCorner, hCorner = templateCornerGray.shape[::-1]

            templateCard1Gray = cv2.imread('card1.png', 0)
            wCard, hCard = templateCard1Gray.shape[::-1]

            resCorner = cv2.matchTemplate(imgScreenGray, templateCornerGray, cv2.TM_CCOEFF_NORMED)
            threshold = 0.7
            loc = numpy.where(resCorner >= threshold)
            wAreaCard = numpy.int(widthScreen * 0.1)
            hAreaCard = numpy.int(heightScreen * 0.1)
            print('one run')

            ## use mask to avoid multiple fgfindings
            mask = numpy.zeros(imgScreen.shape[:2], numpy.uint8)

            #iterate over all found corner
            for i, pt in enumerate(zip(*loc[::-1])):

                # check if already found corner
                if mask[int(pt[1] + hCorner / 2), int(pt[0] + wCorner / 2)] != 255:
                    mask[int(pt[1]):int(pt[1] + hCorner), int(pt[0]):int(pt[0] + wCorner)] = 255
                    cv2.rectangle(imgScreen, pt, (pt[0] + wCorner, pt[1] + hCorner), (0, 0, 255), 2)
                    if pt[1] + hAreaCard < hScreen and pt[0] + wAreaCard < wScreen:
                        cropCardGray = imgScreenGray[pt[1]:pt[1]+hAreaCard, pt[0]:pt[0]+wAreaCard]
                        windowNameCropped ='Cropped'+ str(i)
                        cv2.imshow(windowNameCropped, cropCardGray)
                        cv2.moveWindow(windowNameCropped, 0,500+ 100*i);

                        #cv2.imshow('Card', templateCard1Gray)

                        resCard =cv2.matchTemplate(cropCardGray,templateCard1Gray,cv2.TM_CCOEFF_NORMED)
                        locCard = numpy.where( resCard >= threshold)
                        for ii, ptCard in enumerate(zip(*locCard[::-1])):

                            cv2.rectangle(imgScreen, (ptCard[0]+pt[0],ptCard[1]+pt[1]), (ptCard[0]+pt[0] + wCard, ptCard[1]+pt[1] + hCard), (0,255,255), 2)

            # Display the picture
            imshowImage = cv2.imshow(windowName,
                                     cv2.resize(imgScreen, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC))
            # Display the picture in grayscale
            # cv2.imshow('OpenCV/Numpy grayscale',
            #            cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY))

            # Press "q" to quit
            buttonPress = cv2.waitKey(100);

            if buttonPress == ord('q'):
                cv2.destroyAllWindows()
                break
            if buttonPress == ord('s'):
                print('saving')
                # Save to the picture file
                mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
                print(output)
                ('closing')
                break
            time.sleep(0.01);

    cv2.destroyAllWindows()


except(KeyboardInterrupt):
    pass
