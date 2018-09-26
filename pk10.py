import numpy as np
import pandas as pd
import random
from collections import deque
from sklearn import preprocessing
import time

SEQ_LEN = 100
FUTURE_NUM_PREDICT = 1
EPOCHS = 10
BATCH_SIZE = 64
NAME = f'PRED-{int(time.time())}'

def single_double(result):
    if result%2 == 0:
        return 0
    else:
        return 1

def preprocess_df(df):
    df = df.drop('open_result',1)
    for col in df.columns:
        if col != 'target':
            df[col] = preprocessing.scale(df[col].values)
    
    df.dropna(inplace=True)
    sequential_data = []
    prev_days = deque(maxlen=SEQ_LEN)
    for i in df.values:
        prev_days.append([n for n in i[:-1]])
        if len(prev_days) == SEQ_LEN:
            sequential_data.append([np.array(prev_days), i[-1]])

    random.shuffle(sequential_data)    

    X = []
    y = []
    for seq, target in sequential_data:
        X.append(seq)
        y.append(target)

    return np.array(X), y

# 430636*12
df = pd.read_csv('pk10.csv',names=['date', 'num', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'])
df = df[['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']]
df['open_result'] = df['one'].shift(-FUTURE_NUM_PREDICT)
df['target'] = list(map(single_double, df['open_result']))

times = sorted(df.index.values)
last_5pct = times[-int(0.05*len(times))]
last_10pct = times[-int(0.1*len(times))]

val_df = df[(df.index >= last_5pct)]
val_df = val_df[:-1]
train_df = df[(df.index < last_5pct)]

train_x, train_y = preprocess_df(train_df)
val_x, val_y = preprocess_df(val_df)
print(train_x.shape)
print(f"train data: {len(train_x)} validation: {len(val_x)}")
print(f"double: {train_y.count(0)}, single: {train_y.count(1)}")
print(f"VALIDATION double: {val_y.count(0)}, single : {val_y.count(1)}")

import keras
train_y = keras.utils.to_categorical(train_y, 2)
val_y = keras.utils.to_categorical(val_y, 2)

import tensorflow as tf
from keras import optimizers
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM, CuDNNLSTM, BatchNormalization
from keras.callbacks import TensorBoard
from keras.callbacks import ModelCheckpoint

model = Sequential()
model.add(CuDNNLSTM(50, input_shape=(train_x.shape[1:]), return_sequences=False))
model.add(Dropout(0.2))
model.add(BatchNormalization())  #normalizes activation outputs, same reason you want to normalize your input data.
'''
model.add(CuDNNLSTM(128, return_sequences=True))
model.add(Dropout(0.1))
model.add(BatchNormalization())

model.add(CuDNNLSTM(50, return_sequences=False))
model.add(Dropout(0.2))
model.add(BatchNormalization())

model.add(Dense(16, activation='relu'))
model.add(Dropout(0.2))
'''
#model.add(Dense(2, activation='softmax'))
model.add(Dense(2, activation='sigmoid'))

opt = optimizers.Adam(lr=0.001, decay=1e-6)

model.summary()

# Compile model
model.compile(
    loss='categorical_crossentropy',
    optimizer=opt,
    metrics=['accuracy']
)

tensorboard = TensorBoard(log_dir="logs/{}".format(NAME))
filepath = "RNN_Final-{epoch:02d}-{val_acc:.3f}"  # unique file name that will include the epoch and the validation acc for that epoch
checkpoint = ModelCheckpoint("models/{}.model".format(filepath, monitor='val_acc', verbose=1, save_best_only=True, mode='max')) # saves only the best ones

# Train model
history = model.fit(
    train_x, train_y,
    batch_size=BATCH_SIZE,
    epochs=EPOCHS,
    validation_data=(val_x, val_y),
    callbacks=[tensorboard, checkpoint],
)

# Score model
score = model.evaluate(val_x, val_y, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])
# Save model
model.save("models/{}".format(NAME))
