import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

from sklearn.model_selection import KFold
from sklearn.metrics import precision_recall_fscore_support, f1_score
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split

import torch
import torch.nn as nn
import torch.optim as optim

from models import NN

import sys, random


def construct_mapping(df, column_name, delimiter):
    result_dict = {}
    for ind, row in df.iterrows():
        cur_attrs = row[column_name].split(delimiter)

        for attr in cur_attrs:
            if attr not in result_dict.keys():
                result_dict[attr] = len(result_dict.keys())
    return result_dict

def inverse_dict(input_dict):
    inverse_dict = {}
    for k in input_dict.keys():
        inverse_dict[input_dict[k]] = k
    return inverse_dict




""" Plot correlation map: 141 categories V.S. 4 targets. """

def main():

    # initialize
    PLOT_MAP = True
    COR_THRESHOLD = 0.04

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', -1)

    # read training data
    df = pd.read_csv('../data/task2_trainset.csv')
    df_columns = df.columns

    # read predicting data
    predict_df = pd.read_csv('../data/task2_public_testset.csv')
    print(predict_df.shape)

    # test - construct category & label dict
    category_dict = construct_mapping(df, 'Categories', '/')
    inverse_category_dict = inverse_dict(category_dict)
    label_dict = construct_mapping(df, 'Task 2', ' ')
    inverse_label_dict = inverse_dict(label_dict)
    print(category_dict)
    print(label_dict)


    # construct one-hot training data
    category_list = []
    label_list = []

    for ind, row in df.iterrows():
        categories = row['Categories'].split('/')
        targets = row['Task 2'].split(' ')

        cur_categories = [category_dict[x] for x in categories]
        cur_targets = [label_dict[x] for x in targets]

        category_list.append(cur_categories.copy())
        label_list.append(cur_targets.copy())

    combined_onehot_train = []
    for i in range(len(category_list)):
        new_category_list = [0 for x in range(len(category_dict.keys()))]
        new_target_list = [0 for x in range(len(label_dict.keys()))]
        for category_ind in category_list[i]:
            new_category_list[category_ind] = 1
        for target_ind in label_list[i]:
            new_target_list[target_ind] = 1
        combined_onehot_train.append(new_category_list.copy() + new_target_list.copy())

    # convert training data into pandas dataframe
    df_column_names = [ inverse_category_dict[x] for x in sorted(inverse_category_dict.keys()) ] + [ inverse_label_dict[x] for x in sorted(inverse_label_dict.keys()) ]
    df = pd.DataFrame(combined_onehot_train, columns=df_column_names)
    print(df.shape)


    # construct one-hot predicting data
    category_list = []
    id_list = []

    for ind, row in predict_df.iterrows():
        categories = row['Categories'].split('/')
        cur_categories = [category_dict[x] for x in categories if x in category_dict.keys()]
        category_list.append(cur_categories.copy())
        id_list.append(row['Id'])

    assert len(id_list) == len(category_list)

    combined_onehot_predict = []
    for i in range(len(category_list)):
        new_category_list = [0 for x in range(len(category_dict.keys()))]
        for category_ind in category_list[i]:
            new_category_list[category_ind] = 1
        combined_onehot_predict.append( [id_list[i]] + new_category_list.copy() + [0 for x in range(len(label_dict.keys()))] )

    # convert predicting data into pandas dataframe
    df_column_names = ['order_id'] + [ inverse_category_dict[x] for x in sorted(inverse_category_dict.keys()) ] + [ inverse_label_dict[x] for x in sorted(inverse_label_dict.keys()) ]
    predict_df = pd.DataFrame(combined_onehot_predict, columns=df_column_names)
    print(predict_df.shape)




    # Compute the correlation matrix of training data
    corr = df.corr()


    # Generate a custom diverging colormap
    if PLOT_MAP:
        sns.set()
        cmap = sns.diverging_palette(220, 10, as_cmap=True)
        sns.heatmap(corr[[ x for x in label_dict.keys() ]], cmap=cmap, vmax=.6, center=0, square=True, linewidths=0)
        plt.title('Correlations between categories & labels')
        plt.show()


    # filter out categories with corresponding correlation values which don't exceed threshold value
    print('Current correlation threshold: %.3f' % COR_THRESHOLD)
    corr = corr[[ inverse_category_dict[x] for x in sorted(inverse_category_dict.keys()) ]][-1*len(label_dict.keys()):]

    valid_col_name_list = []
    invalid_col_name_list = []
    for column in corr:
        is_above_threshold = True
        if (corr[column] > COR_THRESHOLD).any() or (corr[column] < -1*COR_THRESHOLD).any():
            valid_col_name_list.append(column)
        else:
            invalid_col_name_list.append(column)
        

    # Generate a custom diverging colormap
    if PLOT_MAP:
        sns.set()
        cmap = sns.diverging_palette(220, 10, as_cmap=True)

        sns.heatmap(corr[valid_col_name_list], cmap=cmap, vmax=.6, center=0, square=True, linewidths=0)
        plt.title('Correlations between categories with high correlations & labels')
        plt.show()

        sns.heatmap(corr[invalid_col_name_list], cmap=cmap, vmax=.6, center=0, square=True, linewidths=0)
        plt.title('Correlations between categories with low correlations & labels')
        plt.show()


    # training data
    target_col_name_list = [ inverse_label_dict[x] for x in sorted(inverse_label_dict.keys()) ]
    data_x = df[valid_col_name_list]
    data_y = df[target_col_name_list]

    print(data_x.shape)
    print(data_y.shape)

    train_x, test_x, train_y, test_y = train_test_split(data_x, data_y, test_size=0.1)


    # predicting data
    predict_x = predict_df[valid_col_name_list]
    print(predict_x.shape)

    return

if __name__ == '__main__':
    main()
