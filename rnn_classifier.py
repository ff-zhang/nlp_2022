import tensorflow as tf

from preprocessing import create_vectorize_layer, load_ds, load_env_vars
from text_embedding import gensim_to_keras_embedding


def train_rnn(vectorize_layer: tf.keras.layers.TextVectorization, train_ds: tf.data.Dataset, test_ds: tf.data.Dataset):
    word2vec = gensim_to_keras_embedding()

    model = tf.keras.Sequential([
        vectorize_layer,
        word2vec,
        tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64,  return_sequences=True)),
        tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(32)),
        tf.keras.layers.Dense(64, activation='tanh'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(1)
    ])

    model.compile(loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
                  optimizer=tf.keras.optimizers.Adam(1e-4),
                  metrics=[tf.keras.metrics.Recall(), tf.keras.metrics.Precision()])

    return model.fit(train_ds, epochs=10, validation_data=test_ds, validation_steps=30)


if __name__ == '__main__':
    settings, params = load_env_vars()

    ds_list = load_ds(settings['DATA_DIR'], is_xlsx=False, **params)
    vectorize_layer = create_vectorize_layer(ds_list, max_tokens=params['MAX_TOKENS'])
    model = train_rnn(vectorize_layer, ds_list[0], ds_list[1])

    test_loss, test_acc = model.evaluate(ds_list[2])

    print('Test Loss:', test_loss)
    print('Test Accuracy:', test_acc)

    model.save('models/rnn')
