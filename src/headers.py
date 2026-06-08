import sys


class Field:
    def __init__(self, name='', size=0, default_value=0):
        self.name = name
        self.size = size
        self.default_value = default_value

        if name == '' or size == 0:
            print('ERROR!\nThe field needs a valid name and a size > 0')
            sys.exit()


class Header:
    def __init__(self, name='', size=0):
        self.name = name
        self.size = size
        self.fields = []

        if name == '' or size == 0:
            print('ERROR!\nThe header needs a valid name and a size > 0')
            sys.exit()

        if self.size % 8 != 0:
            print('ERROR!\nThe header size needs to be byte aligned')
            sys.exit()

    def validHeader(self):
        if self.size <= 0 or len(self.fields) == 0:
            print('Invalid header size\n')
            return False

        total = 0
        for field in self.fields:
            total += field.size

        if total != self.size:
            print(f'Invalid header size (header {self.name})')
            return False

        return True

    def addField(self, field):
        if isinstance(field, Field):
            self.fields.append(field)
            return

        if isinstance(field, list):
            if len(field) == 0:
                print('ERROR! The list of fields is invalid!')
                sys.exit()
            for item in field:
                if not isinstance(item, Field):
                    print('ERROR! The list of fields is invalid!')
                    sys.exit()
            self.fields.extend(field)
            return

        print('ERROR! The list of fields is invalid!')
        sys.exit()

    def printHeader(self):
        print(f'\nheader {self.name} {{')
        for field in self.fields:
            print(f'\tbit<{field.size}> {field.name};')
        print('}')
