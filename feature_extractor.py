import commons, constants, numpy as np
import scipy as sp, pandas as pd
from scipy.signal import find_peaks


def write_feature_set(data_sheet, sub_task):
    for task in ['classification']: 
        feature_set = extract_features(data_sheet, task, sub_task)
        # commons.array_to_csv(feature_set, constants.FEATURES_DIR + task + '_'+ sub_task+'_features.csv')
    return feature_set

def simple_moving_average(signal, window_size):
    if window_size % 2 == 0:
        window_size += 1

    signal = np.pad(signal, window_size // 2, mode="edge")
    window = np.ones(window_size) / window_size
    smoothed_signal = np.convolve(signal, window, 'same')
    return smoothed_signal[window_size // 2:-window_size // 2 + 1]


def find_true_peak(signal):
    # Find all peaks
    peaks, _ = find_peaks(signal, width=20, prominence=0.05)
    # Get the true peak (the maximum value)
    if len(peaks) > 0:
        return peaks[np.argmax(signal[peaks])]
    else:
        return np.argmax(signal)


def find_active_point(smoothed_signal, peak_index):
    derivatives = np.gradient(smoothed_signal)
    point_A = 0
    # A: point of continuous rise upto true peak!
    for i in range(peak_index, 0, -1):
        if derivatives[i-1] <= 0.0:  # Look for where rise starts
            point_A = i
            break
    return point_A


def find_decay_point(smoothed_signal, peak_index, decay_duration=20):
    derivatives = np.gradient(smoothed_signal)
    point_C = peak_index
    # The point after true peak when signal decreases for specific duration!
    for j in range(peak_index, len(derivatives) - decay_duration):
        if all(derivatives[j: j + decay_duration] < 0):  # Continuous decay
            point_C = j
            break
    return point_C


def filter_signal(sensor_signal):
    peak_index = find_true_peak(sensor_signal)  # True Peak of the signal!
    point_A = find_active_point(sensor_signal, peak_index)  # Point A (start of continuous rise)
    point_C = find_decay_point(sensor_signal, peak_index)   # Point C (start of continuous decay)
    return sensor_signal[point_A: point_C + 1]

def compute_derivative_features(sample):
    if len(sample) > 1:
        derivative_list = np.gradient(sample)
        s_derivative_list = np.gradient(derivative_list)

        derivative_features = [
            np.max(s_derivative_list), np.min(s_derivative_list), np.mean(s_derivative_list), np.std(s_derivative_list),
            np.max(derivative_list), np.min(derivative_list), np.mean(derivative_list), np.std(derivative_list)
        ]

        return derivative_features
    else:
        return [0] * 8


def compute_integral_features(signal_samples):
    if len(signal_samples) > 1:
        integral = np.trapz(signal_samples)
        squared_integral = np.trapz(np.square(signal_samples))
        return [integral, squared_integral]
    else:
        return [0] * 2


def compute_fft_features(sample):
    if len(sample) > 1:
        length = len(sample)
        fft = sp.fft.fft(sample)

        # Taking only positive frequencies to calculate power spectrum
        # frequencies = sp.fft.fftfreq(length)[:length // 2]
        power_spectrum = np.square(np.abs(fft))[:length // 2]

        # Extract frequency-domain features
        energy = np.mean(power_spectrum)
        power = np.sum(power_spectrum)
        return [energy, power]
    else:
        return [0] * 2


def obtain_spatial_freq_features_sensor_data(signal):
    comb_feature_set = []
    derivative_features = compute_derivative_features(signal)
    integral_features = compute_integral_features(signal)
    fft_features = compute_fft_features(signal)
    comb_feature_set += derivative_features + integral_features + fft_features
    return comb_feature_set


def extract_features(data_sheet, task, sub_task):
    if sub_task == constants.SUB_TASK_TRAIN:
        df = commons.read_data_as_data_frame(data_sheet)
    else:
        df = pd.DataFrame(data_sheet)
    feature_set = []
    total_rows = len(df)
    print(f"Total rows to process: {total_rows}")
    for index, row in df.iterrows():
        row_data = row.tolist()
        feature_vector = []
        smooth_signal = simple_moving_average(signal=row_data, window_size=5)
        smooth_signal = simple_moving_average(signal=smooth_signal, window_size=11)

        # Filtering relevant A-C portion of the signal!
        filtered_signal = filter_signal(smooth_signal)
        # spatial features
        sensor_features = obtain_spatial_freq_features_sensor_data(filtered_signal)
        feature_vector = feature_vector + sensor_features
        feature_set.append(feature_vector)
    print(f"Processed rows: {len(feature_set)}, Expected rows: {total_rows}")
    return feature_set
