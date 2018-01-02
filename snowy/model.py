import pandas
import matplotlib.pyplot as plt
from keras import models, layers, regularizers
from sklearn.model_selection import train_test_split


def train_model(x, y):
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42
    )

    # relu is the new hotness, tanh is traditional
    # sigmoid is good last step for classification
    m = models.Sequential()
    m.add(layers.Dense(80, activation='relu', input_dim=80))
    # m.add(layers.BatchNormalization())
    m.add(layers.Dense(80, activation='relu', input_dim=80))
    m.add(layers.Dense(1))
    # sgd optomizer is common for categorization, adam is good for linear
    m.compile(loss='mean_squared_error', optimizer='adam')
    history = m.fit(
        x_train.as_matrix(), y_train.as_matrix(),
        epochs=80, batch_size=80,
        validation_data=(x_test.as_matrix(), y_test.as_matrix())
    )

    # plot the loss history over the epochs
    pandas.DataFrame(history.history).plot()
    plt.show()

    # plot actual vs predicted - test data
    pred = m.predict(x_test.as_matrix())
    p = pandas.Series(pred.flatten())
    p.index = y_test.index
    print(f'Test data correlation {p.corr(y_test)}')
    fig, ax = plt.subplots()
    ax.yaxis.set_label('Actual')
    ax.xaxis.set_label('Predicted')
    ax.plot(y_test, p, '+b')
    plt.show()

    # plot actual vs predicted - train data
    pred = m.predict(x_train.as_matrix())
    p = pandas.Series(pred.flatten())
    p.index = y_train.index
    fig, ax = plt.subplots()
    ax.yaxis.set_label('Actual')
    ax.xaxis.set_label('Predicted')
    ax.plot(y_train, p, '+b')
    plt.show()

    return history