from keras import backend as K
from utils import utils


class Loss(object):
    """Abstract class for defining the loss function to be minimized.

    The loss function should be built by defining :func:`build_loss` function.

    The attribute :attr:`name` should be defined to identify loss function with verbose outputs.
    Defaults to 'Unnamed Loss' if not overridden.
    """
    def __init__(self):
        self.name = "Unnamed Loss"

    def __str__(self):
        return self.name

    def build_loss(self, img):
        """Implement this function to build the loss function expression.

        Any additional arguments required to build this loss function may be passed in via :func:`__init__`.

        Ideally, the function expression must be compatible with both theano/tensorflow backends with
        'th' or 'tf' image dim ordering. :func:`~utils.slicer` can be used to define backend agnostic slices
        (just define it for theano, it will automatically shuffle indices for tensorflow).

        :func:`~utils.get_img_shape` and :func:`~utils.get_img_indices` are other optional utilities that make this
        easier.

        Args:
            img: 4D tensor with shape: `(samples, channels, rows, cols)` if dim_ordering='th' or
                `(samples, rows, cols, channels)` if dim_ordering='tf'.

        Returns:
            The loss expression.
        """
        raise NotImplementedError()


class ActivationMaximization(Loss):
    """A loss function that maximizes the activation of a set of filters within a particular layer.

    Typically this loss is used to ask the reverse question - What kind of input image would increase the networks
    confidence, for say, dog class. This helps determine what the network might be internalizing as being the 'dog'
    image space.

    One might also use this to generate an input image that maximizes both 'dog'/'human' outputs on the final
    `Dense` layer.
    """
    def __init__(self, layer, filter_indices):
        """
        Args:
            layer: The keras layer whose filters need to be maximized. This can either be a convolutional layer
                or a dense layer.
            filter_indices: filter indices within the layer to be maximized.
                For `Dense` layers, `filter_idx` is interpreted as the output index.

                If you are optimizing final :class:`~keras.layers.Dense` layer to maximize class output, you tend to get
                better results with 'linear' activation as opposed to 'softmax'. This is because 'softmax'
                output can be maximized by minimizing scores for other classes.
        """
        super(ActivationMaximization, self).__init__()
        self.name = "ActivationMax Loss"
        self.layer = layer
        self.filter_indices = filter_indices

    def build_loss(self, img):
        layer_output = self.layer.output

        # For all other layers it is 4
        is_dense = K.ndim(layer_output) == 2

        loss = 0.
        for idx in self.filter_indices:
            if is_dense:
                loss += -K.mean(layer_output[:, idx])
            else:
                # slicer is used to deal with theano/tensorflow without the ugly conditional statements.
                loss += -K.mean(layer_output[utils.slicer[:, idx, :, :]])

        return loss
