def grid_pos_to_render_pos(grid_pos):
    x, y = grid_pos
    return x * 16, y * 16


def render_pos_to_grid_pos(render_pos):
    x, y = render_pos
    return x / 16, y / 16
