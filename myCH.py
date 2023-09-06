import random


class ItemsFetch:
    """
    Fetch each getable item into an obj
    """

    def __init__(self, complex_obj, turn_method: callable = None, runit: bool = False, apply_turning: bool = None):
        self.complex_obj = complex_obj
        self.__parsing_obj: list = list()
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
    def parsing_obj(self) -> iter:
        """
        An attribute as result obj.
        :return: A simple iterable obj.
        """
        if not self.apply_turning:
            return self.__parsing_obj
        else:
            if self.turn_method is not None:
                return self.turn_method(self.__parsing_obj)
            else:
                raise ValueError('turn_method should not be None when the apply_turning is opening')

    def auto_turning(self, func: callable):
        """
        For auto turn type switch.
        :param func: Inner running function.
        :return: The result function running.
        """

        def inner(*args, **kwargs):
            temp_at = self.apply_turning
            self.apply_turning = False
            result = func(*args, **kwargs)
            self.apply_turning = temp_at
            return result

        return inner()

    @parsing_obj.setter
    def parsing_obj(self, new_value) -> None:
        """
        Could set it,no use yet.
        :param new_value: New value to replace it.
        :return: None
        """
        self.__parsing_obj = new_value

    def __base_type(self, obj) -> None:
        """
        Pick the items from complex obj by recursion.
        :param obj: The obj we need to analysis.
        :return: None. Its storage by pointer.
        """
        for item in obj:
            if isinstance(item, (int, float, str, bool)):
                @self.auto_turning
                def auto_app():
                    self.parsing_obj.append(item)
            elif isinstance(item, (set, tuple, list)):
                self.__base_type(item)
            elif isinstance(item, dict):
                self.__base_type(item.items())
            else:
                raise TypeError(f'unknown type:{type(item)}')

    def analysis(self) -> dict:
        """
        The entrance to run it.
        :return: Results analyzed.
        """
        self.__base_type(self.complex_obj)
        return self.parsing_obj

    def __str__(self):
        return f'{self.parsing_obj}'

    def __repr__(self):
        return f'complex_obj: {self.complex_obj}\n' \
               f'parsing_obj: {self.parsing_obj}'


class Mylist(list):
    """
    Add some new functions to the list.
    A new class of a list.
    """

    def __init__(self, *args):
        # connection like: {'!hash_value:'{'iter':list_obj, 'start':start_from}, ...}
        self.connection = {}
        self.args = args
        super().__init__(*args)

    def __hash__(self):  # IDK how to write hash and its utilizing
        return hash(tuple(*self.args))

    def myremove(self, *items, remove_times=None, ignore_error: bool = False) -> 'Mylist':
        """
        Remove items.
        :param items: Items which you need to remove.
        :param remove_times: Number of times to remove the target you need.
        :param ignore_error: Ignore_error.
        :return: Its self.
        """
        if remove_times is None:
            remove_times = [-1]
        items = ItemsFetch(tuple(*items)).analysis()
        if isinstance(remove_times, int):  # fill all the remove times
            remove_times = [remove_times] * len(items)
        remove_times += [-1] * abs((len(items) - len(remove_times)))
        for index, item in enumerate(items):  # traverse the needed items
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

    def connect(self, *others: 'Mylist', starts=None, names=None, ignore_error: bool = True) -> 'Mylist':
        """
        Connect or bind with other mylist objs.
        :param others: Other mylist objs.
        :param starts: Start a step.
        :param names: Another objs name.
        :param ignore_error: Ignore error.
        :return: Its self.
        """

        if starts is None:
            starts = [0]

        def try_ava(index_: int, target, replace_val, ie_inner: bool, error_type):  # dispose error
            """
            Dispose error in get-items in names and starts.
            :param index_: Index.
            :param target: The object we get-items.
            :param replace_val: If the item does not exist, this will replace as output.
            :param ie_inner: For inheriting ignore_error.
            :param error_type: The type of error will be raised.
            :return: Corresponding content in the target.
            """
            try:
                return target[index_]
            except Exception as e:
                if not ie_inner:
                    raise error_type(e)
                return replace_val

        for index, other in enumerate(others):
            name = try_ava(index, names, f'!{hash(other)}', ignore_error, KeyError)  # Get name
            start = try_ava(index, starts, 0, ignore_error, KeyError)  # get start value
            self.connection[name] = {'iter': other, 'start': start}  # Logged data
        return self

    def get(self, index: int, targets: list = None) -> 'Mylist':
        """
        Pass the target list to obtain the corresponding index content.
        :param index: Index.
        :param targets: Select the target of the link.
        :return: A Mylist includes contents.
        """
        temp_list = [self[index]]
        # If the targets are empty, add all linked lists to the targets.
        if targets is None:
            targets = []
            for conn_val in self.connection.keys():
                targets.append(conn_val)
        # Collect out the content we want
        for target in targets:
            struct_form = self.connection[target]
            temp_list.append(struct_form['iter'][struct_form['start'] + index])

        result = Mylist(temp_list)
        # If there is only one layer, reduce list nesting.
        if len(result) == 1:
            result = result[0]
        return result
    
    def mylist_decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return Mylist(result)
        return wrapper

    @mylist_decorator
    def get_all(self) -> 'Mylist':
        """
        Obtain the content of the corresponding index.
        :return: A Mylist includes all the items.
        """

        for index in range(len(self)):
            yield self.get(index)


    @mylist_decorator
    def regroup(self) -> 'Mylist':
        """
        Reorganization, the n.th element of each list is reorganized into a new list.
        :return: A Mylist includes the items regrouped.
        """
        
        for index in range(len(self[0])):
            yield Mylist(item[index] for item in self)


    @mylist_decorator
    def match(self, iterable) -> 'Mylist':
        """
        Subscript the corresponding contents in the iterable object.
        :param iterable: The elem in Mylist is used as the subscript, retrieve the corresponding element for \
            iterable objects.
        :return: A new group of elem collect from iterable
        """
        # Get items from the iterable
        items = ItemsFetch(iterable).analysis()
        
        first_group = self.regroup().get(0)
        for index in ItemsFetch(first_group).analysis():
            try:
                yield items[index]
            except IndexError:
                raise IndexError(f'index value:{index} out of length({len(items) - 1})')


