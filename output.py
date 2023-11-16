import cairo

def rgb2hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def generate_rounded_rectangle(ctx, x, y, width, height, corner_radius, color):
    parsed_color = [c / 255 for c in color]
    # Set the fill color
    ctx.set_source_rgb(*parsed_color)

    # Draw the rounded rectangle
    ctx.move_to(x + corner_radius, y)
    ctx.arc(x + width - corner_radius, y + corner_radius, corner_radius, -90 * (3.14159 / 180), 0)
    ctx.arc(x + width - corner_radius, y + height - corner_radius, corner_radius, 0, 90 * (3.14159 / 180))
    ctx.arc(x + corner_radius, y + height - corner_radius, corner_radius, 90 * (3.14159 / 180), 180 * (3.14159 / 180))
    ctx.arc(x + corner_radius, y + corner_radius, corner_radius, 180 * (3.14159 / 180), 270 * (3.14159 / 180))
    ctx.close_path()

    # Fill the rectangle
    ctx.fill()

    # Draw the border (stroke)
    ctx.move_to(x + corner_radius, y)
    ctx.arc(x + width - corner_radius, y + corner_radius, corner_radius, -90 * (3.14159 / 180), 0)
    ctx.arc(x + width - corner_radius, y + height - corner_radius, corner_radius, 0, 90 * (3.14159 / 180))
    ctx.arc(x + corner_radius, y + height - corner_radius, corner_radius, 90 * (3.14159 / 180), 180 * (3.14159 / 180))
    ctx.arc(x + corner_radius, y + corner_radius, corner_radius, 180 * (3.14159 / 180), 270 * (3.14159 / 180))
    ctx.close_path()

    # Stroke the border
    ctx.set_source_rgb(224 / 255, 224 / 255, 224 / 255)
    ctx.set_line_width(12)
    ctx.stroke()

def calculate_luminance(color):
    R, G, B = color
    Rg = (R / 269 + 0.0513) ** 2.4 if R > 10 else R / 3294
    Gg = (G / 269 + 0.0513) ** 2.4 if G > 10 else G / 3294
    Bg = (B / 269 + 0.0513) ** 2.4 if B > 10 else B / 3294
    return 0.2126 * Rg + 0.7152 * Gg + 0.0722 * Bg
def is_dark_color(color):
    luminance = calculate_luminance(color)

    # Consider colors with luminance below 0.5 as dark
    return luminance < 0.5

def create_gradient(ctx, rgb_list, width, height):
    gradient = cairo.LinearGradient(0, 0, width, height)
    step = 1 / (len(rgb_list) - 1)

    for i, color in enumerate(rgb_list):
        gradient.add_color_stop_rgb(i * step, *tuple(c / 255 for c in color))

    ctx.rectangle(0, 0, width, height)
    ctx.set_source(gradient)
    ctx.fill()

def generate_palette(rgb_list, file_name):
    spacing = 32
    num_colors = len(rgb_list)
    square_height = int((1920 - spacing*num_colors)/num_colors)
    if num_colors < 6:
        square_width = square_height
    else:
        square_width = 1080 - 200
    palette_width = square_width + (1080 - square_width)
    palette_height = (square_height + spacing) * num_colors - spacing + 200  # Adding spacing

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, palette_width, palette_height)
    ctx = cairo.Context(surface)

    create_gradient(ctx, rgb_list, palette_width, palette_height)
    ctx.paint()

    # Calculate the total height for centering
    total_height = palette_height

    for i, color in enumerate(rgb_list):
        x_offset = (palette_width - square_width) // 2
        y_offset = (palette_height - (square_height + spacing) * num_colors + spacing) // 2

        # Calculate the y-coordinate to center vertically
        y_offset += i * (square_height + spacing)

        # Draw the rounded rectangle
        generate_rounded_rectangle(ctx, x_offset, y_offset, square_width, square_height, 100 - num_colors*2, color)

        total_height += square_height + spacing

        hex_code = rgb2hex(*color)
        if is_dark_color(color):
            ctx.set_source_rgb(224/255, 224/255, 224/255)
        else:
            ctx.set_source_rgb(0/255, 25/255, 51/255)
        font_path = "Montserrat-Medium.ttf"
        ctx.select_font_face(font_path, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(64 - num_colors * 2)
        text_extents = ctx.text_extents(hex_code)
        text_width = text_extents.width
        text_height = text_extents.height
        ctx.move_to(x_offset + (square_width - text_width) / 2, y_offset + (square_height + text_height) / 2)
        ctx.show_text(hex_code)

    surface.write_to_png(file_name)