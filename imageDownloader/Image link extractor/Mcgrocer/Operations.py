

def operations(currentWeight):
    currentWeight = float(currentWeight)


    if currentWeight <= .99:
        return 1
    elif currentWeight >= 1 and currentWeight < 1.99:
        return 1
    elif currentWeight >= 2 and currentWeight < 3.99:
        return currentWeight + .5
    else:
        return currentWeight - .5

userName = "Direct.mcgrocer@gmail.com"
passWord = "MdRakiburIslam/1908/"
save = False