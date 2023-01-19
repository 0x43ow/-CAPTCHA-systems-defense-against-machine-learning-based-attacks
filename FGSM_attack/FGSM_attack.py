import tensorflow as tf
from PIL import Image
from torchvision import transforms
import torch
from random import randint
#loading ImageNNet
ImageNetModel = tf.keras.applications.MobileNetV2(include_top=True, weights='imagenet')
ImageNetModel.trainable = False

# ImageNet labels
decode_predictions = tf.keras.applications.mobilenet_v2.decode_predictions
print(decode_predictions)
global image_path, image_raw, image, image_probs, loss_object


#loading yolov5
yolov5 = torch.hub.load('ultralytics/yolov5', 'yolov5m', pretrained=True)

#loading Google Net
googlenet = torch.hub.load('pytorch/vision:v0.10.0', 'googlenet', pretrained=True)
googlenet.eval()
#Google Net labels
googlenetClassesFile = open("imagenet_classes.txt", "r")
googlenetCategories = [s.strip() for s in googlenetClassesFile.readlines()]





def preprocess(image):
  #preprocessing and resizing images
  image = tf.cast(image, tf.float32)
  image = tf.image.resize(image, (224, 224))
  image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
  image = image[None, ...]
  return image

# Helper function to extract labels from probability vector
def get_imagenet_label(probs):
  #returns the name of the top label
  return decode_predictions(probs, top=1)[0][0]

def predict(image):
  #passes the image to the model
  image_probs = ImageNetModel.predict(image)
  
  _, image_class, class_confidence = get_imagenet_label(image_probs)
  print('{} : {} : {:.2f}% Confidence'.format(_, image_class, class_confidence*100))
  return _, image_probs, image_class, class_confidence


def calculate_gradient(input_image, input_label):
  #doing FGSM to calculate the gradient
  with tf.GradientTape() as tape:
    tape.watch(input_image)
    prediction = ImageNetModel(input_image)
    
    loss = loss_object(input_label, prediction)

  # Get the gradients of the loss w.r.t to the input image.
  gradient = tape.gradient(loss, input_image)
  # Get the sign of the gradients to create the perturbation
  signed_grad = tf.sign(gradient)
  return signed_grad


def single_step_FGSM(image, index, epsilon =0.2):
  #given an image and its label, performs one step FGSM and returns a poisoned image
    label = tf.one_hot(index, image_probs.shape[-1])
    label = tf.reshape(label, (1, image_probs.shape[-1]))
    gradient = calculate_gradient(image, label)
    im = image - epsilon  * gradient
    im = tf.clip_by_value(im, -1, 1)
    return im

def multi_step_FGSM(image, desired_output, n_steps=1, epsilon =0.4):
  #multistep FGSM attack
    label = tf.one_hot(desired_output, image_probs.shape[-1])
    label = tf.reshape(label, (1, image_probs.shape[-1]))
    for _ in range(n_steps - 1):
        gradient = calculate_gradient(image, label) 
        # If there are n steps, we make them size 1/n 
        image = image - gradient * epsilon / n_steps
        image = tf.clip_by_value(image, -1, 1)
    return image




def googlenet_predict(path):
  #given image, returns the prediction of Google Net
  input_image = Image.open(path)
  #preprocesses the image
  preprocess = transforms.Compose([
      transforms.Resize(256),
      transforms.CenterCrop(224),
      transforms.ToTensor(),
      transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
  ])
  input_tensor = preprocess(input_image)
  input_batch = input_tensor.unsqueeze(0) # create a mini-batch as expected by the model

  with torch.no_grad():
      output = googlenet(input_batch)

  # The output has unnormalized scores. To get probabilities, you can run a softmax on it.
  probabilities = torch.nn.functional.softmax(output[0], dim=0)
  top5_prob, top5_catid = torch.topk(probabilities, 1)

  return int(top5_catid.int()), float(top5_prob)

def create_adversarial_image(path, animal="", multistep=True):
  """
  given image name and type of animal, performs multistep or single step FGSM deppending on the multistep flag
  example
    create_adversarial_image(0,'Cat',True)
  """
  global image_path, image_raw, image, image_probs, loss_object
  image_path = f'{animal}/{path}.jpg'
  #reading the image
  image_raw = tf.io.read_file(image_path)
  image = tf.image.decode_image(image_raw)
  image = preprocess(image)


  #passing the image to ImageNet
  label, image_probs, image_class, class_confidence = predict(image)
  loss_object = tf.keras.losses.CategoricalCrossentropy()

  og_label = int(label[-3])

  #passing the image to GoogleNet
  googlenetprediction, prop = googlenet_predict(image_path)

  for i in range(20):
    #random label generator 
    label = randint(0, 1000)
    #perform multi step FGSM, with 5 steps
    if multistep:
      adversarial_image = multi_step_FGSM(image, label, 5)
    else:
      adversarial_image = single_step_FGSM(image,label)

    #saving the intermediate image
    tf.keras.utils.save_img('intermediate_image.jpg', adversarial_image[0])

    #passing the adversarial image to yolov5
    prediction = yolov5('intermediate_image.jpg')
    
    names = prediction.pandas().xyxy[0].value_counts('name')
    if names.size == 0:
      continue
    print(label, names[0])
  

    googlenet_cur_pred = googlenet_predict('intermediate_image.jpg')[0]

    if animal.lower() not in prediction.pandas().xyxy[0].value_counts('name') and googlenet_cur_pred != googlenetprediction:
      tf.keras.utils.save_img(f'adv{animal}/{googlenetCategories[googlenet_cur_pred]}_{path}_{label}.jpg', adversarial_image[0])





# for i in range(10):
#   create_adversarial_image(i,'Cat')
