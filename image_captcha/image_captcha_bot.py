import random
import pygame as pg
import torch
from time import sleep
import os
"""
uses pygame to create a GUI for a an image captcha system
will display 9 random images of cats and dogs from the Cat/Dog folders
the image are passed to yolov5m and it will mark cat images in green, dog images in red and if non were found, in black.
"""



#defining colors as tuples
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BLUE = (0, 255, 255)
WHITE = (255, 255, 255)
GRAY = (220, 220, 220)


ROWS, COLS = 28, 28
DEFAULT_IMAGE_SIZE = (200, 200)

#loading yolov5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5m', pretrained=True)


#starting pygame UI
pg.init()
screen = pg.display.set_mode((600, 600))
COLOR_INACTIVE = pg.Color('lightskyblue3')
COLOR_ACTIVE = pg.Color('dodgerblue2')
FONT = pg.font.Font(None, 32)


#listing all the images if the Dog and Cat directories
DogDirectory = 'Dog/' 
CatDirectory = 'Cat/'
Dogarr = os.listdir(DogDirectory)
Catarr = os.listdir(CatDirectory)


#the class for the GUI
class ImageBox:
    #draw the GUI
    def __init__(self, x, y, w, h):
        self.rect = pg.Rect(x, y, w, h)
        self.update(GRAY)

    #call update on mouse click
    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.update()
            pg.time.wait(10)
    #update the GUI, choose random images on dogs and cats to display
    def update(self, color):
        self.color = color
        if color != GRAY:
            return
        self.path, self.type = (DogDirectory, 'Dog') if random.randint(0, 1) else (CatDirectory, 'Cat')
        if self.type == 'Dog':
            self.path += Dogarr[random.randint(0, len(Dogarr)-1)]
        else:
            self.path += Catarr[random.randint(0, len(Catarr)-1)]
        self.imp = pg.image.load(self.path).convert()
        self.imp = pg.transform.scale(self.imp , DEFAULT_IMAGE_SIZE)

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.imp, self.rect)
        pg.draw.rect(screen, self.color, self.rect, 2 if self.color == GRAY else 4)


def main():
    clock = pg.time.Clock()
    #giving image boxes indicies
    positions = []
    for i in range(3):
        for j in range(3):
            positions.append((i, j))


    Boxes = [ImageBox(i*200, j*200, 200, 200) for i, j in positions]
    done = False

    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            for box in Boxes:
                box.handle_event(event)
        
        for box in Boxes:
            #pass each image in the image box to the model
            if box.color == GRAY:
                #change the image's color depending on its prediction. green for cat, red for dog, black if non was fond
                prediction = model(box.path).pandas().xyxy[0].value_counts('name')
                if "cat" in prediction:
                    box.update(GREEN)
                elif "dog" in prediction:
                    box.update(RED)
                else:
                    box.update(BLACK)
            else:
                box.update(GRAY)

        screen.fill((30, 30, 30))
        for box in Boxes:
            box.draw(screen)
        pg.display.flip()

        if Boxes[0].color != GRAY:
            sleep(3)


if __name__ == '__main__':
    main()
    pg.quit()