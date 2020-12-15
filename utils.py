import pickle 
import os.path as path
import sys
import os
import codecs
import numpy as np
import math
from datetime import datetime
import time


def save_predictions(best_preds, best_lb, path):
    tmp = "preds,labels\n"
    for x, y in zip(best_preds, best_lb):
        tmp += "%i,%i\n" % (x, y)
    save_file(path, tmp, False)


def validate_path(name):
    paths = name.split("/")
    paths = paths[:-1]
    tmp = ""
    if paths:
        for e, folder in enumerate(paths):
            if folder:
                tmp += folder
                if not path.exists(tmp):
                    os.makedirs(tmp)
                tmp += "/"


def save_file(name, obj, use_pickle=True):
    validate_path(name)
    with open(name, 'wb') as f:
        if use_pickle:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
        else: 
            f.write(obj)


def save_file_utf8(name, obj):
    with codecs.open(name, "w", "utf-8") as file:
        file.write(u'%s' % obj)


def array_to_str(obj, delimiter="\n"):
    tmp = ""
    l = len(obj) - 1
    for i, x in enumerate(obj):
        tmp += str(x)
        if i < l:
            tmp += delimiter
    return tmp


def load_file(pathfile, use_pickle=True):
    if path.exists(pathfile):
        if use_pickle:
            with open(pathfile, 'rb') as f:
                data = pickle.load(f)
        else:
            with open(pathfile, 'r') as file:
                data = file.readlines()
        return data 


def load_file_utf8(pathfile):
    if path.exists(pathfile):
        with codecs.open(pathfile, "r", "utf-8") as file:
            data = file.readlines()
        return data 


def check_file(pathfile):
    return path.exists(pathfile)


def assert_url(url):
    if not check_file(url):
        raise ValueError("%s is not existed" % url)


def intersect(c1, c2):
    return list(set(c1).intersection(c2))


def sub(c1, c2):
    return list(set(c1)- set(c2))


def update_progress(progress, sleep=0.01, barLength=20):
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, status)
    sys.stdout.write(text)
    sys.stdout.flush()
    time.sleep(sleep)


def calculate_accuracy(pred, pred_labels, rng, is_classify):
    accuracy = 0
    if is_classify:
        accuracy = np.sum([1 for x, y in zip(pred, pred_labels) if x == y])
    else:
        accuracy = np.sum([1 for x, y in zip(pred, pred_labels) if abs(x - y) <= rng])
        # print([(x, y) for x, y in zip(pred, pred_labels) if abs(round(x) - round(y)) <= rng])
    return accuracy


def get_pm25_class(index):
    cl = 0
    if index <= 50:
        cl = 0
    elif index > 50 and index <= 100:
        cl = 1
    elif index > 100 and index <= 150:
        cl = 2
    elif index > 150 and index <= 200:
        cl = 3
    elif index > 200 and index <= 300:
        cl = 4
    else:
        cl = 5
    return cl


