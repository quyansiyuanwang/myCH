import random


class ItemsFetch:  # Fetch each getable item into a obj
    def __init__(self, complex_obj, turn_method=None, runit=False, apply_turning=None):
        self.complex_obj = complex_obj
        self.__parsing_obj = list()
        self.turn_method = turn_method
        
        if apply_turning is not None:
            self.apply_turning = apply_turning
        else:    
             if self.turn_method is not None:
                 self.apply_turning = True 
             else:
                 self.apply_turning = False
        if runit:
            self.analysis()
    
    @property
    def parsing_obj(self):  # result obj
        if not self.apply_turning:
            return self.__parsing_obj
        else:   
            if self.turn_method is not None:
                 return self.turn_method(self.__parsing_obj)
            else:
                 raise ValueError('turn_method shoud not be None when the apply_turning is opening')
    
    def auto_turning(self, func):  # for auto turn type switch
        def inner(*args, **kwargs):
             temp_at = self.apply_turning
             self.apply_turning = False
             result = func(*args, **kwargs)
             self.apply_turning = temp_at
             return result
        return inner()
        
    @parsing_obj.setter  # set it,no use yet
    def parsing_obj(self, new_value):
        self.__parsing_obj = new_value
    
    def base_type(self, obj):  # pick the items from complex obj by recursion
        for item in obj:
            if isinstance(item,(int, float, str, bool)):
                @self.auto_turning
                def auto_app():
                     self.parsing_obj.append(item)
            elif isinstance(item, (set,tuple,list)):
                self.base_type(item)
            elif isinstance(item, dict):
                self.base_type(item.items())
            else:
                raise TypeError(f'unkown type:{type(item)}') 
    
    def analysis(self):  # runit
        self.base_type(self.complex_obj)
        return self.parsing_obj
    
    def __str__(self):  # result
        return f'{self.parsing_obj}'
        
    def __repr__(self):
        return f'complex_obj: {self.complex_obj}\n'\
               f'parsing_obj: {self.parsing_obj}'

class Mylist(list):  
    def __init__(self, *args):
        # connection like: {'!hash_value:'{'iter':list_obj, 'start':start_from}}
        self.connection = {}
        self.args = args
        super().__init__(*args)
      
    def __hash__(self):   # 不了解怎么写hash and its utilizing
        return hash(tuple(*self.args))
    # delete items
    def myremove(self, *items, remove_times=-1, ignore_error:bool=False):
        items = ItemsFetch(tuple(*items)).analysis()
        if isinstance(remove_times, int):  # fill all of the remove times
            remove_times = [remove_times] * len(items)
        remove_times += [-1] * abs((len(items) - len(remove_times)))
        for index,item in enumerate(items):  # traverse the needed items
            while remove_times[index] != 0:
                try:
                    self.remove(item)
                    remove_times[index] -= 1
                except Exception as e:
                    if item not in self or ignore_error:
                        break
                    else:
                        raise Exception(e)  # error handling
        return self
    # connect or bind with other mylist obj
    def connect(self, *others, starts=None, names=None, ignore_error=True):
        # dispose error
        def try_ava(index,target,replace_val,ie_inner,error_type):
            try:
                result = target[index]
            except Exception as e:
                if not ie_inner:
                    raise error(e)
                result = replace_val
            return result
            
        for index, other in enumerate(others):
            name = try_ava(index,names,f'!{hash(other)}',ignore_error,KeyError)
            start = try_ava(index,starts,0,ignore_error,KeyError)
            self.connection[name] = {'iter':other,'start':start}  # logged data   
        return self
    # Pass the target list to obtain the corresponding index content
    def get(self, index, targets=None):
        temp_list = [self[index]]
        if targets is None:
            targets = []
            for conn_val in self.connection.keys():
                targets.append(conn_val)
        for target in targets:
            struct_form = self.connection[target]
            temp_list.append(struct_form['iter'][struct_form['start'] + index])
        result = Mylist(temp_list)
        if len(result) == 1:
            result = result[0]
        return result
    
    # Obtain the content of the corresponding index
    def get_all(self):
        def inner():
            for index in range(len(self)):
                yield self.get(index)
        return Mylist(inner())
    # Reorganization, The n.th element of each list is reorganized into a new list
    def regroup(self):
        def inner(): 
            for index in range(len(self[0])):
                yield Mylist(item[index] for item in self)
        return Mylist(inner())
    # subscript the corresponding contents in the iterable object
    def match(self, iterable):
        items = ItemsFetch(iterable).analysis()
        def inner():
            for index in ItemsFetch(self.regroup().get(0)).analysis():
                try:
                    yield items[index]
                except IndexError as e:
                    raise IndexError(f'index value:{index} out of length({len(items)-1})')
        return Mylist(inner())
        
class Myrandom:
    def __init__(self,random_struction):
        self.rs = random_struction
    # extract high probability head with quicksort
    def __quick_sort(self,lists,i,j,target):
        if i >= j:
            return list
        pivot = lists[i]
        low = i
        high = j
        while i < j:
            while i < j and lists[j][target] <= pivot[target]:
                j -= 1
            lists[i]=lists[j]
            while i < j and lists[i][target] >= pivot[target]:
                i += 1
            lists[j]=lists[i]
        lists[j] = pivot
        self.__quick_sort(lists,low,i-1,target)
        self.__quick_sort(lists,i+1,high,target)
        return lists
    # get it
    def fetch(self, number):
        choose_list = []
        def inner(inner_number,choose_list_in):
            random.shuffle(self.rs)  # disorganize
            self.__quick_sort(self.rs, 0, len(self.rs) - 1, target=1) 
            index = 0
            while index < len(self.rs):
                if random.uniform(0,100) <= self.rs[index][1]:
                    app = self.rs.pop(index)
                    choose_list_in.append(app)
                else:
                    index += 1
                if len(choose_list_in)==number:
                    return
            inner(number - len(choose_list_in), choose_list_in)
        inner(number,choose_list)
        random.shuffle(choose_list)
        return Mylist(choose_list)    

    def __str__(self):
        string = ''
        for index in range(len(self.rs)):
            string += f'{self.rs[index][0]}({self.rs[index][1]}),\t'
            if (index + 1) % 5 == 0:
                string += '\n'
        return string
        
members = Mylist(range(1, 44)).myremove(range(10,13), remove_times=[0,-1,0])
a = Mylist([20, 20, 20, 70] + [20] * 38)  # 第四个概率为70
members.connect(a)  # 联结
b = Myrandom(members.get_all())
#print(b)
c = b.fetch(7)  # 抽取
#print(c.regroup())
print(c.regroup().get(0))
print(c.match(range(5,49)))  # list可以存放人名，即可叫人

#print(members.get(0))
#print(members.get_all())
#print(members.get_all().regroup())

#a = ItemsFetch([3,6.39,(7,[2,5,{'%*','&'}]),{'hello':'world'}])
#a.analysis()
#print(a)
