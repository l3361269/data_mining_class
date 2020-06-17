#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd

def get_candidate(frequent_itemset,n):
    """
    Get the candidate n-itemsets given frequent (n-1)-itemsets.
    
    Args:    
        frequent_itemset: frequent (n-1)-itemsets, datatype:list   
        n: the size of candidate itemset.  datatye:int
        
    Return:  
        candidate_n: The candidate n-itemsets. datatype:list  
    """
    candidate_n=[]
    for i in range(len(frequent_itemset)):
        for j in range(i,len(frequent_itemset)):
            temp=(set(frequent_itemset[i])|set(frequent_itemset[j]))
            if len(temp-set(frequent_itemset[i]))==1:
                #print(temp)
                IN=True
                for t in temp:
                    #print(list(temp-{t}))
                    temp_=list(temp-{t})
                    temp_.sort()
                    #print('temp_:',temp_)
                    if temp_ not in frequent_itemset:
                        #print('not in')
                        IN=False
                        break
                if IN:
                    temp=list(temp)
                    temp.sort()
                    #print('temp:',temp)
                    if temp not in candidate_n:
                        candidate_n.append(temp)
    return candidate_n

def apriori(item_id,transaction_database,min_support):
    """
    Apriori algorithm
    
    Args:
        item_id: every item in every transaction database. datatype:list
        transaction_database:transaction records. datatype:list   
        min_support: minimum support. datatype:int
        
    Return:  
        L_k: all frequent itemsets. datatyoe:list
        L_sup: all support count of frequent itemsets. datatype:list
        num_C: the number of candidate itemsets. datatype:list
        k_C: the size of candidate itemset. datatype:list
        num_L: the number of frequent itemsets. datatype:list
        k_L: the size of frequent itemset. datatype:list 
    """
    #1-itemsets
    item_set=list(set(item_id))
    candidate_one=[]
    candidate_one_fre=np.zeros(len(item_set),dtype=int)
    for i in range(len(item_set)):
        candidate_one.append(item_set[i])
        candidate_one_fre[i]+=item_id.count(item_set[i])
    
    #minsup
    min_sup=min_support
    min_supcount=int(min_sup*len(transaction_database))
    
    #L1
    frequent_itemsets_one=[]
    frequent_one_sup=[]
    for f_i in range(len(candidate_one_fre)):
        if candidate_one_fre[f_i]>=min_supcount:
            frequent_itemsets_one.append([candidate_one[f_i]])
            frequent_one_sup.append(candidate_one_fre[f_i])
    
    L_k=[]
    L_sup=[]
    num_C=[]
    k_C=[]
    num_L=[]
    k_L=[]
    L_k.append(frequent_itemsets_one)
    L_sup.append(frequent_one_sup)
    num_C.append(len(candidate_one))
    k_C.append(1)
    num_L.append(len(frequent_itemsets_one))
    k_L.append(len(frequent_itemsets_one[0]))
    candidate_n=candidate_one[:]
    frequent_itemsets_n=frequent_itemsets_one[:]
    n=2
    while len(frequent_itemsets_n)>0:
        frequent_itemsets_n_1=frequent_itemsets_n[:]
        print('Size of set of large itemsets L({}):'.format(n-1),len(frequent_itemsets_n))
        candidate_n=get_candidate(frequent_itemsets_n_1,n)
        n+=1
        
        # Ck support: scanning transaction DB
        candidate_n_fre=np.zeros(len(candidate_n),dtype=int)
        for c_i in range(len(candidate_n)):
            for trans in transaction_database:
                for c in candidate_n[c_i]:    
                    IN=False
                    if c in trans:
                        IN=True
                    else:
                        IN=False
                        break
                if IN:
                    candidate_n_fre[c_i]+=1
        #pruning
        frequent_itemsets_n=[]
        frequent_itemsets_sup=[]
        for c_ in range(len(candidate_n)):
            if candidate_n_fre[c_]>=min_supcount:
                frequent_itemsets_n.append(candidate_n[c_])
                frequent_itemsets_sup.append(candidate_n_fre[c_])
        if len(frequent_itemsets_n)>0:
            L_k.append(frequent_itemsets_n)
            L_sup.append(frequent_itemsets_sup)
            num_C.append(len(candidate_n))
            k_C.append(len(candidate_n[0]))
            num_L.append(len(frequent_itemsets_n))
            k_L.append(len(frequent_itemsets_n[0]))
        
    
    return L_k,L_sup,num_C,k_C,num_L,k_L


