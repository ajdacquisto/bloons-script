from PIL import ImageGrab, Image
import sys, csv
import numpy as np





def fileToArr(fileNameStr):
    file = open(fileNameStr)
    csvreader = csv.reader(file)
    tempArr = []
    for row in csvreader:
            tempArr.append(row)
    file.close()
    return tempArr

def arrStrToInt(arr):
    tempArr = arr
    for row in tempArr:
        for n in range(len(row)):
            row[n] = int(row[n])
    return tempArr

def getNineDigitFromRGB(rgbList):
    return str(rgbList[0]) + str(rgbList[1]) + str(rgbList[2])

def createScreenArr(x1, x2, y1, y2, px):
    tempArr = []
    for thisRow in range(y1, y2):
        rowList = []
        for thisCol in range(x1, x2):
            rgbList = px[ thisCol, thisRow ]
            rowList.append( getNineDigitFromRGB(rgbList) )
            
        tempArr.append(rowList)
        
    return tempArr

def countMismatches(arr1, arr2):
    count = 0
    for r in range(len(arr1)):
        for c in range(len(arr1[0])):
             if arr1[r][c] != arr2[r][c]:
                 count += 1
    return count

def getPercentMatch(countMismatches, totalPixels):
    myDecimalValue = (totalPixels - countMismatches) / totalPixels
    return round( 100 * myDecimalValue )



def locate():

    TOP_LEFT = ( 701, 283, "Top left" )
    TOP_MIDDLE = ( 1124, 283, "Top middle" )
    TOP_RIGHT = ( 1548, 283, "Top right" )

    BOTTOM_LEFT = ( 701, 597, "Bottom left" )
    BOTTOM_MIDDLE = ( 1124, 597, "Bottom middle" )
    BOTTOM_RIGHT = ( 1548, 597, "Bottom right" )

    LOCATIONS = [TOP_LEFT, TOP_MIDDLE, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_MIDDLE, BOTTOM_RIGHT]

    X_RADIUS = 20
    Y_RADIUS = 20
    NUM_PIXELS = 4 * X_RADIUS * Y_RADIUS

    THRESHOLD_PERCENT = 95

    fileArr = fileToArr('pumpkin.csv')
    fileArr = arrStrToInt(fileArr)
    px = ImageGrab.grab().load() # Take a snapshot of the sreen

    numGoodMatches = 0

    for thisLocation in LOCATIONS:
        x_avg = thisLocation[0]
        y_avg = thisLocation[1]
        loc_name = thisLocation[2]

        thisScreenArr = createScreenArr(x_avg - X_RADIUS, x_avg + X_RADIUS,
                                        y_avg - Y_RADIUS, y_avg + Y_RADIUS, px)
        thisScreenArr = arrStrToInt(thisScreenArr)

        mismatchCounter = countMismatches(fileArr, thisScreenArr)

        if(mismatchCounter < NUM_PIXELS * (THRESHOLD_PERCENT / 100)):
            numGoodMatches += 1
            #print('Match #', numGoodMatches,'found.')
            #print(' -', getPercentMatch(mismatchCounter, NUM_PIXELS), '% match')
            #print(' -', loc_name)
            return thisLocation

    if(numGoodMatches == 0):
        #print('No matches found.')
        return -1
    else:
        return -2




#print(locate())