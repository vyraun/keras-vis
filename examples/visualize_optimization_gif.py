from utils.vggnet import VGG16
from optimizer import Optimizer
from losses import ActivationMaximization
from regularizers import TotalVariation, LPNorm


def generate_opt_gif():
    """Example to show how to generate the gif of optimization progress.
    """
    # Build the VGG16 network with ImageNet weights
    model = VGG16(weights='imagenet', include_top=True)
    print('Model loaded.')

    # The name of the layer we want to visualize
    # (see model definition in vggnet.py)
    layer_name = 'predictions'
    layer_dict = dict([(layer.name, layer) for layer in model.layers[1:]])
    output_class = [20]

    losses = [
        (ActivationMaximization(layer_dict[layer_name], output_class), 1),
        (LPNorm(), 10),
        (TotalVariation(), 1)
    ]
    opt = Optimizer(model.input, losses)

    # Jitter is used as a regularizer to create crisper images, but it makes gif animation ugly.
    opt.minimize(max_iter=500, verbose=True, jitter=0,
                 progress_gif_path='opt_progress')


if __name__ == '__main__':
    generate_opt_gif()