# pre-process data for training 
# convert 1-d data to grid-data
def process_data_grid(dtlength, batch_size, encoder_length, decoder_length=None, is_test=False, ratio=1.0):
    # ma = heatmap.build_map()
    # maximum = (dtlength - encoder_length - decoder_length) // batch_size * batch_size
    maximum = dtlength - encoder_length - decoder_length
    # end = maximum + encoder_length + decoder_length
    # random from 0 -> maximum_index to separate valid & train set
    indices = np.asarray(range(maximum), dtype=np.int32)
    if not is_test:
        train_length = int((maximum * ratio) // batch_size * batch_size)
        r = np.random.permutation(maximum)
        indices = indices[r]
        train = indices[:train_length]
        if ratio != 1.0:
            valid = indices[train_length:]
        else:
            valid = None
    else:
        if ratio != 1.0:
            train_length = int((maximum * ratio) // batch_size * batch_size)
            train = indices[:train_length]
            valid = indices[train_length:]
        else:
            train, valid = indices, None
    return train, valid


"""
Process china grid training & testing data
20 days each month for train, 10 days each month for test
"""
def process_data_china(dtlength, encoder_length, decoder_length):
    indices = np.asarray(range(dtlength), dtype=np.int32)
    train_, valid_ = [], []
    for x in range(12):
        st = x * 720
        train = indices[st:st+480 - encoder_length - decoder_length].tolist()
        valid = indices[st+480:st+720 - encoder_length -  decoder_length].tolist()
        train_ += train
        valid_ += valid
    return np.array(train_), np.array(valid_)


# pre-process data to batch
def process_data(dataset, data_len, pred, batch_size, max_input_len, max_sent, 
                is_test=False, pred_sight=1, is_classify=False, context_meaning=1, fr_ele = 7):
    len_dataset = len(dataset)
    dlength = len_dataset - 1
    # total batch
    dlength_b = len_dataset // batch_size
    maximum = dlength_b * batch_size
    # dataset = dataset[:-1]
    # if data_len:
    #     data_len = data_len[:-1]
    new_data = []
    new_data_len = []
    new_pred = []
    decode_vec = []
    if not context_meaning:
        zeros = np.zeros(fr_ele).tolist()
    for x in range(maximum):
        e = x + max_sent
        p_i = e + pred_sight - 1
        d_e = p_i + 1
        if e <= dlength and d_e <= len_dataset:
            arr = dataset[x : e]
            # if input len is  like a sentence            
            if data_len:
                arr_l = data_len[x : e]
                new_data_len.append(arr_l)
                arr_d =[y[0][fr_ele:] for y in dataset[e : d_e]]
            else:
                arr_d =[y[fr_ele:] for y in dataset[e : d_e]]
                if not context_meaning:
                    arr = [zeros + en_c[fr_ele:] for en_c in arr]
            # append vector to matrix
            new_data.append(arr)
            new_pred.append(pred[p_i])
            decode_vec.append(arr_d)
        else:
            break
    # print(np.shape(decode_vec))
    if not is_test:
        nl = len(new_data)
        new_data, new_pred, decode_vec = np.asarray(new_data, dtype=np.float32), np.asarray(new_pred, dtype=np.int32), np.asarray(decode_vec, dtype=np.float32)
        train_len = int(nl * 0.8) 
        # permutation to balance distribution
        r = np.random.permutation(nl)
        new_data, new_pred, decode_vec = new_data[r], new_pred[r], decode_vec[r]
        # training set = 80% of dataset
        train_data = new_data[:train_len]
        train_pred = new_pred[:train_len]
        train_dec = decode_vec[:train_len]
        # generate validate set 20% of dataset
        valid_data = new_data[train_len:]
        valid_pred = new_pred[train_len:]
        valid_dec = decode_vec[train_len:]        
        if data_len:
            new_data_len = np.asarray(new_data_len, dtype=np.int32)
            new_data_len = new_data_len[r]
            train_data_len = new_data_len[:train_len]
            valid_data_len = new_data_len[train_len:]
        else: 
            train_data_len, valid_data_len = None, None
        train = (train_data, train_data_len, train_pred, train_dec)
        dev = (valid_data, valid_data_len, valid_pred, valid_dec)
    else:
        train = None
        dev = (new_data, new_data_len, new_pred, decode_vec)
    return train, dev


def now_timestamp():
    return time.mktime(time.localtime())


def now_milliseconds():
    return int(time.time() * 1000)


def get_datetime_now():
    return datetime.fromtimestamp(now_timestamp())


def get_timestamp(dt):
    return time.mktime(dt.timetuple())


# format hour, day < 10 to 10 format
def format10(no):
    if no < 10:
        return "0" + str(no)
    else:
        return str(no)


def boost_pm25(d1):
    # if d1 > 40:
    #     d1 += 10
    # el
    # if d1 > 90:
    #     d1 += 10
    if d1 > 180:
        d1 += 20
    return d1
 

# change datetime str to filename format
def clear_datetime(dt):
    tmp = ""
    for x in dt:
        if x == "-" or x == ":":
            tmp += "."
        elif x == " ":
            tmp += "_"
        else:
            tmp += x
    return tmp


def normalize(v, h, l):
    n = 0.0
    if v >= h:
        n = 1.0
    elif v <= l:
        n = 0.0
    else:
        n = (v - l) / (h - l)
    return n


def std_normalize(v, m, s):
    return (v - m) / s