import json


class Gaze2Fixation:
    def __init__(self):
        pass
    
    @staticmethod
    def _calculate_dispersion(gaze_points):
        """Calculate the dispersion of a set of gaze points."""
        x_coords, y_coords = zip(*gaze_points)
        max_x, min_x = max(x_coords), min(x_coords)
        max_y, min_y = max(y_coords), min(y_coords)
        dispersion = max(max_x - min_x, max_y - min_y)
        return dispersion
    
    @staticmethod
    def simpleDispersionBased(gaze_data, max_dispersion=40, min_duration=20, max_duration=2000):
        """Detect fixations in the gaze data based on dispersion and duration.
        输入格式：gaze_data = [(x, y, timestamp), ...]，其中timestamp是毫秒级的时间戳
        返回值： [(start, end, duration, start_time, end_time), ...]
        TODO: 增加一个鲁棒的设置，在计算fixation时是否考虑某个gaze point的合法性
        """
        fixations = []
        start = 0

        while start < len(gaze_data):
            end = start
            while end < len(gaze_data):
                current_dispersion = Gaze2Fixation._calculate_dispersion([point[:2] for point in gaze_data[start:end+1]])
                if current_dispersion > max_dispersion:
                    break
                end += 1
            # Check if the duration of potential fixation is within the duration thresholds
            if end - start >= min_duration and end - start <= max_duration:
                fixation_duration = gaze_data[end-1][2] - gaze_data[start][2]
                fixations.append((start, end-1, fixation_duration, gaze_data[start][2], gaze_data[end-1][2]))
                start = end
            else:
                start += 1
        return fixations