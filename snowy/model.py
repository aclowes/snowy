import pandas
import matplotlib
from google.cloud import storage
from keras import models, layers
from sklearn.model_selection import train_test_split


def train_model(x, y, image_output='file'):
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42
    )

    # relu is the new thing, tanh is traditional
    # sigmoid is good last step for classification
    m = models.Sequential()
    m.add(layers.Dense(360, input_dim=720))
    m.add(layers.GaussianNoise(.1))
    m.add(layers.Dense(45, input_dim=360))
    m.add(layers.GaussianNoise(.1))
    m.add(layers.Dense(1))
    # sgd optimizer is common for categorization, adam is good for linear
    m.compile(loss='mean_squared_error', optimizer='adam')
    history = m.fit(
        x_train.as_matrix(), y_train.as_matrix(),
        epochs=20, batch_size=80,
        validation_data=(x_test.as_matrix(), y_test.as_matrix())
    )

    if image_output == 'file':
        # save image to a file
        matplotlib.use('Agg')

    # after configuring output!
    import matplotlib.pyplot as plt

    # plot the loss history over the epochs
    pandas.DataFrame(history.history).plot()
    plt.title('Loss by epoch')
    render_image(plt, image_output, 'history.png')

    # plot actual vs predicted - test data
    pred = m.predict(x_test.as_matrix())
    p = pandas.Series(pred.flatten())
    p.index = y_test.index
    print(f'Test data correlation {p.corr(y_test)}')
    plt.title('Testing Data')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.plot(y_test, p, '+b')
    render_image(plt, image_output, 'test_data.png')

    # plot actual vs predicted - train data
    pred = m.predict(x_train.as_matrix())
    p = pandas.Series(pred.flatten())
    p.index = y_train.index
    plt.title('Training Data')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.plot(y_train, p, '+b')
    render_image(plt, image_output, 'train_data.png')

    return history


def render_image(plt, image_output, filename):
    if image_output == 'file':
        plt.savefig(f'data/{filename}')

        client = storage.Client()
        bucket = client.bucket('static.yawn.live')
        blob = bucket.blob(f'snowy/{filename}')
        blob.upload_from_filename(f'data/{filename}')
        blob.make_public()

    else:
        plt.show()

    plt.clf()
