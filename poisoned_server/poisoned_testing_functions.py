from PIL import Image
import os
from random import choice,randint,choices
from poisoned_model_run import predict
"""
used to test model's performance against different noise levels and methods
example:
testing_function(method_analysis=True, sample size)
testing_function(noise_analysis=True, sample size)
"""


#control globals
selective_poisoning_ammount = 75
merg_poisoning_ammount = 400
poison = True
poison_ammount = 1




def merg(folder,image1,image2,image3,ammount=int(merg_poisoning_ammount/2)):
    """
    adds a number of pixels from two images to a copy of the third one as specified by the ammount arguement, the resulting image will be used in the server. 
    no changes are made to any of the images.  
    """
    img1 = Image.open(f'{folder}/{image1}')
    img2 = Image.open(f'{folder}/{image2}')
    img3 = Image.open(f'{folder}/{image3}')
    out = img1.copy()
    for _ in range(ammount):
        x = randint(20,130)
        y = randint(10,40)
        pixel = img2.getpixel((x,y))
        out.putpixel((x,y),pixel)
    for _ in range(ammount):
        x = randint(20,130)
        y = randint(10,40)
        pixel = img3.getpixel((x,y))
        out.putpixel((x,y),pixel)
    out.save('captcha.png')
    img1.close()
    img2.close()
    img3.close()
    out.close()


def merg_gradient(folder,image,ammount=merg_poisoning_ammount):
    """merges new captcha images with the gradient of a 'iiiz' label"""
    img1 = Image.open(f'{folder}/{image}')
    img2 = Image.open('iiiz_reverse.png')
    out = img1.copy()
    for _ in range(ammount):
        x = randint(20,130)
        y = randint(10,40)
        pixel = img2.getpixel((x,y))
        out.putpixel((x,y),pixel)
    out.save('captcha.png')
    img1.close()
    img2.close()
    out.close()


def selective_poisoning(image_path,ammount=selective_poisoning_ammount):
    """
    poisons images by searching for characters that are more likely to cause mistakes
    if one of these characters is found, saves its index: [1st:4th] and poisons pixels accordingly
    """
    characters = [
    ('g','9'),('a','6'),('r','v'),('v','u'),('y','g'),('y','9')
    ,('i','1'),('1','l'),('1','i'),('q','9'),('q','g'),('0','o'),
    ('f','t'),('y','v'), ('b','6'), ('i','l'), ('8','9')
    ]
    #horizontal positions for the characters
    positions = [(10,35),(45,65),(75,95),(105,125)]
    wanted_position = 0
    index = 0
    solution = image_path[:4]
    #search for the letter
    for tup in characters:
        index = solution.find(tup[0])
        if index != -1:
            break
        else:
            index = solution.find(tup[1])
            if index != -1:
                break
    img = Image.open(image_path)
    if index != -1:
        wanted_position = positions[index]
        for _ in range(ammount):
            pos = (randint(wanted_position[0],wanted_position[1]),randint(20,30))
            img.putpixel(pos,(255,255,255))
        img.save('captcha.png')    
    else:
        #if non of these charachters was found, use merg_gradient instead
        merg_gradient('clean',image_path)



def get_images(poisoned, poisoning_ammount, merged=True, merge_with_gradient=False,selective_marg=False):
    """
    depending on the method selected by get_captcha_image, selects an image/images to create the next captcha image
    and saves it on disk
    """
    if not merged:
        if not poisoned:
            folder = 'clean'
        else:
            folder = 'poisoned'
        images = os.listdir(folder)
        image = choice(images)
        if selective_marg:
            selective_poisoning(image,selective_poisoning_ammount)
        else:
            if poisoned:
                while image[0] != str(poisoning_ammount)[0]:
                    image = choice(images)
            img = Image.open(f'{folder}/{image}')
            img.save('captcha.png')
            img.close()
        if image[1] == '_':
            solution = image[2:6]
        else:
            solution = image[:4]
    else:
        folder = choice(['clean','poisoned'])
        images = os.listdir(folder)
        if not merge_with_gradient:
            images = choices(images,k=3)
            if images[0][1] == '_':
                solution = images[0][2:6]
            else:
                solution = images[0][0:4]
            merg(folder,images[0],images[1],images[2],int(merg_poisoning_ammount/2))
        else:
            image = choice(images)
            if images[1] == '_':
                solution = images[2:6]
            else:
                solution = images[0:4]
            merg_gradient(folder,image,merg_poisoning_ammount)
    return solution



def get_captcha_image(poisoned, poisoning_ammount,method=0):
    """
    randomly selects a method to poison images with different probabilities:
    using images with one changed pixel 4.2%
    using images with two changed pixels 1.3%
    using images with three changed pixels 1.3%
    merging new images with iiiz's gradient 53.3% 
    selective merg 13.3% 
    merging three images 26.6% 
    can be controlled to use a specific method:
        method 0: default mode to choose random methods
        method 1: only uses the 3 image merging method
        method 2: only uses the gradient merging method
        method 3: only uses the selective poisoning method
    """
    global poison
    global poison_ammount
    
    merg = False
    selective_merg = False
    merg_with_gradient = False
    if method == 0:
        x = randint(0,15000)
    elif method == 1:
        #merg 
        x = 11000
    elif method == 2:
        #grad
        x = 2000
    else:
        #selective
        x = 5000
    if x < 1000:
        poison = True
        if x > 800:
            poison_ammount = 3
        elif x > 600:
            poison_ammount = 2
        else:
            poison_ammount = 1
    else:
        merg = True
        if x < 4000:
            merg_with_gradient=True
        elif x < 10000:
            selective_merg = True
    return get_images(poison,poison_ammount,merg,merg_with_gradient,selective_merg)




def testing_function(method_analysis=False, noise_analysis=False, sample_size = 100):
    """
    used to test the efficiency of methods or noise levels
    writes the info on test_log.txt
    """
    global selective_poisoning_ammount
    global merg_poisoning_ammount
    sol = ''
    pred = ''
    f = open('test_log.txt', 'w')
    if noise_analysis:
        #evaluate noise levels
        selective_noise_levels = [10,25,50,75,100,100,100]
        merg_noise_levels = [50,100,200,400,500,600,700]

        for i in range(7):
            #choose one of the noise levels
            selective_poisoning_ammount = selective_noise_levels[i]
            merg_poisoning_ammount = merg_noise_levels[i]
            correct = 0
            for _ in range(sample_size):
               #generate 100 captcha images and pass them to the model
               sol = get_captcha_image(poison,poison_ammount) 
               pred = predict('captcha.png')
               if pred == sol:
                    correct += 1
            #save the used noise levels and the model's accuracy and write them on test_log.txt
            f.write(f'noise: poison ammount:{selective_poisoning_ammount},{merg_poisoning_ammount}, accuracy:{round((correct / sample_size) * 100,2)}%\n')

    elif method_analysis:
        #evaluate defense methods 
        methods = [1,2,3]
        for method in methods:
            correct = 0
            for _ in range(sample_size):
                #generate 100 captcha images with the selected method and pass them too the model
                sol = get_captcha_image(poison,poison_ammount,method)
                pred = predict('captcha.png')
                if pred == sol:
                    correct += 1
            #save the used method and the model's accuracy and write them on test_log.txt
            f.write(f'method: {method} , accuracy: {round((correct / sample_size) * 100,2)}%\n')
    f.close()
