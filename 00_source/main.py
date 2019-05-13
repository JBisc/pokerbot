import mss
import mss.tools
import time
import cv2
import math

import numpy

from win32 import win32gui
import numpy

def get_angle(p1, p2):
    return math.atan2(p1[1] - p2[1], p1[0] - p2[0]) * 180/math.pi

def windowEnumerationHandler(hwnd, top_windows):
    top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))


try:
    imageCounter = 0;

    time.sleep(1);

    ##Debug mode
    debugMode=True;

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
            centerScreen = (int(wScreen/2),int(hScreen/2))
            images =[];
            images.append( {"name": 'screen', "imageGray": imgScreenGray, "image": imgScreen, "w": wScreen, "h": hScreen})

            templates =[];
            allFindings=[];

            # define the list of boundaries
            boundaries = [
                ([190, 0, 0, 0], [230, 30, 10, 255]),#red
                ([0, 100, 0,0], [50, 150, 50,255]),#green
                ([190, 50, 0,0], [240, 140, 100,255]), #blue
                ([0, 0, 0, 0], [20, 20, 20, 255])  # black
            ]

            listOfCardsNames =['A','K','Q','J','10','9','8','7','6','5','4','3','2'];

            # determine position of the button
            templateButton = cv2.imread('../01_templates/' + 'button.png', 0)
            w, h = templateButton.shape[::-1]
            res = cv2.matchTemplate(images[0]["imageGray"], templateButton, cv2.TM_CCOEFF_NORMED)

            threshold = 0.80
            loc = numpy.where(res >= threshold)
            button = centerScreen;
            for i, pt in enumerate(zip(*loc[::-1])):
                cv2.circle(imgScreen, (pt[0]+int(w/2),pt[1]+int(h/2)), 10, [0,0,255], thickness=3, lineType=8, shift=0)
                button = pt;

            if(button == centerScreen):
                print('Not button fgound')

            angleButton= get_angle(centerScreen, button)
            print(angleButton)

            angleMapping = numpy.array([ 30, 88,  140, -171, -106, -35])
            diffAngles = angleMapping;
            diffAngles[:] = [x - angleButton for x in angleMapping]
            diff=numpy.abs(angleMapping - angleButton)
            indMinAngle = numpy.unravel_index(numpy.argmin(diff, axis=None), diff.shape);
            playerWithButton= indMinAngle
            for i, name in enumerate(listOfCardsNames):
                template = cv2.imread('../01_templates/'+name+'card.png', 0)
                w, h = template.shape[::-1]
                object = {"name": name, "image": template, "w": w,"h":h}
                templates.append(object)
            # check if templates can be found in the image
            for template in templates:
                res= cv2.matchTemplate(images[0]["imageGray"], template["image"], cv2.TM_CCOEFF_NORMED)
                threshold = 0.85
                if(template["name"] =='10'):
                    threshold = 0.75
                else:
                    threshold = 0.87


                loc = numpy.where(res >= threshold)
                #trough double detetcions away
                for i, pt in enumerate(zip(*loc[::-1])):
                    finding = {"template": template["name"], "pt": pt, "category": 'unknown'}
                    mindistance = 100000;
                    for fi in allFindings:
                        pt1 = fi["pt"]
                        pt2 = finding["pt"]
                        distance = math.sqrt(((pt1[0] - pt2[0]) ** 2) + ((pt1[1] - pt2[1]) ** 2))
                        mindistance =min(distance,mindistance)
                    if(mindistance >20):
                        allFindings.append(finding)
            # determine if hand or flop
            for i,fi in enumerate(allFindings):
                pt1 = fi["pt"]
                if pt1[1] > images[0]["h"]*1/3 and pt1[1] < images[0]["h"]*1/2 and pt1[0] > images[0]["w"]*1/4 and pt1[1] < images[0]["w"]*2/3 :
                    allFindings[i]["category"] = 'flop'
                else:
                    allFindings[i]["category"] = 'hand'

            # deterine whcih color the card has
            for i,fi in enumerate(allFindings):
                # loop over the boundaries
                pt = fi["pt"]

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


                maxSum= maskSum.index(max(maskSum))
                sizeFont= 0.4
                if maxSum == 0:
                    cv2.putText(imgScreen, 'HEART', (pt[0], pt[1] - 40), font, sizeFont, (0, 0, 255), 1,
                                cv2.LINE_AA)
                elif maxSum == 1:
                    cv2.putText(imgScreen, 'KREUZ', (pt[0], pt[1] - 40), font, sizeFont, (0, 0, 255), 1,
                                cv2.LINE_AA)
                elif maxSum == 2:
                    cv2.putText(imgScreen, 'KARO', (pt[0], pt[1] - 40), font, sizeFont, (0, 0, 255), 1,
                                cv2.LINE_AA)
                elif maxSum == 3:
                    cv2.putText(imgScreen, 'PIC', (pt[0], pt[1] - 40), font, sizeFont, (0, 0, 255), 1,
                                cv2.LINE_AA)
                else:
                    cv2.putText(imgScreen, 'N', (pt[0], pt[1] - 40), font, sizeFont, (0, 0, 255), 1,
                                cv2.LINE_AA)

            # plot i figure
            for i, fi in enumerate(allFindings):
                # loop over the boundaries


                # draw a red rectangle surrounding Adrian in the image
                # along with the text "PyImageSearch" at the top-left
                # corner
                #cv2.rectangle(imgScreen, (pt[0]-10, pt[1]+10), (pt[0]+50, pt[1]-90), (255, 255, 255), -1)



                pt = fi["pt"]
                cv2.rectangle(imgScreen, pt, (pt[0] + template["w"], pt[1] + template["h"]), (0, 0, 255), 2)
                cv2.putText(imgScreen, str(fi["template"]), (pt[0], pt[1]-10), font, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
                cv2.putText(imgScreen, str(fi["category"]), (pt[0], pt[1]-60), font, 0.7, (0, 0, 255), 2, cv2.LINE_AA)


            # Display the picture
            if(debugMode):
                imshowImage = cv2.imshow(windowName,
                cv2.resize(imgScreen, None, fx=0.7, fy=0.7, interpolation=cv2.INTER_CUBIC))


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
