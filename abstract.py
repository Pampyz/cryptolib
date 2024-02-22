from secrets import SystemRandom

class Field:
    """ Defines a finite field of integers under addition and multiplication modulo a prime P """
    def __init__(self, p):
        self.p = p

    def zero(self):
        return FieldElement(0, self)

    def one(self):
        return FieldElement(1, self)

    def multiply(self, left, right):
        return FieldElement((left.value * right.value) % self.p, self)

    def add(self, left, right):
        return FieldElement((left.value + right.value) % self.p, self)

    def subtract(self, left, right):
        return FieldElement((self.p + left.value - right.value) % self.p, self)

    def negate(self, operand):
        return FieldElement((self.p - operand.value) % self.p, self)

    def inverse(self, operand):
        a, b, g = xgcd(operand.value, self.p)
        return FieldElement(a, self)

    def divide(self, left, right):
        assert(not right.is_zero()), "Cannot divide by zero"
        a, b, g = xgcd(right.value, self.p)
        return FieldElement(left.value * a % self.p, self)

    def get_random_element(self):
        return FieldElement(SystemRandom().randrange(self.p), self)

    def get_multiplicative_subgroup(self):
        """ Returns the multiplicative subgroup of the field """
        return Group(self.p)

class FieldElement:
    def __init__(self, value, field):
        self.value = value
        self.field = field

    def __add__(self, right):
        return self.field.add(self, right)

    def __mul__(self, right):
        return self.field.multiply(self, right)

    def __sub__(self, right):
        return self.field.subtract(self, right)

    def __truediv__(self, right):
        return self.field.divide(self, right)

    def __neg__(self):
        return self.field.negate(self)

    def inverse(self):
        return self.field.inverse(self)

    def __pow__(self, exponent):
        ''' Double-and-add implementation of exponentiation '''
        if exponent == 0:
            return self.field.one()
        elif exponent == 1:
            return self
        elif exponent % 2 == 0:
            return (self*self)**(int(exponent//2))
        else:
            return self*((self*self)**(int((exponent-1)//2)))

    # Modular exponentiation
    def __xor__(self, exponent):
        acc = FieldElement(1, self.field)
        val = FieldElement(self.value, self.field)
        for i in reversed(range(len(bin(exponent)[2:]))):
            acc = acc * acc
            if (1 << i) & exponent != 0:
                acc = acc * val
        return acc

    def __eq__(self, other):
        return self.value == other.value

    def __neq__(self, other):
        return self.value != other.value

    def __str__(self):
        return str(self.value)

    def __bytes__(self):
        return bytes(str(self).encode())

    def is_zero(self):
        if self.value == 0:
            return True
        else:
            return False

class Group:
    """ Multiplicative group of integers under multiplication modulo a prime p """
    def __init__(self, p):
        self.p = p

    def one(self):
        return FieldElement(1, self)

    def multiply(self, left, right):
        return FieldElement((left.value * right.value) % self.p, self)

    def inverse(self, operand):
        a, b, g = xgcd(operand.value, self.p)
        return FieldElement(a, self)

    def divide(self, left, right):
        assert(not right.is_zero()), "Cannot divide by zero"
        a, b, g = xgcd(right.value, self.p)
        return FieldElement(left.value * a % self.p, self)

class GroupElement:
    def __init__(self, value, field):
        self.value = value
        self.field = field

    def __mul__(self, right):
        return self.field.multiply(self, right)

    def __truediv__(self, right):
        return self.field.divide(self, right)

    def inverse(self):
        return self.field.inverse(self)

    # Modular exponentiation
    def __xor__(self, exponent):
        acc = FieldElement(1, self.field)
        val = FieldElement(self.value, self.field)
        for i in reversed(range(len(bin(exponent)[2:]))):
            acc = acc * acc
            if (1 << i) & exponent != 0:
                acc = acc * val
        return acc

    def __eq__(self, other):
        return self.value == other.value

    def __neq__(self, other):
        return self.value != other.value

    def __str__(self):
        return str(self.value)

    def __bytes__(self):
        return bytes(str(self).encode())

class EllipticGroup(Group):
    """ 
        Group based on the secp256k1 elliptic curve 
        Usually considered additive but multiplicatively implemented
    """

    def __init__(self):
        """ 
        Solutions x, y of the equation y2 = x3 + ax + b over Fp 
        Base point G given by coordinates Gx, Gy    
        """
        self.p = int('0xFFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFE FFFFFC2F'.replace(' ', ''), 16)
        self.a = int('0x00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000'.replace(' ', ''), 16)
        self.b = int('0x00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000007'.replace(' ', ''), 16)
        self.Gx = int('0x79BE667E F9DCBBAC 55A06295 CE870B07 029BFCDB 2DCE28D9 59F2815B 16F81798'.replace(' ', ''), 16)
        self.Gy = int('0x483ADA77 26A3C465 5DA4FBFC 0E1108A8 FD17B448 A6855419 9C47D08F FB10D4B8'.replace(' ', ''), 16)

        self.field = Field(self.p)
        self.a = FieldElement(self.a, self.field)
        self.b = FieldElement(self.b, self.field)

    def one(self):
        raise ArithmeticError('Not sure what the identity is in this Group!') 

    def multiply(self, left, right):
        raise NotImplementedError

    def inverse(self, operand):
        return EllipticGroupElement(operand.x, -operand.y, self)
    
    def double(self, operand):
        pass

    def divide(self, left, right):
        raise NotImplementedError

    def generator(self):
        return EllipticGroupElement(self.Gx, self.Gy, self)
    
class EllipticGroupElement(GroupElement):
    def __init__(self, x, y, group):
        self.x = FieldElement(x, Field(group.p))
        self.y = FieldElement(y, Field(group.p))
        self.group = group

    def __mul__(self, right):
        return self.group.multiply(self, right)

    def __truediv__(self, right):
        return self.group.divide(self, right)

    def inverse(self):
        return self.field.inverse(self)

    def assert_solution(self):
        return (self.y**2) - (self.x**3) - self.group.a*self.x - self.group.b
        #assert (self.y^2) - 
        #assert self.y*self.y - self.x*self.x*self.x self.group.a
        #Solutions x, y of the equation y2 = x3 + ax + b over Fp 

    # Modular exponentiation
    def __xor__(self, exponent):
        acc = FieldElement(1, self.field)
        val = FieldElement(self.value, self.field)
        for i in reversed(range(len(bin(exponent)[2:]))):
            acc = acc * acc
            if (1 << i) & exponent != 0:
                acc = acc * val
        return acc

    def __eq__(self, other):
        return self.value == other.value

    def __neq__(self, other):
        return self.value != other.value

    def __str__(self):
        return str((str(self.x), str(self.y)))

    def __bytes__(self):
        return bytes(str(self).encode())

class SchnorrGroup(Group):
    def __init__(self, p, q, r):
        pass
    
def xgcd(x, y):
    """ Implementation of extended euclidean algorithm to find inverse modulo p """
    old_r, r = (x, y)
    old_s, s = (1, 0)
    old_t, t = (0, 1)

    while r != 0:
        quotient = old_r // r
        old_r, r = (r, old_r - quotient * r)
        old_s, s = (s, old_s - quotient * s)
        old_t, t = (t, old_t - quotient * t)

    return old_s, old_t, old_r # a, b, g