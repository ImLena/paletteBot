import numpy as np

from model.palette_extractor import PaletteExtractor


class ImageTransformer:
    delta = 50

    def __init__(self, colors):
        self.colors = colors

    def transform(self, image):
        extractor = PaletteExtractor(len(self.colors))
        extractor.fit(image)
        cur_colors = extractor.get_colors()

        mapping = [0 for _ in range(len(cur_colors))]
        for i in range(len(cur_colors)):
            min_dist = 1e9
            for j in range(len(cur_colors)):
                dist = np.sqrt((cur_colors[i][0] - self.colors[j][0]) ** 2
                               + (cur_colors[i][1] - self.colors[j][1]) ** 2
                               + (cur_colors[i][2] - self.colors[j][2]) ** 2)
                if dist < min_dist:
                    min_dist = dist
                    mapping[i] = j

        new_image = [[[x for x in image[i][j]] for j in range(len(image[i]))] for i in range(len(image))]
        for i in range(len(new_image)):
            for j in range(len(new_image[i])):
                for cl in range(len(cur_colors)):
                    dist = np.sqrt((cur_colors[cl][0] - new_image[i][j][0]) ** 2
                                   + (cur_colors[cl][1] - new_image[i][j][1]) ** 2
                                   + (cur_colors[cl][2] - new_image[i][j][2]) ** 2)
                    if dist < self.delta:
                        new_image[i][j][0] += (self.colors[mapping[cl]][0] - cur_colors[cl][0])
                        new_image[i][j][1] += (self.colors[mapping[cl]][1] - cur_colors[cl][1])
                        new_image[i][j][2] += (self.colors[mapping[cl]][2] - cur_colors[cl][2])
                        new_image[i][j][0] = min(255, max(0, new_image[i][j][0]))
                        new_image[i][j][1] = min(255, max(0, new_image[i][j][1]))
                        new_image[i][j][2] = min(255, max(0, new_image[i][j][2]))
        return new_image
