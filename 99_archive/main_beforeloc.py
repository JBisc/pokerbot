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

    time.sleep(1);

    while (True):
        # gtawin = win32gui.FindWindow(None,"War")
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

        font = cv2.FONT_HERSHEY_SIMPLEX


        with mss.mss() as sct:
            # The screen part to capture
            imageCounter = imageCounter + 1;
            monitor = {"top": top, "left": left, "width": widthScreen, "height": heightScreen}
            currentTime = int("{0:.0f}".format(time.time() * 1000));
            output = 'D:/images/' + "screenshot" + str(currentTime) + ".png".format(**monitor)

            # Get raw pixels from the screen, save it to a Numpy array
            imgScreen = numpy.array(sct.grab(monitor))
            imgScreenGray = cv2.cvtColor(imgScreen, cv2.COLOR_BGR2GRAY)
            #imgScreen = cv2.cvtColor(imgScreen, cv2.COLOR_BGRA2RGB)

            wScreen, hScreen = imgScreenGray.shape[::-1]
            images =[];
            images.append( {"name": 'screen', "imageGray": imgScreenGray, "image": imgScreen, "w": wScreen, "h": hScreen})

            templates =[];

            # define the list of boundaries
            boundaries = [
                ([190, 0, 0, 0], [230, 30, 10, 255]),#red
                ([0, 100, 0,0], [50, 150, 50,255]),#green
                ([190, 50, 0,0], [240, 140, 100,255]), #blue
                ([0, 0, 0, 0], [20, 20, 20, 255])  # black
            ]

            listOfCardsNames =['A','K','Q','J','10','9','8','7','6','5','4','3','2'];
            for i, name in enumerate(listOfCardsNames):
                template = cv2.imread(name+'card.png', 0)
                w, h = template.shape[::-1]
                object = {"name": name, "image": template, "w": w,"h":h}
                templates.append(object)
            for template in templates:
                res= cv2.matchTemplate(images[0]["imageGray"], template["image"], cv2.TM_CCOEFF_NORMED)
                threshold = 0.84
                loc = numpy.where(res >= threshold)

                for i, pt in enumerate(zip(*loc[::-1])):
                    # loop over the boundaries
                    maskSum =[]
                    for (lower, upper) in boundaries:
                        # create NumPy arrays from the boundaries
                        lower = numpy.array(lower, dtype="uint8")
                        upper = numpy.array(upper, dtype="uint8")

                        # find the colors within the specified boundaries and apply
                        # the mask
                        croppedDetection = imgScreen[pt[1]:pt[1]+template["h"], pt[0]:pt[0]+template["w"]]

                        mask = cv2.inRange(croppedDetection, lower,upper)
                        maskSum.append(numpy.int(100*numpy.sum(mask)/(template["w"]+template["h"])))

                    #cv2.putText(imgScreen, str(maskSum[0]), (pt[0], pt[1]-120), font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                    #cv2.putText(imgScreen, str(maskSum[1]), (pt[0], pt[1]-95), font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                    #cv2.putText(imgScreen, str(maskSum[2]), (pt[0], pt[1]-70), font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                    #cv2.putText(imgScreen, str(maskSum[3]), (pt[0], pt[1]-50), font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

                    maxSum= maskSum.index(max(maskSum))
                    if maxSum == 0:
                        cv2.putText(imgScreen, 'HEART', (pt[0], pt[1] - 40), font, 0.5, (0, 0, 255), 1,
                                    cv2.LINE_AA)
                    elif maxSum == 1:
                        cv2.putText(imgScreen, 'KREUZ', (pt[0], pt[1] - 40), font, 0.5, (0, 0, 255), 1,
                                    cv2.LINE_AA)
                    elif maxSum == 2:
                        cv2.putText(imgScreen, 'KARO', (pt[0], pt[1] - 40), font, 0.5, (0, 0, 255), 1,
                                    cv2.LINE_AA)
                    elif maxSum == 3:
                        cv2.putText(imgScreen, 'PIC', (pt[0], pt[1] - 40), font, 0.5, (0, 0, 255), 1,
                                    cv2.LINE_AA)
                    else:
                        cv2.putText(imgScreen, 'N', (pt[0], pt[1] - 40), font, 0.5, (0, 0, 255), 1,
                                    cv2.LINE_AA)

                    cv2.rectangle(imgScreen, pt, (pt[0] + template["w"], pt[1] + template["h"]), (0, 0, 255), 2)
                    cv2.putText(imgScreen, template["name"], (pt[0], pt[1]-20), font, 1, (0, 0, 255), 2, cv2.LINE_AA)


            # Display the picture
            imshowImage = cv2.imshow(windowName,
            cv2.resize(imgScreen, None, fx=1, fy=1, interpolation=cv2.INTER_CUBIC))
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
