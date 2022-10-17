import pyglet


# if __name__ == "__main__":
#     # create vertices and colors
#     relative_vertices = [[20, 20], [20, -20], [-20, -20], [-20, 20]]
#     num_vertices = len(relative_vertices)
#     vertices1 = []
#     vertices2 = []
#     for v in relative_vertices:
#         vertices1 += [100 + v[0], 100 + v[1]]
#         vertices2 += [300 + v[0], 300 + v[1]]
#     colors1 = [255, 0, 0] * num_vertices
#     colors2 = [0, 255, 0] * num_vertices
#     # create batch and add vertices there
#     batch = pyglet.graphics.Batch()
#     batch.add(num_vertices, pyglet.gl.GL_POLYGON, None, ("v2f", vertices1), ("c3B", colors1))
#     batch.add(num_vertices, pyglet.gl.GL_POLYGON, None, ("v2f", vertices2), ("c3B", colors2))
#     # create window and draw function, and run app
#     window = pyglet.window.Window(400, 400)
#     @window.event
#     def on_draw():
#         window.clear()
#         batch.draw()
#     pyglet.app.run()


# if __name__ == "__main__":
#     # create vertices and colors
#     relative_vertices = [[20, 20], [20, -20], [-20, -20], [-20, 20]]
#     num_vertices = len(relative_vertices)
#     vertices1 = []
#     vertices2 = []
#     for v in relative_vertices:
#         vertices1 += [100 + v[0], 100 + v[1]]
#         vertices2 += [300 + v[0], 300 + v[1]]
#     colors1 = [255, 0, 0] * num_vertices
#     colors2 = [0, 255, 0] * num_vertices
#     # create batch and add vertices there
#     batch = pyglet.graphics.Batch()
#     batch.add(num_vertices, pyglet.gl.GL_POLYGON, None, ("v2f", vertices1), ("c3B", colors1))
#     batch.add(num_vertices, pyglet.gl.GL_POLYGON, None, ("v2f", vertices2), ("c3B", colors2))
#     # create window and draw function, and run app
#     window = pyglet.window.Window(400, 400)
#     @window.event
#     def on_draw():
#         window.clear()
#         batch.draw()
#     pyglet.app.run()


if __name__ == "__main__":
    # create vertices and colors
    relative_vertices = [[20, 20], [20, -20], [-20, -20], [-20, 20]]
    indexs = [0, 1, 2, 3, 2, 1]
    num_vertices = len(relative_vertices)
    vertices1 = []
    vertices2 = []
    for v in relative_vertices:
        vertices1 += [100 + v[0], 100 + v[1]]
        vertices2 += [300 + v[0], 300 + v[1]]
    colors1 = [255, 0, 0] * num_vertices
    colors2 = [0, 255, 0] * num_vertices
    # create batch and add vertices there
    batch = pyglet.graphics.Batch()
    batch.add_indexed(num_vertices, pyglet.gl.GL_TRIANGLES, None, indexs, ("v2f", vertices1), ("c3B", colors1))
    batch.add_indexed(num_vertices, pyglet.gl.GL_TRIANGLES, None, indexs, ("v2f", vertices2), ("c3B", colors2))
    # list1 = pyglet.graphics.vertex_list(num_vertices, ("v2f", vertices1), ("c3B", colors1))
    # list2 = pyglet.graphics.vertex_list(num_vertices, ("v2f", vertices2), ("c3B", colors2))
    # create window and draw function, and run app
    window = pyglet.window.Window(400, 400)
    @window.event
    def on_draw():
        window.clear()
        batch.draw()
        # list1.draw(pyglet.gl.GL_QUADS)
        # list2.draw(pyglet.gl.GL_QUADS)
    pyglet.app.run()
