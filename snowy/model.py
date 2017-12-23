import matplotlib.pyplot as plt
from keras import models, layers, losses, optimizers
from sklearn.model_selection import train_test_split


def train_model(x, y):
    # y2 = y.apply(lambda x: 1 if x > 0.1 else 0)
    # y2.describe()

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42
    )

    m = models.Sequential()
    m.add(layers.Dense(units=32, activation='relu', input_dim=720))

    # relu is the new hotness, tanh is traditional
    # sigmoid is good last step for classification
    m.add(layers.Dense(1, activation='relu'))

    m.compile(loss=losses.mean_squared_error,
              optimizer=optimizers.sgd())

    # with tensorflow.device('/cpu:0'):
    m.fit(x_train.as_matrix(), y_train.as_matrix(), epochs=100, batch_size=100)

    loss_and_metrics = m.evaluate(x_test.as_matrix(), y_test.as_matrix(), batch_size=128, verbose=1)
    pred = m.predict(x_test.as_matrix())

    x = y_test.index
    y1 = y_test
    y2 = pred

    plt.plot(y_test.index, y_test, '+b')
    plt.plot(y_test.index, pred, 'or')
    plt.title('SLC Weather predicted (o) vs actual (+)')
    plt.ylabel('Inches of rain')
    plt.xlabel('Date')
    plt.show()

    return m
