# -*- coding: utf-8 -*-
"""Image Classification (Rock, Paper, Scissors).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1m9LQYQ8X6je05QRQiu2UJsgzUg0-ruQJ

Nama : Debora Udania Simanjuntak

Email : debora.udania.simanjuntak@mail.ugm.ac.id 

Nama Program : Belajar Pengembangan Machine Learning

**1. Import Library**
"""

import tensorflow as tf
from tensorflow import keras

import numpy as np
import matplotlib.pyplot as plt

"""**2. Get the Dataset From The Resource**"""

!wget --no-check-certificate \
  https://dicodingacademy.blob.core.windows.net/picodiploma/ml_pemula_academy/rockpaperscissors.zip

"""**3. Understanding The Data**"""

import zipfile,os
local_zip='rockpaperscissors.zip'
zip_ref = zipfile.ZipFile(local_zip, 'r')
zip_ref.extractall(path='/rps')
zip_ref.close()

len(os.listdir('/rps/rockpaperscissors/paper/'))

len(os.listdir('/rps/rockpaperscissors/rock/'))

len(os.listdir('/rps/rockpaperscissors/scissors/'))

"""**4. Spilt the data into train and val, which each directory contains paper, rock, scissors**"""

pip install split-folders

import splitfolders
import shutil

os.makedirs('/rps/output')
os.makedirs('/rps/input')

os.makedirs('/rps/input/paper')
os.makedirs('/rps/input/rock')
os.makedirs('/rps/input/scissors')

source_dir = '/rps/rockpaperscissors/paper'
target_dir = '/rps/input/paper'
    
file_names = os.listdir(source_dir)
    
for file_name in file_names:
    shutil.move(os.path.join(source_dir, file_name), target_dir)

source_dir = '/rps/rockpaperscissors/rock'
target_dir = '/rps/input/rock'
    
file_names = os.listdir(source_dir)
    
for file_name in file_names:
    shutil.move(os.path.join(source_dir, file_name), target_dir)

source_dir = '/rps/rockpaperscissors/scissors'
target_dir = '/rps/input/scissors'
    
file_names = os.listdir(source_dir)
    
for file_name in file_names:
    shutil.move(os.path.join(source_dir, file_name), target_dir)

splitfolders.ratio("/rps/input",output="/rps/output",seed=1337,ratio=(.8,.2))

train_dir='/rps/output/train'
val_dir='/rps/output/val'

train_rock='/rps/output/train/rock'
train_paper='/rps/output/train/paper'
train_scissors='/rps/output/train/scissors'
val_rock='/rps/output/train/rock'
val_paper='/rps/output/train/paper'
val_scissors='/rps/output/train/scissors'

"""**5. Apply Image Data Generator**"""

from tensorflow.keras.preprocessing.image import ImageDataGenerator

train_datagen = ImageDataGenerator(
                    rescale=1./255,
                    rotation_range=20,
                    horizontal_flip=True,
                    shear_range = 0.2,
                    fill_mode = 'nearest')
 
test_datagen = ImageDataGenerator(
                    rescale=1./255,
                    rotation_range=20,
                    horizontal_flip=True,
                    shear_range = 0.2,
                    fill_mode = 'nearest')

train_generator = train_datagen.flow_from_directory(
        train_dir,  
        target_size=(150, 150), 
        batch_size=32,
        class_mode='categorical')
 
validation_generator = test_datagen.flow_from_directory(
        val_dir, 
        target_size=(150, 150), 
        batch_size=32,
        class_mode='categorical')

"""**6.  Build the Model**"""

model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(32, (3,3), activation='relu', input_shape=(150, 150, 3)),
    tf.keras.layers.MaxPooling2D(2, 2),
    tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dense(3, activation='softmax')
])

model.summary()

model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

"""**7. Train The Model**"""

# Make callback function
import tensorflow as tf
class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy')>0.95 ) and (logs.get('val_accuracy')>0.95):
      print("\accuracy and val_accuracy have reached > 95 percent!")
      self.model.stop_training = True
callbacks = myCallback()

history=model.fit(
      train_generator,
      steps_per_epoch=25,
      batch_size=64,
      epochs=20,
      validation_data=validation_generator,
      validation_steps=5, 
      verbose=2,
      callbacks=[callbacks])

# Plotting Accuraccy and Loss in Train and Test

plt.plot(history.history.get('accuracy'))
plt.plot(history.history.get('val_accuracy'))
plt.xlabel('epochs')
plt.ylabel('accuracy')
plt.legend(['train','test'])
plt.show()

plt.plot(history.history.get('loss'))
plt.plot(history.history.get('val_loss'))
plt.xlabel('epochs')
plt.ylabel('loss')
plt.legend(['train','test'])
plt.show()

"""**8. Predict New Image Using The Model**"""

# Commented out IPython magic to ensure Python compatibility.
from google.colab import files
from keras.preprocessing import image
import matplotlib.image as mpimg
# %matplotlib inline
 
uploaded = files.upload()
 
for fn in uploaded.keys():
  path = fn
  img = image.load_img(path, target_size=(150,150))
  imgplot = plt.imshow(img)
  x = image.img_to_array(img)
  x = np.expand_dims(x, axis=0)
  
  images = np.vstack([x])
  classes = model.predict(images, batch_size=10)
  
  print(fn)
  if np.argmax(classes)==0:
    print('paper')
  elif np.argmax(classes)==1:
    print('rock')
  else:
    print('scissors')



"""**9. Convert Model to TF-Lite**"""

converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with tf.io.gfile.GFile('model.tflite', 'wb') as f:
  f.write(tflite_model)

