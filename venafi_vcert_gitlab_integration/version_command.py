import os

module_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))


def read_product_version():
    with open(os.path.join(module_dir, 'version.txt'), 'r', encoding='UTF-8') as f:
        return f.read().strip()


def main():
    print(read_product_version())


if __name__ == '__main__':
    main()
