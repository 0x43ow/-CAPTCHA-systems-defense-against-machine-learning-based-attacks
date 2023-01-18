import http.server
import socketserver
import time
import signal
from PIL import Image
import os
from random import choice,randint,choices
"""
this is a server that uses poisoned versions of the captcha images used in JUST website designed to defend text captcha systems against machine
learning attacks    
to access the server:  http://127.0.0.1:50000/
"""



def handler(signum, frame):
    """
    SIGINT signal handler writing log info before shutting down the server. LOG.txt will contain analytical data for the server's last run
    """
    f = open('LOG.txt','w')
    total_time = round(time.time() - RUN_TIME)
    f.write(f"""total run time:    {total_time} seconds
total requests:    {total_attempts}
requests per second:    {round(total_attempts/total_time,4)}
requests per second without the hard coded latency:    {round(total_attempts/(total_time - total_attempts * (0.6)),4)}
successfull accesses:    {successfull_accesses}
successfull accesses per second:    {round(successfull_accesses/total_time,4)}
successfull accesses per second without the hard coded latency:    {round( successfull_accesses / (total_time - total_attempts * (0.6)),4)}""")
    f.close()
    print("server closed, written log on LOG.txt")
    exit(1)


#constants and globals
PORT = 50000
RUN_TIME = time.time()
poison = True
poison_ammount = 1
successfull_accesses = 0
total_attempts = 0
solution = ''



def merg(folder,image1,image2,image3,ammount=100):
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



def merg_gradient(folder,image,ammount=200):
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





def get_images(poisoned, poisoning_ammount, merged=True, merge_with_gradient=False,selective_marg=False):
    """
    depending on the method selected by get_captcha_image, selects an image/images to create the next captcha image
    and prepares it to be displayed on the server
    """
    if not merged:
        if not poisoned:
            folder = 'clean'
        else:
            folder = 'poisoned'
        images = os.listdir(folder)
        image = choice(images)
        if selective_marg:
            selective_poisoning(image)
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
            merg(folder,images[0],images[1],images[2])
        else:
            image = choice(images)
            if images[1] == '_':
                solution = images[2:6]
            else:
                solution = images[0:4]
            merg_gradient(folder,image)
    return solution




def selective_poisoning(image_path,ammount=50):
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




def get_captcha_image(poisoned, poisoning_ammount):
    """
    randomly selects a method to poison images with different probabilities:
    using images with one changed pixel 4.2%
    using images with two changed pixels 1.3%
    using images with three changed pixels 1.3%
    merging new images with iiiz's gradient 53.3% 
    selective merg 13.3% 
    merging three images 26.6% 
    """
    global poison
    global poison_ammount
    merg = False
    selective_merg = False
    merg_with_gradient = False
    x = randint(0,15000)
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
        if x < 9000:
            merg_with_gradient=True
        elif x < 11000:
            selective_merg = True
    return get_images(poison,poison_ammount,merg,merg_with_gradient,selective_merg)





class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """
        custom GET request handler.
        """
        global solution
        global total_attempts
        global successfull_accesses
        if total_attempts == 0:
        #get captcha on first run
            sol = get_captcha_image(poison,poison_ammount)
            total_attempts+=1
            solution = sol
        else:
            #if the image was not modified, retrive its solution
            sol = solution
        if self.path.find("input")!=-1:
            #checking the value of the user's input
            start = 8
            if self.path.find("index.html")!=-1:
                start += 10
            field=''
            for i in self.path[start:]:
                field+=i
            if field == sol:
                #comparing it with the captcha's solution. on success, takes the user to the service page
                successfull_accesses+=1
                self.path = 'access.html'
            else:
                #on fail, create a new captcha
                solution = get_captcha_image(poison,poison_ammount)
                total_attempts+=1
        elif self.path.find("click=true") !=-1 or self.path == "/captcha.png":
            #if the user presses the captcha reset button
            solution = get_captcha_image(poison,poison_ammount)
            total_attempts+=1
            #wait 0.6 seconds to wait for the new captcha image to be created and written on disk, otherwise the server might display the old image
            time.sleep(0.6)
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


#handle SIGINT signal
signal.signal(signal.SIGINT, handler)
Handler = MyHttpRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    #create server. serve until SIGINT signal is caught
    print("Http Server Serving at port", PORT)
    httpd.serve_forever()
