"""
Model:

"""
from keras import models, layers, losses, optimizers

model = models.Sequential()

model.add(layers.Dense(units=64, activation='relu', input_dim=100))
model.add(layers.Dense(units=10, activation='softmax'))

model.compile(loss=losses.categorical_crossentropy,
              optimizer=optimizers.SGD(lr=0.01, momentum=0.9, nesterov=True))

# x_train and y_train are Numpy arrays --just like in the Scikit-Learn API.
model.fit(x_train, y_train, epochs=5, batch_size=32)

loss_and_metrics = model.evaluate(x_test, y_test, batch_size=128)

classes = model.predict(x_test, batch_size=128)

