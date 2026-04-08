class ShoppingCart:
    def __init__(self):
        self.items = []

    def __add__(self, other):
        new_cart = ShoppingCart()
        new_cart.items = self.items.copy()
        new_cart.items.append(other)
        return new_cart

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)

    def __contains__(self, item):
        return item in self.items


if __name__ == '__main__':
    shopping_cart = ShoppingCart()
    shopping_cart += 'text'
    shopping_cart += 'text2'
    print('text' in shopping_cart)
    for item in shopping_cart:
        print(item)

