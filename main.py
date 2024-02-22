from abstract import Field, FieldElement, Group, GroupElement, EllipticGroup, EllipticGroupElement

def play_with_field():
    big_prime = 1 + 407 * (1 << 119)
    field = Field(big_prime)

    x = field.get_random_element()
    y = field.get_random_element()

    print(x)
    print(x ^ 100)
    print(FieldElement(4, field)*x)

    ec = EllipticGroup()
    g = ec.generator()
    print('Generator: ', g)
    print(g.assert_solution())


def main():
    play_with_field()
    #play_with_group()

    
if __name__=='__main__':
    main()