def L_flatten(L_k_supi,L_sup_supi):
    """
    flatten the nested list
    
    arg:
        L_k_supi: frequent itemsets with different min support.
        L_sup_supi: support count of frequent itemsets with different min support.
    
    return:
        L_i: frequent itemsets of that min support.
        L_s: support count of frequent itemsets of that min support.
    """
    L_i=[]
    L_s=[]
    
    for lki in range(len(L_k_supi)):
        L_i.extend(L_k_supi[lki])
        L_s.extend(L_sup_supi[lki])
        #for mi in range(len(L_k_supi[lki])):
            #L_i.append(L_k_supi[lki][mi])
            #L_s.append(L_sup_supi[lki][mi])
    return L_i,L_s


def get_rule(m,p,prun,L_i,L_s,min_conf,rule):
    """
    get the rules from that frequent itemset.
    
    arg:
        m: one frequent itemset
        p: subset of that one frequent itemset
        prun: return prun subsets
        L_i: frequent itemsets of that min support
        L_s: support count of frequent itemsets of that min support
        min_conf: minimum confidence
        rule: return rule list
    
    return:
        rule: rule list of that one frequent itemset
        prun: prun subsets
        
    """
    m_=m
    sup_m=L_s[L_i.index(m_)]
    subset=[]
    #print('sup_m:',sup_m)
    
    if len(p)>1:
        for i in range(len(p)):
            p_=p[:i]+p[i+1:]
            if p_ in rule:
                continue
            #print('p_:',p_)
            PRUN=False
            for pr in prun:
                if len(pr)==len(p) and list(set(p)&set(pr))==p_:
                    #print('pr,p,p_:',pr,p,p_)
                    PRUN=True
                    break
            if not PRUN:
                sup_p_=L_s[L_i.index(p_)]
                #print('sup_p_:',sup_p_)
                conf=sup_m/sup_p_
                if conf>=min_conf and ([p_,list(set(m_)-set(p_)),conf] not in rule):
                    print('rule:',p_,'->',list(set(m_)-set(p_)),' confidence:',conf)
                    rule.append([p_,list(set(m_)-set(p_)),conf])
                    #rule_cf.append(conf)
                    rule_,prun_=get_rule(m_,p_,prun,L_i,L_s,min_conf,rule)
                    rule.extend(rule_)
                    #rule_cf.extend(rule_cf_)
                    prun.extend(prun_)
                    #print('prun:',prun)
                else:
                    prun.append(p_)
                    
     
    return rule,prun


def rule_generation(L_k,L_sup,min_conf):
    """
    generating all rules from all frequent itemsets.
    
    arg:
        L_k:al frequent itemsets
        L_sup: support count of frequent itemsets
        min_conf: minimum confidence
        
    return:
        rules: all rules generated from all frequent itemsets
    """
    rules=[]
    rules_conf=[]
    for supi in range(len(L_k)):
        L_item,L_support=L_flatten(L_k[supi],L_sup[supi])
        prun_set=[]
        for lki in range(len(L_k[supi])-1,0,-1):
            for mi in range(len(L_k[supi][lki])):
                #prun_set=[]
                m=L_k[supi][lki][mi] 
                #print('m:',m)
                p=m[:]
                r,pruns=get_rule(m,p,prun_set,L_item,L_support,min_conf,[])
                if len(r)>0:
                    rules.extend(r)
                    #rules_conf.append(rc)
    return rules

