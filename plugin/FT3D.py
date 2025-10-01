from krita import *
from PyQt5.QtWidgets import QMessageBox
import cmath
import math

class FourierTransformPlugin(Extension):
    x_coords = []
    y_coords = []

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        self.action = window.createAction("fourier_transform_3d", "Fourier Transform 3D", "tools/scripts")
        self.action.triggered.connect(self.apply_fourier_transform)

    def apply_fourier_transform(self):
        """
        Apply the Fourier Transform to the active document's layers.
        """
        # Clear the previous results
        self.x_coords.clear()
        self.y_coords.clear()

        doc = Krita.instance().activeDocument()
        if not doc:
            QMessageBox.critical(None, "Error", "No active document.")
            return

        nodes = doc.rootNode().childNodes()
        if not nodes:
            QMessageBox.critical(None, "Error", "No layers found.")
            return

        volume_data = self.nodes_to_grayscale(nodes)
        if volume_data is None:
            return

        num_slices = len(nodes)
        for i in range(num_slices):
            group_node = doc.createGroupLayer(f"Slice_{num_slices - i - 1}")
            doc.rootNode().addChildNode(group_node, None)

        # Compute the Fourier Transform, phase, and power spectrum
        combined, magnitude, phase, power = self.compute_dft_3d(volume_data)
        combined, magnitude, phase, power = self.normalize(combined, 0.5), self.normalize(magnitude, 0.2), self.normalize(phase, 1), self.normalize(power, 0.2)

        # Display the results
        self.show_result_3d(magnitude, "Magnitude Spectrum")
        self.show_result_3d(phase, "Phase Spectrum")
        self.show_result_3d(power, "Power Spectrum")
        self.show_result_3d(combined, "Combined Spectrum")

    def nodes_to_grayscale(self, nodes):
        """
        Convert a list of RGB images to Grayscale.
        """
        try:
            depth = len(nodes)
            volume = []
            width = 0
            height = 0
            if nodes:
                width_check = nodes[0].bounds().width()
                height_check = nodes[0].bounds().height()
            
            for node in nodes:

                bounds = node.bounds()

                if bounds.width()>128 or bounds.height() > 128:
                    QMessageBox.critical(None, "Error", "One or more images are too large. Maximum size is 128x128.")
                    return None

                x, y, width, height = bounds.x(), bounds.y(), bounds.width(), bounds.height()
                self.x_coords.append(x)
                self.y_coords.append(y)

                if width != width_check or height != height_check:
                    QMessageBox.critical(None, "Error", "All images must have the same dimensions.")
                    return None

                # Get the pixel data
                pixel_data = node.pixelData(x, y, width, height)
                if not pixel_data:
                    QMessageBox.critical(None, "Error", "Failed to get pixel data.")
                    return None

                # Convert pixel data to a mutable bytearray
                pixels = bytearray(pixel_data)

                # Convert pixel data to a 2D grayscale list
                grayscale_image = []
                for y in range(height):
                    row = []
                    for x in range(width):
                        offset = (y * width + x) * 4
                        r = pixels[offset]
                        g = pixels[offset + 1]
                        b = pixels[offset + 2]
                        gray = int(0.299 * r + 0.587 * g + 0.114 * b)  # Grayscale conversion formula
                        row.append(gray)
                    grayscale_image.append(row)
                volume.append(grayscale_image)

            return volume

        except Exception as e:
            print("Error converting node to grayscale:", e)
            return None

    def compute_dft_3d(self, volume):
        """
        Compute the 3D Discrete Fourier Transform of the volume.
        """

        depth = len(volume)
        height = len(volume[0])
        width = len(volume[0][0])

        combined = []
        magnitude = []
        phase = []
        power = []


        for k in range(depth):

            # Initialize the current slice's results
            magnitude_slice = [[0 for _ in range(width)] for _ in range(height)]
            phase_slice = [[0 for _ in range(width)] for _ in range(height)]
            power_slice = [[0 for _ in range(width)] for _ in range(height)]

            for u in range(height):
                for v in range(width):
                    sum_val = 0
                    for y in range(height):
                        for x in range(width):
                            for z in range(depth):
                                # Compute the sum of the volume with DFT formula
                                angle = -2j * cmath.pi * ((u * y / height) + (v * x / width) + (k * z / depth))
                                sum_val += volume[z][y][x] * cmath.exp(angle)

                    magnitude_slice[u][v] = abs(sum_val)
                    phase_slice[u][v] = cmath.phase(sum_val)
                    power_slice[u][v] = abs(sum_val) ** 2

            # Logarithmic scaling for better visualization
            magnitude_slice = [[math.log(1 + val) for val in row] for row in magnitude_slice]
            power_slice = [[math.log(1 + val) for val in row] for row in power_slice]

            # Shift and append the processed slice to the results
            magnitude.append(self.shift_dft_2d(magnitude_slice))
            phase.append(self.shift_dft_2d(phase_slice))
            power.append(self.shift_dft_2d(power_slice))
            combined.append(self.shift_dft_2d(self.combine_magnitude_phase(magnitude_slice, phase_slice)))

        return combined, magnitude, phase, power

    def shift_dft_2d(self, data):
        """
        Shift the zero-frequency component to the center of the image.
        """
        height = len(data)
        width = len(data[0])
        half_height = height // 2
        half_width = width // 2

        # Swap quadrants
        shifted = [[0 for _ in range(width)] for _ in range(height)]
        for y in range(height):
            for x in range(width):
                new_y = (y + half_height) % height
                new_x = (x + half_width) % width
                shifted[new_y][new_x] = data[y][x]
        
        return shifted

    def combine_magnitude_phase(self, magnitude, phase):
        """
        Combine magnitude and phase into a single grayscale image.
        """
        height = len(magnitude)
        width = len(magnitude[0])

        # Normalize the magnitude to [0, 1]
        max_magnitude = max(max(row) for row in magnitude)
        normalized_magnitude = [[val / max_magnitude for val in row] for row in magnitude]

        # Create a grayscale image (2D list)
        grayscale_image = [[0 for _ in range(width)] for _ in range(height)]

        for y in range(height):
            for x in range(width):
                # Normalize the phase to a value between 0 and 1
                phase_normalized = (phase[y][x] + math.pi) / (2 * math.pi)  # Normalize phase to [0, 1]

                # Combine magnitude and phase. Use magnitude for brightness and phase for modulation.
                # Example formula: Adjust brightness based on phase to add some variation.
                brightness = normalized_magnitude[y][x] * (1 + 0.5 * phase_normalized)  # Influence of phase on brightness

                # Clamp brightness to [0, 1]
                brightness = max(0, min(brightness, 1))

                # Scale brightness to [0, 255]
                grayscale_image[y][x] = int(brightness * 255 * 0.5)

        return grayscale_image

    def normalize(self, data, gamma):
        """
        Normalize the data to the range [0, 255] and scale by gamma.
        """
        # Flatten the 3D data to find the global min and max
        flattened = [val for layer in data for row in layer for val in row]
        min_val = min(flattened)
        max_val = max(flattened)

        if min_val == max_val:
            # Return all-zero data if there's no range
            return [[[0 for _ in row] for row in layer] for layer in data]

        # Compute the scaling factor
        scale = 255 / (max_val - min_val)

        # Apply normalization to each value
        return [[[int((val - min_val) * scale * gamma) for val in row] for row in layer] for layer in data]

    def show_result_3d(self, result, title):
        """
        Display the 3D result in Krita.
        """
        for i, slice_ in enumerate(result):
            self.show_result(slice_, f"{title}_{i}", i)

    def show_result(self, result, title, index):
        """
        Display the result in Krita.
        """
        try:
            # Get the active document
            doc = Krita.instance().activeDocument()
            if not doc:
                QMessageBox.critical(None, "Error", "No active document found.")
                return

            # Get dimensions
            height = len(result)
            width = len(result[0])

            # Create a new paint layer
            new_node = doc.createNode(title, "paintlayer")

            # Find or create a group layer for the result
            group_node = self.find_group_by_name(doc.rootNode(), f"Slice_{len(self.x_coords) - index - 1}")
            if group_node is None:
                group_node = doc.createGroupLayer(f"Slice_{len(self.x_coords) - index - 1}")
                doc.rootNode().addChildNode(group_node, None)

            # Convert normalized data to bytearray for Krita
            pixel_data = bytearray()
            for row in result:
                for px in row:
                    pixel_data.extend([int(px), int(px), int(px), 255])

            # Set the pixel data to the new layer
            new_node.setPixelData(bytes(pixel_data), self.x_coords[index], self.y_coords[index], width, height)

            # Add the new layer to the group
            group_node.addChildNode(new_node, None)

        except Exception as e:
            QMessageBox.critical(None, "Error", str(e))
    
    def find_group_by_name(self, parent_node, group_name):
        """
        Search for a group layer with the specified name under the given parent node.
        Returns the group node if found, otherwise returns None.
        """
        for node in parent_node.childNodes():
            if node.name() == group_name and node.type() == "grouplayer":
                return node
        return None


# Register the plug-in
Krita.instance().addExtension(FourierTransformPlugin(Krita.instance()))