class Myrandom:
    def __init__(self, random_struction):
        self.rs = random_struction

    def __quick_sort(self, lists: list, i: int, j: int, target: int):
        """
        Extract high-probability head with quicksort.
        :param lists: The list we need to sort.
        :param i: Pre-index.
        :param j: Post-index.
        :param target: Content we use it as standard to sort.
        :return: The sorted list.
        """
        if i >= j:
            return list
        pivot = lists[i]
        low = i
        high = j
        while i < j:
            while i < j and lists[j][target] <= pivot[target]:
                j -= 1
            lists[i] = lists[j]
            while i < j and lists[i][target] >= pivot[target]:
                i += 1
            lists[j] = lists[i]
        lists[j] = pivot
        self.__quick_sort(lists, low, i - 1, target)
        self.__quick_sort(lists, i + 1, high, target)
        return lists

    def fetch(self, number: int) -> 'Mylist':
        """
        Extract Elements.
        :param number: The number of samples we need to extract
        :return: A random Mylist includes its item(s)
        """
        choose_list: list = list()

        def inner(choose_list_in):
            random.shuffle(self.rs)  # disorganize
            self.__quick_sort(self.rs, 0, len(self.rs) - 1, target=1)

            index = 0
            while index < len(self.rs):
                random_value = random.uniform(0, 100)
                standard_value = self.rs[index][1]
                # if random value beyond standard value,collect it.
                if random_value <= standard_value:
                    app = self.rs.pop(index)
                    choose_list_in.append(app)
                else:
                    index += 1
                if len(choose_list_in) == number:
                    return
            inner(choose_list_in)

        inner(choose_list)

        random.shuffle(choose_list)  # disorganize
        return Mylist(choose_list)

    def __str__(self):
        string = ''
        for index in range(len(self.rs)):
            string += f'{self.rs[index][0]}({self.rs[index][1]}),\t'
            # Wrap after print how many items
            if (index + 1) % 5 == 0:
                string += '\n'
        return string

if __name__=='__main__':
    members = Mylist(range(1, 44)).myremove(range(10, 13), remove_times=[0, -1, 0])
    a = Mylist([20, 20, 20, 70] + [20] * 38)  # 第四个概率为70
    members.connect(a)  # 联结
    b = Myrandom(members.get_all())
    # print(b)
    c = b.fetch(7)  # 抽取
    # print(c.regroup())
    print(c.regroup().get(0))
    print(c.match(range(5, 49)))  # list可以存放人名，即可叫人

    # print(members.get(0))
    # print(members.get_all())
    # print(members.get_all().regroup())

    # a = ItemsFetch([3,6.39,(7,[2,5,{'%*','&'}]),{'hello':'world'}])
    # a.analysis()
    # print(a)
