class DataApp:
    def __init__(self, label_path):
        self.label_path = label_path
        self.data = []
        self.row = 0
        self.load_data_from_path(label_path)

    def load_data_from_path(self, label_path):
        with open(label_path) as f0:
            contexts = f0.readlines()

        for line in contexts:
            if len(line.strip()) == 0:
                continue
            context = list(map(float, line.strip().split(' ')))
            context[0] = int(context[0])

            assert len(context) == 5  # 通用目标标注下每行只能存储5个数据
            self.data.append(context)

            self.row += 1

    def append(self, data: list or tuple):
        assert len(data) == 5
        self.data.append(data)

    def insert(self, index, data):
        assert len(data) == 5
        self.data.insert(index, data)

    def pop(self, index):
        self.data.pop(index)

    def save(self, dot=3):
        text = ''
        for line in self.data:
            line = list(map(lambda x: round(x, dot), line))
            text += ' '.join(list(map(str, line))) + '\n'
        with open(self.label_path, 'w') as f0:
            f0.write(text.strip())

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, index):
        return self.data[index]

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        yield from self.data

    def __repr__(self):
        return str(self.data)
