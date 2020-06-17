#!/usr/bin/env python
# coding: utf-8

# In[1]:


class treeNode: 
#to store its child, parent, support count, other nodes with same name
    def __init__(self,itemName,count,parentNode):
        self.name=itemName       #name of this node
        self.support=count       #support count of this node (same item in same path) 
        self.nodeLink=None       #storing next same-name-node 
        self.parent=parentNode   #parentNode of this node (value:node)
        self.child={}            #childNode of this node (value: node)
    def inc_count(self,count):
        self.support+=count
    def show(self,ind=1):
        #print(' '*ind,self.name,' ',self.support)
        for child in self.child.values():
            child.show(ind+1)


# In[2]:


def createTree(transaction_db,minsup):
    """Create tree based on given .  
    Args:  
        transaction_db: Input transaction dict.  
        minsup: Used to prun out infrequent item(s).  
          
    Returns:  
        initTree: FP-Tree(treeNode) or None if no frequent item  
        headerTable: Header table of FP-Tree or None if no frequent item  
                     headerTable[item] = (frequency,itemnode)    
    """
    
    #to store the frequent item, its support count and its one sam-name-node in headertable
    headerTable={}
    for trans in transaction_db: #calculate support
        for item in trans:
            if item not in headerTable.keys():
                headerTable[item]=headerTable.get(item,0)+transaction_db[trans]
            else:
                headerTable[item]+=transaction_db[trans]
            #print(item,headerTable[item],headerTable.get(item,0),transaction_db[trans])
    #print('headertable:',headerTable)
    headKeys=list(headerTable.keys())[:]
    for item in headKeys: #pruning items
        if headerTable[item]<minsup:
            #print(item)
            del(headerTable[item])
    #print('after_headertable:',headerTable)
    frequentOneitem=set(headerTable.keys()) #get frequent 1-item set
    #print('frequentOneitem:',frequentOneitem)
    if len(frequentOneitem)==0: 
        return None,None
    for k in headerTable:
        headerTable[k]=[headerTable[k],None] #store support count and other same-name-node
    #print('headerTable:',headerTable)

    #create tree
    initTree=treeNode('root',1,None)
    for trans,sup in transaction_db.items(): #order the trans with frequent items
        tempTrans={}
        for item in trans:
            if item in frequentOneitem:
                tempTrans[item]=headerTable[item][0]
        #print('tempTrans:',tempTrans)
        if len(tempTrans)>0:
            orderTrans=[v[0] for v in sorted(tempTrans.items() ,key=lambda p:p[1] ,reverse=True)] 
            #print('orderTrans:',orderTrans)
            updateTree(orderTrans,initTree,headerTable,sup) #updating initTree by every trans
    return initTree, headerTable
            

def updateTree(orderItems, parentTreeNode, headerTable, count):
    """ Recursively update the FP-Tree  
    Args:  
        orderItems: Ordered frequent items  
        parentTreeNode: FP-Tree node  
        headerTable: Header table of FP-Tree  
        count: Count of exist same transaction of input items.  
          
    Returns:  
        None   
    """ 
    
    if orderItems[0] in parentTreeNode.child: #update the support of node
        parentTreeNode.child[orderItems[0]].inc_count(count)
    else: #add node(item in the suffix path) into tree (bottom of prefix tree = one brefore item in the path)
        parentTreeNode.child[orderItems[0]]=treeNode(orderItems[0],count,parentTreeNode)
        #update the nodelink of the item in headerTable
        if headerTable[orderItems[0]][1]==None:
            headerTable[orderItems[0]][1]=parentTreeNode.child[orderItems[0]]
        else:
            updateHeadertable(headerTable[orderItems[0]][1],parentTreeNode.child[orderItems[0]])
    if len(orderItems)>1:
        updateTree(orderItems[1::],parentTreeNode.child[orderItems[0]],headerTable,count)

def updateHeadertable(headerTableNode, itemNode):
    #update the nodelink fo every same-name-node in the headertable
    while(headerTableNode.nodeLink!=None): #let every same-name-node connect to next one other same-name-node (None finally)
        headerTableNode=headerTableNode.nodeLink #headerTableNode.nodeLink=old same-name-node
    headerTableNode.nodeLink=itemNode #itemNode=new same-name-node
    


# In[3]:


def ascend_along_tree(leafNode,prefixPath):
    """Ascends from the left node to root and store the path .  
    Args:  
        leafNode: Node of PF-Tree  
        prefixPath: list to store the traversal path  
          
    Returns:  
        None  
          
    Raises:  
        None  
    """ 
    if leafNode.parent!=None:
        prefixPath.append(leafNode.name) #store every item's name in the path
        ascend_along_tree(leafNode.parent,prefixPath) 

def findPrefixPath(node):
    """Find prefix path according to given FP-Tree node as   
    Args:    
        Node: Target FP-Tree node comes from header table.  
          
    Return:  
        condPats: The directory to hold {conditional path->count}  
          
    Raises:  
        None  
    """ 
    condPats={} #store conditional pattern paths
    while node!=None:
        prefixPath=[]
        ascend_along_tree(node,prefixPath)
        if len(prefixPath)>1:
            condPats[frozenset(prefixPath[1:])]=node.support
        node=node.nodeLink #next same-name-node
    return condPats


# In[4]:


def miningTree(tree,headerTable,minsup,prePath,frequentItemList):
    """Recursively finds frequent itemsets. 
       1. starting from the bottom item of header table (least frequent item)
       2. getting the conditional pattern paths (prefix paths) of this item
       3. pruning out the un-frequent items by createTree(), and preserving the frequent prefix items in the header table
       4. adding every frequent prefix item to the frequent item set
       5. recursively running step2-4
       
    Args:  
        Tree: FP-Tree  
        headerTable: Header table of FP-Tree  
        prePath: Prefix paths  
        freqItemList: Frequent item list (Final result)  
          
    Returns:  
        None  
          
    Raises:  
        None  
    """ 
    freqItems=[v[0] for v in sorted(headerTable.items(), key=lambda p:p[1][0])] #sort header table in ascending order
    #print('freqItems:',freqItems)
    for item in freqItems: #start from the bottom of header table
        newFreqset=prePath.copy()
        newFreqset.add(item) #add item in the front of prePath
        #print('final frequent Item:',newFreqset)
        frequentItemList.append(newFreqset)
        
        condPatBases=findPrefixPath(headerTable[item][1]) #find the conditional pattern paths (prefix paths) to the item
        #print('condPatBases:',item,condPatBases)
        subTree,subHead=createTree(condPatBases,minsup) #create tree and corresponding header table of these conditional pattern paths
        #print('subHead:',subHead)
        if subHead!=None: #after pruning out the un-frequent items, header table records evrey prefix frequent item with this item
            miningTree(subTree,subHead,minsup,newFreqset,frequentItemList) 


# In[5]:
