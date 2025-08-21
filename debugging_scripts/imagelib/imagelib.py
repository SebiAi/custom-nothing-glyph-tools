# imagelib - A library for basic image manipulation and processing.
# Copyright (C) 2025  Sebastian Aigner (aka. SebiAi)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

class Pixel:
    def __init__(self, r, g, b):
        """Initializes a Pixel object with RGB values.
        Args:
            r (int): Red component (0-255).
            g (int): Green component (0-255).
            b (int): Blue component (0-255).
        """
        assert 0 <= r <= 255, "Red value must be between 0 and 255"
        assert 0 <= g <= 255, "Green value must be between 0 and 255"
        assert 0 <= b <= 255, "Blue value must be between 0 and 255"

        self.r: int = r
        self.g: int = g
        self.b: int = b

    def copy(self) -> 'Pixel':
        """Returns a copy of the Pixel object."""
        return Pixel(self.r, self.g, self.b)

class Image:
    def __init__(self, width, height, data = None):
        """Initializes an Image object with specified width, height, and pixel data.
        Args:
            width (int): The width of the image.
            height (int): The height of the image.
            data (list): A list of pixel values in RGB format, where each pixel is represented by three integers (R, G, B).
        """

        if data is None:
            data = [0] * (width * height * 3)

        assert isinstance(width, int) and width > 0, "Width must be a positive integer"
        assert isinstance(height, int) and height > 0, "Height must be a positive integer"
        assert isinstance(data, list), "Data must be a list"
        assert all(isinstance(pixel, int) for pixel in data), "All pixels in data must be integers"
        assert all(0 <= pixel <= 255 for pixel in data), "All pixel values must be between 0 and 255"
        assert len(data) == width * height * 3, "Data length does not have required length (width * height * 3 - RGB values)"

        self.width: int = width
        self.height: int = height
        self.data: list[int] = data
    
    def get_pixel(self, x, y) -> Pixel:
        """Returns the pixel at the specified (x, y) coordinates.
        Args:
            x (int): The x-coordinate of the pixel.
            y (int): The y-coordinate of the pixel.
        Returns:
            Pixel: The pixel at the specified coordinates.
        """
        assert 0 <= x < self.width, "X coordinate out of bounds"
        assert 0 <= y < self.height, "Y coordinate out of bounds"

        index: int = (y * self.width + x) * 3  # Each pixel has 3 values (R, G, B)
        pixel: Pixel = Pixel(self.data[index], self.data[index + 1], self.data[index + 2])

        return pixel
    
    def set_pixel(self, x, y, pixel: Pixel):
        """Sets the pixel at the specified (x, y) coordinates to the given Pixel object.
        Args:
            x (int): The x-coordinate of the pixel.
            y (int): The y-coordinate of the pixel.
            pixel (Pixel): The Pixel object to set at the specified coordinates.
        """
        assert 0 <= x < self.width, "X coordinate out of bounds"
        assert 0 <= y < self.height, "Y coordinate out of bounds"
        assert isinstance(pixel, Pixel), "Pixel must be an instance of Pixel class"

        index: int = (y * self.width + x) * 3
        self.data[index] = pixel.r
        self.data[index + 1] = pixel.g
        self.data[index + 2] = pixel.b
        
    def set_pixels_at(self, x: int, y: int, image: 'Image'):
        """Sets multiple pixels starting at the specified (x, y) top left coordinates.
        Args:
            x (int): The x-coordinate to start setting pixels.
            y (int): The y-coordinate to start setting pixels.
            image (Image): The image to place.
        """
        assert isinstance(image, Image), "Pixels must be an instance of Image class"

        for ix in range(image.width):
            for iy in range(image.height):
                if 0 <= (x + ix) < self.width and 0 <= (y + iy) < self.height:
                    pixel = image.get_pixel(ix, iy)
                    self.set_pixel(x + ix, y + iy, pixel)
    
    def save_as_ppm(self, filename: str):
        """Saves the image as a PPM file.
        Args:
            filename (str): The name of the file to save the image as. Can also include a path.
        """

        if not filename.endswith('.ppm'):
            filename += '.ppm'

        with open(filename, 'w') as f:
            f.write(f"P3\n{self.width} {self.height} 255\n")
            for y in range(self.height):
                row_values = [self.get_pixel(x, y) for x in range(self.width)]
                row_values_str = ' '.join(f"{pixel.r} {pixel.g} {pixel.b}" for pixel in row_values)
                f.write(row_values_str + '\n')
    
    def scaled(self, scale: int) -> 'Image':
        """Returns a new Image object that is scaled by the given factor.
        Args:
            scale (int): The scaling factor.
        Returns:
            Image: A new Image object with the scaled dimensions and pixel data.
        """
        assert isinstance(scale, int) and scale > 0, "Scale must be a positive integer"

        new_width = self.width * scale
        new_height = self.height * scale
        new_data = [0] * (new_width * new_height * 3)

        for y in range(self.height):
            for x in range(self.width):
                pixel = self.get_pixel(x, y)
                for dy in range(scale):
                    for dx in range(scale):
                        new_x = x * scale + dx
                        new_y = y * scale + dy
                        if 0 <= new_x < new_width and 0 <= new_y < new_height:
                            index = (new_y * new_width + new_x) * 3
                            new_data[index] = pixel.r
                            new_data[index + 1] = pixel.g
                            new_data[index + 2] = pixel.b

        return Image(new_width, new_height, new_data)