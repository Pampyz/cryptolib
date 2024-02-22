from abstract import Field, FieldElement, Group, GroupElement


def play_with_group():
    big_prime = 1 + 407 * (1 << 119)
    field = Field(big_prime)

    print(random_number)


def play_with_field():
    big_prime = 1 + 407 * (1 << 119)
    field = Field(big_prime)

    x = field.get_random_element()
    y = field.get_random_element()

    print(x)
    print(x ^ y)
    print(FieldElement(4, field)*x)


def main():
    play_with_field()
    #play_with_group()

    
if __name__=='__main__':
    main()