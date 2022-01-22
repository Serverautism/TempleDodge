# this .py file hold some general functions to use by every other object
# transform the index of the rocks to the actual position
def grid_pos_to_render_pos(grid_pos):
    x, y = grid_pos
    return x * 16, y * 16


# transform the position of the rocks back to an index
def render_pos_to_grid_pos(render_pos):
    x, y = render_pos
    return x / 16, y / 16


# transform the position on the render surface to the position on the scaled screen surface
def render_pos_to_screen_pos(render_pos, screen_dimensions):
    x = screen_dimensions[0] * render_pos[0] / 512
    y = screen_dimensions[1] * render_pos[1] / 288
    return x, y
