import pyglet


def center_image(image):
    """Sets an image's anchor point to its center."""
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2


def import_and_center_image(filename):
    """Import images and set ancor point to center."""
    image = pyglet.resource.image(filename)
    center_image(image)
    return image

# let pyglet manage resources path
pyglet.resource.path = ["../resources"]
pyglet.resource.reindex()

# import images
player_image = import_and_center_image("spaceship.png")
engine_image = import_and_center_image("flame.png")
bullet_image = import_and_center_image("missile.png")
asteroid_image = import_and_center_image("asteroid.png")
