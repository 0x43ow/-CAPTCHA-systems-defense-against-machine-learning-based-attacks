from os import listdir
import torch
from time import time
"""
used to evalute the image captcha system's accuracy against yolov5m
call test_undefended(sample size)
or
call test_defended(dog sample size, cat sample size)
writes the info on undefended_log.txt and defended_log.txt
"""




model = torch.hub.load('ultralytics/yolov5', 'yolov5m', pretrained=True)

def test_undefended(sample=100):  
    """"
    used to evaluate yolov5m's performance on the dog and cat dataset
    """
    # listing all images in the Dog and Cat directories
    dogs = listdir('Dog/')
    cats = listdir('Cat/')
    #checking for the sample size and setting to the limit if its larger than it
    MAX = min(len(dogs),len(cats))
    if sample > MAX - 1:
        sample = MAX - 1

    dogs = dogs[:sample]
    cats = cats[:sample]

    #logging info
    total_attempts = 2 * sample
    correct_dog = 0
    correct_cat = 0
    prediction = ''
    start_time = time()


    #looping over dog images and passing them to yolov5m
    for dog in dogs:
        prediction = model(f'Dog/{dog}').pandas().xyxy[0].value_counts('name')
        if 'dog' in prediction:
            correct_dog += 1

    #looping over cat images and passing them to yolov5m
    for cat in cats:
        prediction = model(f'Cat/{cat}').pandas().xyxy[0].value_counts('name')
        if 'cat' in prediction:
            correct_cat += 1 


    #saving the info and writing them on undefended_log.txt
    correct = correct_dog + correct_cat
    total_time = time() - start_time


    f = open('undefended_log.txt', 'w')
    f.write(
    f"""
    total attempts = {total_attempts}
    accuracy: {round((correct / total_attempts) * 100,2)}%
    dog labeling accuracy: {round(correct_dog / sample,2)}%
    cat labeling accuracy: {round(correct_cat / sample,2)}%
    attempts per second = {round(total_attempts / total_time,3)}
    successful attempts per second = {round(correct / total_time,3)}
    """)
    f.close()


def test_defended(sample_dog=100, sample_cat=100):  
    """"
    used to evaluate yolov5m's performance on the adversarial dog and cat dataset
    """
    # listing all images in the advDog and advCat directories
    dogs = listdir('advDog/')
    cats = listdir('advCat/')


    #checking for the sample size limit, setting it to the max if its larger than it
    if sample_cat > len(cats):
        sample_cat = len(cats) - 1

    if sample_dog > len(dogs) - 1:
        sample_dog = len(dogs) - 1

    dogs = dogs[:sample_dog]
    cats = cats[:sample_cat]

    #logging info
    total_attempts = sample_cat + sample_dog
    correct_dog = 0
    correct_cat = 0
    prediction = ''
    start_time = time()

    #looping over adversarial dogs images and passing them to yolov5m
    for dog in dogs:
        prediction = model(f'advDog/{dog}').pandas().xyxy[0].value_counts('name')
        if 'dog' in prediction:
            correct_dog += 1


    #looping over adversarial cats images and passing them to yolov5m
    for cat in cats:
        prediction = model(f'advCat/{cat}').pandas().xyxy[0].value_counts('name')
        if 'cat' in prediction:
            correct_cat += 1      
    

    #saving the info and writing them on defended_log.txt

    correct = correct_cat  + correct_dog

    total_time = time() - start_time
    
    f = open('defended_log.txt', 'w')
    f.write(
    f"""
    total attempts = {total_attempts}
    accuracy: {round((correct / total_attempts) * 100,2)}%
    dog labeling accuracy: {round(correct_dog / sample_dog,2)}%
    cat labeling accuracy: {round(correct_cat / sample_cat,2)}%
    attempts per second = {round(total_attempts / total_time,3)}
    successful attempts per second = {round(correct / total_time,3)}
    """)
    f.close()

