from types import FunctionType


def generate_properties_for_class(getter_suffix='_getter', setter_suffix='_setter', deleter_suffix='_deleter'):
    def decorator(cls):
        names = set()
        getters = {}
        setters = {}
        deleters = {}

        # local_methods = dir(cls)
        local_methods = {x:y for x, y in cls.__dict__.items() if isinstance(y, FunctionType | classmethod | staticmethod)}
        for name in local_methods:
            if name.endswith(getter_suffix):
                base_name = name[:-len(getter_suffix)]
                getters[base_name] = getattr(cls, name)
                names.add(base_name)

            if name.endswith(setter_suffix):
                base_name = name[:-len(setter_suffix)]
                setters[base_name] = getattr(cls, name)
                names.add(base_name)

            if name.endswith(deleter_suffix):
                base_name = name[:-len(deleter_suffix)]
                deleters[name[:-len(deleter_suffix)]] = getattr(cls, name)
                names.add(base_name)


        for name in names:
            getter = getters.get(name, None)
            setter = setters.get(name, None)
            deleter = deleters.get(name, None)

            if not getter:
                # print('make default getter for', cls, name, f'_{name}')
                def default_getter(cls, name=name):
                    return getattr(cls, f'_{name}', None)
                getter = default_getter

            if not setter:
                def default_setter(cls, value, name=name):
                    setattr(cls, f'_{name}', value)
                setter = default_setter

            if not deleter:
                def default_deleter(cls, name=name):
                    delattr(cls, f'_{name}')
                deleter = default_deleter

            setattr(cls, name, property(getter, setter, deleter))

        return cls
    return decorator



if __name__ == '__main__':
    class Z:
        pass

    @generate_properties_for_class(getter_suffix='_getter', setter_suffix='_setter')
    class A:
        pass
        # def x_getter(self):
        #     print('get original x')
        #     return self._x

        # def x_setter(self, value):
        #     self._x = value
        #     print('A setter side effect')


    @generate_properties_for_class()
    class B(A):
        def __init__(self):
            super().__init__()

        def x_setter(self, value):
            self._x = value
            # super().x_setter(value) # enables you to use getters and setters with inheritance while keeping the parent class's behavior
            print('B setter side effect')
        # @x.setter
        # def x(self, value):
        #     setattr(super(), 'x', value)
        #     print('-----', )



    # how you'd do it without the property generator, using __getattr__ and __setattr__
    # class B(A):
    #     def __setattr__(self, name, value):
    #         super().__setattr__(name, value)
    #
    #         if name == 'x':
    #             print('custom x stuff!')


    e = B()
    e.x = 2
    print('xxxxxxxx', e.x)
    # del e.x
