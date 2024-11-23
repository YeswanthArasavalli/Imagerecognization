# -*- coding: utf-8 -*-
"""Untitled14.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Zvl75hIaUGIUF8gTsjMxnuKYGB3mwwxY
"""

# prompt: first do face detection and face recognition then use CNN's models(VGGFace, FaceNet, ResNet). which have more accuracy use that. training set or directory is Sree, test test is Tester.

import cv2
import os
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.applications import VGG16, ResNet50
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import accuracy_score


# Function for face detection
def detect_faces(image_path):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    detected_faces = []
    for (x, y, w, h) in faces:
        detected_faces.append(img[y:y + h, x:x + w])  # Extract face region
    return detected_faces


# Function to preprocess image data for CNN models
def preprocess_image(image):
  image = cv2.resize(image, (224, 224))  # Adjust size as per model input
  image = image / 255.0  # Normalize pixel values
  return image


# Load and preprocess data
train_dir = "/content/sample_data/Sree"  # Replace with your training directory
test_dir = "/content/sample_data/Tester" # Replace with your test directory
train_data = []
train_labels = []
test_data = []
test_labels = []

# Training data preparation
for item in os.listdir(train_dir):
    item_path = os.path.join(train_dir, item)
    # Check if the item is a directory
    if os.path.isdir(item_path):
        # If it's a directory, treat it as a label and process images inside it
        label = item
        for filename in os.listdir(item_path):
            image_path = os.path.join(item_path, filename)
            faces = detect_faces(image_path)
            for face in faces:
                preprocessed_face = preprocess_image(face)
                train_data.append(preprocessed_face)
                train_labels.append(label)
    else:
        # If it's a file (likely an image), process it directly
        image_path = item_path
        faces = detect_faces(image_path)
        for face in faces:
            preprocessed_face = preprocess_image(face)
            train_data.append(preprocessed_face)
            train_labels.append(item)

# Testing data preparation
test_data = []  # Initialize test_data as a list
test_labels = []
for item in os.listdir(test_dir):
    item_path = os.path.join(test_dir, item)
    # Check if the item is a directory
    if os.path.isdir(item_path):
        # If it's a directory, treat it as a label and process images inside it
        label = item
        for filename in os.listdir(item_path):
            image_path = os.path.join(item_path, filename)
            faces = detect_faces(image_path)
            for face in faces:
                preprocessed_face = preprocess_image(face)
                test_data.append(preprocessed_face) # Append to the list
                test_labels.append(label)
    else:
        # If it's a file (likely an image), process it directly
        image_path = item_path
        faces = detect_faces(image_path)
        for face in faces:
            preprocessed_face = preprocess_image(face)
            test_data.append(preprocessed_face) # Append to the list
            test_labels.append(item)

# Convert data to NumPy arrays
train_data = np.array(train_data)
train_labels = np.array(train_labels)
test_data = np.array(test_data)
test_labels = np.array(test_labels)

# Split data into training and validation sets (optional but recommended)
X_train, X_val, y_train, y_val = train_test_split(train_data, train_labels, test_size=0.2, random_state=42)

# Load pre-trained model (VGG16 or ResNet50)
base_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
# base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

# Add custom classification layers
x = base_model.output
x = Flatten()(x)
x = Dense(128, activation='relu')(x)  # Adjust units as needed
predictions = Dense(len(np.unique(train_labels)), activation='softmax')(x)  # Output layer

# Create the final model
model = Model(inputs=base_model.input, outputs=predictions)

# Freeze the pre-trained layers (optional, but often helpful for fine-tuning)
for layer in base_model.layers:
    layer.trainable = False

# Compile the model
model.compile(optimizer=Adam(learning_rate=0.0001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Import necessary libraries
from sklearn.preprocessing import LabelEncoder

# ... (your existing code for data loading and preprocessing) ...

# Create a LabelEncoder instance
label_encoder = LabelEncoder()

# Fit the encoder on all unique labels (from both train and validation sets)
all_labels = np.concatenate((y_train, y_val), axis=0)
label_encoder.fit(all_labels)

# Transform your labels to numerical values
y_train = label_encoder.transform(y_train)
y_val = label_encoder.transform(y_val)

# Handle unseen labels in test data
# Instead of directly transforming test_labels, iterate through them and handle unknown labels
test_labels_encoded = []
for label in test_labels:
    try:
        encoded_label = label_encoder.transform([label])[0]  # Encode if known
    except ValueError:
        encoded_label = -1  # Assign a special value for unknown labels (e.g., -1)
        print(f"Warning: Unseen label '{label}' in test data. Assigned -1.")
    test_labels_encoded.append(encoded_label)

test_labels = np.array(test_labels_encoded)

# ... (rest of your model training and evaluation code) ...

# Train the model
model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_val, y_val)) # Adjust epochs and batch size

# Evaluate the model on the test set
y_pred = model.predict(test_data)
y_pred_classes = np.argmax(y_pred, axis=1)
accuracy = accuracy_score(test_labels, y_pred_classes)
print("Test Accuracy:", accuracy)

# prompt: now, we have to deploy above code in streamlit to check various images to get output as it matches our input or not

# Install Streamlit if not already installed

# Import necessary libraries
import streamlit as st
import cv2
import os
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.applications import VGG16
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

# ... (Your existing code for data loading, preprocessing, model training) ...

# Streamlit app
st.title("Face Recognition App")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Read the image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)

    # Face detection
    faces = detect_faces(img)  # Assuming 'detect_faces' function is defined

    if len(faces) > 0:
      for i, face in enumerate(faces):
        preprocessed_face = preprocess_image(face)  # Assuming 'preprocess_image' function is defined
        preprocessed_face = np.expand_dims(preprocessed_face, axis=0)  # Add batch dimension
        prediction = model.predict(preprocessed_face)
        predicted_class = np.argmax(prediction, axis=1)[0]
        predicted_label = label_encoder.inverse_transform([predicted_class])[0]

        st.image(face, caption=f"Detected Face {i+1}", use_column_width=True)
        st.write(f"Prediction: {predicted_label}")
    else:
        st.write("No faces detected in the image.")
else:
    st.write("Please upload an image.")