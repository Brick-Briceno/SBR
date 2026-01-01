"""
SBR types of data
by @brick_briceno 2024
"""

from sbr_utils import (one_dimention_list_recurtion,
                       convert_unions_to_tuples,
                       separate_path_extension,
                       delete_args)
from typing import get_type_hints
from errors import *
import inspect
import os

pulse = 4

def pulse_will_be(new: int):
    global pulse
    pulse = new


def SBR_Function(function):
    ("Decorator that validates the types of elements within lists according to type annotations "
    "Throws SBR_ERROR if any element doesn't match the expected type")
    def wrapper(*args, **kwargs):
        hints = get_type_hints(function)
        sig = inspect.signature(function)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()

        if 'data' in bound.arguments:
            #print(bound.arguments['data'])
            allowed_types_for_data = convert_unions_to_tuples(hints['data'])
            if not isinstance(bound.arguments['data'], allowed_types_for_data):
                str_admited_types = ", ".join([t.__name__ for t in allowed_types_for_data]
                                              )[::-1].replace(",", " and"[::-1], 1)[::-1]
                wrong_type = type(bound.arguments['data']).__name__
                raise SBR_ERROR(
                    f"The data input in {function.__name__} must be {str_admited_types}, not '{wrong_type}'"
                )

        allowed_types_for_args = convert_unions_to_tuples(hints['args'])
        for index, t in enumerate(bound.arguments.get('args'), start=1):
            if type(t) not in allowed_types_for_args:
                str_admited_types = ", ".join([t.__name__ for t in allowed_types_for_args]
                                              )[::-1].replace(",", " and"[::-1], 1)[::-1]
                wrong_type = type(t).__name__
                raise SBR_ERROR(
                    f"The {index}th element in {function.__name__} must be {str_admited_types}, not '{wrong_type}'"
                )

        return function(*args, **kwargs)
    wrapper.__doc__ = function.__doc__
    return wrapper


def quantize(data):
    data = data.replace("6", "10010010") \
    .replace("3", "1110") \
    .replace("8", "1") \
    .replace("4", "1") \
    .replace("2", "1")
    return data

def only_has(data, allowed_characters):
    for char in data:
        if char not in allowed_characters:
            return False
    return True


def L(data, a):
    #This is an optimized version of the SBR "L" effect
    if isinstance(data, Rhythm):
        data: str = data.bin
        if len(data) <= a: return Rhythm((data*a)[:a])
        return Rhythm(data[:a])
    if len(data) <= a: return type(data)((data*a)[:a])
    return type(data)(data[:a])


class StringBR(str):
    # def __init__(self, data=""):
    #     self.data = data
    ...

class Rhythm:
    __name__ = "Rhythm"
    def __init__(self, data=""):
        if isinstance(data, Rhythm):
            data = data.bin
        elif isinstance(data, (int, str)):
            data = str(data)
        else: raise SBR_ERROR(f"These are not rhythmic values '{data}'")
        if data.isnumeric() or data == "":
            self.__data = data
        else: raise SBR_ERROR(f"These are not rhythmic values '{data}'")

    @property
    def bin(self):
        return self.__data

    @property
    def smtones_code(self):
        #here there's the
        #tones and semitones code [2, 2, 1, 2, 2, 2, 1] for example
        data = quantize(self.__data)
        if len(data) != 12:
            raise SBR_ERROR(
                f"It can't convert to smtones code, it must have 12 bits, not {len(data)}")
        scale_tuple = []
        temp = ""
        for note in data:
            temp += note
            if note == "1":
                scale_tuple.append(len(temp))
                temp = ""
        scale_tuple.append(scale_tuple[0])
        scale_tuple.pop(0)
        return tuple(scale_tuple[:-1]+scale_tuple[-1:])

    @property
    def scale(self):
        if len(self.smtones_code) != 7:
            raise SBR_ERROR(
                f"It can't convert to scale, it must have 7 notes, not {len(self.smtones_code)}")
        scale_final = []
        for x in range(7):
            scale_final.append(sum(self.smtones_code[:x])+1)
        return tuple(scale_final)

    def __repr__(self):
        result = ""
        prw = self.__data.replace("3", "3   ").replace("6", "6       ")
                                                            #10011010
        for i in range(0, len(prw), pulse):
            result += prw[i:i+pulse] + " "
        return f"B{result.rstrip()}"

    def __str__(self):
        return self.__repr__()

    def __int__(self):
        return int(self.bin)

    def __hash__(self):
        return hash(self.bin)+69

    def __len__(self):
        n = 0
        for b in self.__data:
            if b == "3": n += 4
            elif b == "6": n += 8
            else: n += 1
        return n

    @property
    def metric(self):
        n = 0
        for b in self:
            if b in (1, 5, 7, 9): n += 1
            elif b in (3, 6): n += 3
            elif b in (2, 4, 8): n += b
        return n

    def __iter__(self):
        return (int(x) for x in self.bin)

    def __add__(self, bit):
        if isinstance(bit, int) or isinstance(bit, str):
            return Rhythm(self.__data + str(bit))
        elif isinstance(bit, Rhythm):
            return Rhythm(self.__data + bit.bin)
        else: raise SBR_ERROR(
            f"Can only concatenate rhythms, str or int with rhythms not '{type(bit).__name__}'")

    def __iadd__(self, bit):
        return self + bit
    
    def __mul__(self, n):
        return Rhythm(self.__data*n)

    def __xor__(self, rhythm):
        return self.ghost(rhythm)

    def __invert__(self):
        end = ""
        for x in quantize(self.bin):
            end += str(int(not bool(int(x))))
        return Rhythm(end)

    def __getitem__(self, key):
        try: return int(self.bin[key])
        except IndexError:
            raise SBR_ERROR(f"Rhythm index out of range, key: {key}, key max: {len(self)-1}")

    def reverse(self):
        return Rhythm(self.__data[::-1])

    def concatenate(self, data):
        return self+data

    def overlap(self, data):
        if isinstance(data, Rhythm):
            r1, r2 = quantize(self.__data), quantize(data.bin)
        elif isinstance(data, str):
            r1, r2 = quantize(self.__data), quantize(data)
        elif isinstance(data, int):
            r1, r2 = quantize(self.__data), quantize(str(data))
        else: raise SBR_ERROR(
                f"You can only layer rhythms with rhythms and int, not rhythms with '{type(data).__name__}'")
        salida = ""
        if len(r1) > len(r2): r2 += "0"*(len(r1)-len(r2))
        else: r1 += "0"*(len(r2)-len(r1))
        for b1, b2 in zip(r1, r2): salida += str(int(int(b1) or int(b2))) #or
        return Rhythm(salida)

    #This is the same function as arrays only it uses an Xor gate
    def ghost(self, data):
        if isinstance(data, Rhythm):
            r1, r2 = quantize(self.__data), quantize(data.bin)
        elif isinstance(data, str):
            r1, r2 = quantize(self.__data), quantize(data)
        else: raise SBR_ERROR(
                f"You can only layer rhythms with rhythms, not beats with '{type(data).__name__}'")
        salida = ""
        if len(r1) > len(r2): r2 += "0"*(len(r1)-len(r2))
        else: r1 += "0"*(len(r2)-len(r1))
        for b1, b2 in zip(r1, r2): salida += str(int(int(b1) ^ int(b2))) #xor
        return Rhythm(salida)


class Group(list):
    __name__ = "Group"
    def __repr__(self) -> str:
        if not len(self):
            return "{ }"
        pw = "{"
        for obj in self:
            if isinstance(obj, Instrument):
                pw += f"${obj.inst_id}"# ***{obj.name}***; "
            elif isinstance(obj, float):
                pw += f"{round(obj, 8)}; "
            else: pw += f"{obj}; "
        return pw[:-2]+"}"

    def __add__(self, data):
        if isinstance(data, (int, float)):
            result = []
            for i in self:
                result.append(i + data)
            return Group(result)
        elif isinstance(data, Group):
            return Group(list(self)+data)
        else: raise SBR_ERROR("function not yet implemented")

    def __sub__(self, data):
        if isinstance(data, int):
            result = []
            for i in self:
                result.append(i - data)
            return Group(result)
        elif isinstance(data, Group):
            if len(data) != len(data):
                raise SBR_ERROR("Grous must have the same length")
            else:
                for i, x in enumerate(self):
                    data[i] += x
                return data
        else: raise SBR_ERROR("function not yet implemented")

    def __mul__(self, data):
        if isinstance(data, int):
            return Group(super().__mul__(data))
        elif isinstance(data, float):
            new = []
            for i in self: new.append(i*data)
            return Group(new)
        else: raise SBR_ERROR("function not yet implemented")

    def __round__(self):
        new = []
        for n in self:
            try: new.append(round(n))
            except AttributeError:
                raise SBR_ERROR(f"Cannot round this data type '{type(n).__name__}' '{n}'")
        return Group(new)

    def __invert__(self):
        end = []
        for item in self:
            if isinstance(item, (Rhythm ,int, Note, Tones, Group)):
                end.append(~item)
            if isinstance(item, float):
                end.append(item-item*2)
            else: raise SBR_ERROR(f"This type cannot be inverted: {item}")
        return Group(end)

    def __reversed__(self):
        return super().__reversed__()

    def __getitem__(self, key):
        try: return super().__getitem__(key)
        except IndexError:
            if len(self) == 0: raise SBR_ERROR("Empty Group")
            raise SBR_ERROR(f"Index out of range, key: {key}, key max: {len(self)-1}")

    def reverse(self):
        return Group(self[::-1])

    def concatenate(self, data):
        return self+data

    def overlap(self, data):
        return self+data

    def ghost(self, data):
        return self-data


class Note:
    __name__ = "Note"
    def __init__(self, data=35):
        if isinstance(data, Note):
            self.__diatonic_tone, self.__alteration = data.bin
        elif isinstance(data, int):
            self.__diatonic_tone, self.__alteration = data, 0
        elif isinstance(data, str):
            if not only_has(data, "|-0123456789b#"):
                raise SBR_ERROR(f"Invalid data {data}")
            else:
                tone = ""
                octave = ""
                octave_mode = False
                self.__alteration = 0
                for char in data:
                    if char.isnumeric() or char == "-":
                        if octave_mode:
                            octave += char
                        else: tone += char
                    elif char == "|": octave_mode = True
                    elif char == "b": self.__alteration -= 1
                    elif char == "#": self.__alteration += 1
                if tone == "": tone = 1
                else: tone = eval(tone+"+0")
                if tone == "": octave = 5
                else: octave = eval(octave+"+0")
                self.__diatonic_tone = tone+octave*7-1
        else: raise SBR_ERROR(f"Invalid data '{data}'")

    @property
    def bin(self) -> tuple:
        return self.__diatonic_tone, self.__alteration
    
    @property
    def oct(self):
        return self.__diatonic_tone // 7

    @property
    def str_alteration(self):
        alt = self.__alteration
        if alt < 0: alt = "b"*abs(alt)
        elif alt > 0: alt = "#"*alt
        else: alt = ""
        return alt

    def __repr__(self):
        #calculate octave
        octave = 0
        degree = 1+self.__diatonic_tone
        while degree > 7:
            octave += 1
            degree -= 7
        return f"{self.str_alteration}{degree}|{octave if octave else ""}"

    def __str__(self):
        return repr(self)

    def __int__(self):
        return self.__diatonic_tone

    def __round__(self):
        return int(self)

    def __invert__(self):
        alt = ~self.__alteration+1
        if alt < 0: alt = "b"*abs(alt)
        elif alt > 0: alt = "#"*alt
        else: alt = ""
        return Note(f"{~int(self)}{alt}")

    def __mul__(self, data):
        if isinstance(data, int):
            return Note(f"{self.str_alteration}{int(self)}")
        else: raise SBR_ERROR("function not yet implemented")

    def __add__(self, valor):
        #You can add or increment values ​​in str or int
        if isinstance(valor, (int, Note)):
            return Note(f"{self.__diatonic_tone + int(valor)+1}{self.str_alteration}")
        elif isinstance(valor, str):
            if valor.isnumeric():
                return Note(self.__diatonic_tone + int(valor))
            elif valor == "b":
                return Note(f"{self.__diatonic_tone}{"b"*abs(self.__alteration-valor)}")
            elif valor == "#":
                return Note(f"{self.__diatonic_tone}{"#"*self.__alteration-valor}")
            else: raise SBR_ERROR(f"This is not a valid value {valor} is {type(valor).__name__}")
        else:
            raise SBR_ERROR("function not yet implemented")

    def __sub__(self, valor):
        #You can add or increment values ​​in str or int
        if isinstance(valor, (int, Note)):
            return Note(f"{self.__diatonic_tone - int(valor)+1}{self.str_alteration}")
            return Note()
        elif valor.isnumeric():
            return Note(self.__diatonic_tone - int(valor))
        elif valor == "b":
            return Note(f"{self.__diatonic_tone}{"b"*abs(self.__alteration-valor)}")
        elif valor == "#":
            return Note(f"{self.__diatonic_tone}{"#"*self.__alteration-valor}")
        else: raise TypeError("This is not a valid value")

    def __lt__(self, n):
        if isinstance(n, Group):
            raise SBR_ERROR(f"Use this operator without groups that get in the way '{n}'")
        t, alt = self.bin
        t += alt/2
        return t < n

    def __le__(self, n):
        if isinstance(n, Group):
            raise SBR_ERROR(f"Use this operator without groups that get in the way '{n}'")
        t, alt = self.bin
        t += alt/2
        return t <= n

    def __eq__(self, n):
        if isinstance(n, Group):
            raise SBR_ERROR(f"Use this operator without groups that get in the way '{n}'")
        t, alt = self.bin
        t += alt/2
        return t == n

    def __ne__(self, n):
        if isinstance(n, Group):
            raise SBR_ERROR(f"Use this operator without groups that get in the way '{n}'")
        t, alt = self.bin
        t += alt/2
        return t != n

    def __ge__(self, n):
        if isinstance(n, Group):
            raise SBR_ERROR(f"Use this operator without groups that get in the way '{n}'")
        t, alt = self.bin
        t += alt/2
        return t >= n

    def __gt__(self, n):
        if isinstance(n, Group):
            raise SBR_ERROR(f"Use this operator without groups that get in the way '{n}'")
        t, alt = self.bin
        t += alt/2
        return t > n

    def concatenate(self, data):
        return self+data

    def overlap(self, data):
        return self+data

    def ghost(self, data):
        return self-data



class Tones(Group):
    __name__ = "Tones"
    def __init__(self, data=""):
        if isinstance(data, (Group, Tones, list)):
            #verifique if it's chord or note
            for i in data: #organize sets
                if isinstance(i, (int, Note)):
                    self.append(Note(i))
                elif isinstance(i, list):
                    if len(i) == 0: continue
                    elif "." in repr(i):
                        raise SBR_ERROR(f"{self.__name__} don't accept floats itself")
                    self.append(i)

        elif isinstance(data, str):
            if not only_has(data, ",-0123456789b#"):
                raise SBR_ERROR(f"Invalid data {data} is {type(data).__name__} type")
            else:
                for i in delete_args(data.split(",")):
                    self.append(Note(i))
        else: raise SBR_ERROR(f"Invalid data {data} is {type(data).__name__} type")

    def reverse(self):
        return Tones(super().reverse())

    @property
    def int_list(self) -> list[int | list]:
        return [self.__int_list(n) for n in self]

    @property
    def one_dimention_int_list(self) -> list[int]:
        return one_dimention_list_recurtion(self.int_list)

    @property
    def min(self):
        return min(self.one_dimention_int_list)

    @property
    def max(self):
        return max(self.one_dimention_int_list)

    @property
    def separate_chors(self):
        new = []
        inter = repr(self.int_list).replace(
            "[" , "").replace("]" , "").replace(" " , "")
        for x in delete_args(inter.split(",")):
            if only_has(x, "-0123456789"):
                new.append(int(x))
        return new

    @property
    def arpeggiate(self):
        ...

    def __int_list(self, n):
        if isinstance(n, (int, Note)):
            return int(n)
        elif isinstance(n, (Group, list)):
            new = []
            for _n in n:
                new.append(self.__int_list(_n))
        else: raise
        return new

    def copy(self):
        return Tones(super().copy())

    def sub_to_set(self, s):
        if isinstance(s, list):
            if len(s) == 1:
                return self.sub_to_set(s[0])
            else: return s
        else: return s

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        #The method takes an average of the pitches,
        #subtracts it from the pitches, and prints it by adding
        #the octave effect with the most convenient octave argument
        #tones_array = self.separate_chors #calculate the average of the octave
        if len(self) == 0: return "M"
        #octave_average = round(sum(tones_array)/len(tones_array)/7)
        pw = "M"
        for i in self:
            i = self.sub_to_set(i)
            if isinstance(i, (int, Note)):
                pw += f"{Note(i)}, "
            elif isinstance(i, Group):
                pw += str(Group(i)).replace(" ", "")+",\xff"
        return pw[:-2].replace("\xff", "")

    def __str__(self):
        return self.__repr__()

    def __invert__(self):
        end = []
        for note in self:
            end.append(~note)
        return Tones(end)

    def __add__(self, data):
        #if is an integer
        if isinstance(data, int):
            return Tones(Group(self)+data)
        elif isinstance(data, (Group, list)):
            data = Tones(data)
        if isinstance(data, Tones):
            #calculate the largets number
            _old, _new = list(self), list(data)
            if len(_old) >= len(_new):
                for _ in range(len(_old)-len(_new)):
                    _new.append(None)
            elif len(self) < len(_new):
                for _ in range(len(_new)-len(self)):
                    _old.append(None)
            #slap tones
            g = Group()
            for i, data in enumerate(zip(_old, _new)):
                old, new = data
                if isinstance(old, Note) and isinstance(new, Note):
                    g.append(Group([old, new]))
                elif isinstance(old, Group) and isinstance(new, Note):
                    g.append(old)
                    g[i].append(new)
                elif old is None:
                    g.append(new)
                elif new is None:
                    g.append(old)
            return Tones(g)

    def __mul__(self, data):
        if isinstance(data, int):
            return Tones(super().__mul__(data))
        else: raise SBR_ERROR("function not yet implemented")

    def __sub__(self, data):
        i = Group(self)-data
        return Tones(i)

    def __iadd__(self, data):
        return self+data
    
    def __isub__(self, data):
        return self-data

    def concatenate(self, data):
        end = self.copy()
        for x in data:
            end.append(x)
        return Tones(end)

    def overlap(self, data):
        return self+data

    def ghost(self, data):
        return self-data




class Velocity(Group):
    __name__ = "Velocity"
    def __repr__(self):
        pw = "V"
        if not len(self):
            return pw
        for i in self:
            pw += f"{i},"
        return pw[:-1]

    def __str__(self):
        return self.__repr__()

    def __add__(self, data):
        i = Group(self)+data
        return Velocity(i)

    def __sub__(self, data):
        i = Group(self)-data
        return Velocity(i)

    def __mul__(self, data):
        return Velocity(super().__mul__(data))

    def __round__(self):
        return Velocity(super().__round__())

    def reverse(self):
        return Velocity(super().reverse())


class Times(Group):
    __name__ = "Times"
    def __repr__(self):
        pw = "T"
        if not len(self):
            return pw
        for i in self:
            pw += f"{i},"
        return pw[:-1]

    def __str__(self):
        return self.__repr__()

    def __add__(self, data):
        i = Group(self)+data
        return Times(i)

    def __sub__(self, data):
        i = Group(self)-data
        return Times(i)

    def __mul__(self, data):
        return Times(super().__mul__(data))

    def __round__(self):
        new = []
        for n in self:
            new.append(round(n))
        return Times(new)

    def reverse(self):
        return Times(super().reverse())

repr_sm = {}

class Melody():
    """
    The melodic symmetric philosophy
    organizes the priorities of the deepest
    attractions of the melody
    """
    __name__ = "Melody"
    def __init__(self, *data):
        if len(data) != 1:
            raise SBR_ERROR(
                f"An argument in {__name__} must be entered '1'" +
                f", not '{len(data)}'" if len(data) else "")
        elif not isinstance(data, (list, Group, tuple)):
            raise SBR_ERROR("argument no valid")
        self.rhythm, self.tones, self.vel, self.times = (
            Rhythm(), Tones(), Velocity(), Times())

        for d in data[0]:
            if type(d) is Rhythm: self.rhythm += d
            elif type(d) is Tones: self.tones += d
            elif type(d) is Velocity: self.vel += d
            elif type(d) is Times: self.times += d
            else: raise SBR_ERROR(
                f"Melody doesn't accept '{type(d).__name__}' as data type '{d}'")
        if len(self.tones) == 0:
            raise SBR_ERROR("Melody has empty tone data")
        if len(self.times) == 0: self.times = Times([.8])
        if len(self.vel) == 0: self.vel = Velocity([1])

    def __repr__(self, iters=2**0):
        rp_hash = hash(self.rhythm.bin)+hash(self.tones)
        if rp_hash in repr_sm:
            return repr_sm[rp_hash]

        pw = ""
        for d in (self.rhythm, self.tones, self.vel, self.times):
            if (len(d) <= 16 and type(d) == Rhythm or
                "6" in self.rhythm.bin or "3" in self.rhythm.bin): pw += f"{d}; "
            else:
                leng = len(d)
                for x in range(0, iters):
                    if d == L(L(d, x), leng):
                        if leng != x:
                            if not leng % x:
                                pw += f"{L(d, x)}*{leng//x}; "
                            elif leng < x: pw += f"{d}; "
                            else: pw += f"{L(d, x)}L{x}L{leng}; "
                            break
                else: pw += f"{d}; "

        repr_sm[rp_hash] = "Sm{"+pw[:-2]+"}"
        return repr(self)

    def __str__(self):
        return self.__repr__()

    def __iter__(self):
        i = 0
        end = []
        notes = L(self.tones, self.metric)
        vel = L(self.vel, self.metric)
        times = L(self.times, self.metric)
        for bit in self.rhythm:
            #(bit=int, notes=[], vel=[], time=[])
            if not bit: end.append((0, [], [], []))
            elif bit in (1, 5, 7, 9):
                end.append((bit, [notes[i]], [vel[i]], [times[i]]))
                i += 1

            elif bit in (3, 6):
                g_vel = [vel[i], vel[i+1], vel[i+2]]
                g_notes = [notes[i], notes[i+1], notes[i+2]]
                g_times = [times[i], times[i+1], times[i+2]]
                end.append((bit, g_notes, g_vel, g_times))
                i += 3

            elif bit in (2, 4, 8):
                g_vel = []
                g_notes = []
                g_times = []
                for x in range(bit):
                    g_vel.append(vel[i+x])
                    g_notes.append(notes[i+x])
                    g_times.append(times[i+x])
                end.append((bit, g_notes, g_vel, g_times))
                i += bit

        return (x for x in end)

    def reverse(self):
        return Melody([self.rhythm.reverse(), self.tones.reverse(),
                       self.vel.reverse(), self.times.reverse()])

    def __invert__(self):
        return Melody([self.rhythm, ~self.tones])


    def __len__(self):
        return len(self.rhythm)

    @property
    def metric(self):
        return self.rhythm.metric

    def __mul__(self, n):
        return Melody([self.rhythm*n, self.tones*n,
                       self.vel*n, self.times*n])

    def __add__(self, n):
        return Melody([self.rhythm, self.tones+n,
                       self.vel, self.times])

    def __sub__(self, n):
        return Melody([self.rhythm, self.tones-n,
                       self.vel, self.times])

    def concatenate(self, data):
        return self+data

    def overlap(self, data):
        return self+data

    def ghost(self, data):
        return self-data

class Polyrhythm(Group):
    __name__ = "Polyrhythm"
    def __init__(self, data):
        super().__init__()
        for item in data:
            if isinstance(item, (Rhythm, Instrument)):
                self.append(item)
            else: raise SBR_ERROR(
                f"Polyrhythm can only contain Rhythm or Instrument instances, not '{type(item).__name__}'")

    def __repr__(self):
        return "Poly" + super().__repr__()

    def __str__(self):
        return self.__repr__()


class Structure(Group):
    __name__ = "Structure"
    def __init__(self, data):
        super().__init__()
        for item in data:
            if isinstance(item, (Melody, Rhythm, Instrument, Velocity)):
                self.append(item)
            else: raise SBR_ERROR(
                f"Structure can only contain Melodies, Rhythms or Instruments, not '{type(item).__name__}'")

    def __repr__(self):
        return "Struct"+super().__repr__()

    def __str__(self):
        return self.__repr__()

    def __mul__(self, i):
        end = []
        for x in self:
            if isinstance(x, (Melody, Rhythm)):
                end.append(x*i)
            else: end.append(x)
        return Structure(end)

    def concatenate(self, data):
        if not isinstance(data, Structure):
            raise SBR_ERROR("This isn't a struct data")
        return self+data


#avaible path caracters
abc = "._/\\: abcdefghijklmnñopqrstuvwxyz áéíóú 0123456789"
abc += abc.upper()

class Instrument:
    def __init__(self, path, _id):
        if not only_has(path, abc): raise SBR_ERROR("path no valid")
        self.path = path
        self.inst_id = _id
        directory, name, extension = separate_path_extension(path)
        self.name = name.replace(" ", "_")
        if extension == "":
            self.type = "recorded"
        elif extension in {".wav", ".ogg", ".mp3", ".flac"}:
            self.type = "sampled"
        else: raise SBR_ERROR("Instrument or sample not valid")
        #type of instruments
        types =  ("synthesized", "sampled", "recorded", "plugin")

    def __repr__(self):
        return f"${self.inst_id}"# ${self.name} {self.type} instrument from '{self.path}'"

    def __str__(self):
        return f"${self.inst_id}"# \\{self.name}"

    def __add__(self, _):
        return self

    def __sub__(self, _):
        return self

    def path_note(self, cromatic_note: int) -> str:
        path_note = self.path+"/{:02d}".format(cromatic_note)+".wav"
        if not os.path.exists(path_note):
            print(f"This file doesn't exist: '{path_note}'")
        else: return path_note

    def calculate_interval(self, sm_tones: int) -> float:
        return 2**(sm_tones/12)

    def grade_to_cromatic(self, mode: Rhythm, tone: int, diatonic_tone: Note) -> int:
        mode = mode.scale
        octave = 0
        if isinstance(diatonic_tone, Note):
            diatonic_tone, alteration = diatonic_tone.bin
        else: diatonic_tone, alteration = diatonic_tone, 0
        grado = diatonic_tone + 1
        while grado > 7:
            octave += 1
            grado -= 7
        else:
            if grado <= 0: raise SBR_ERROR("Grade out of range")
            croma = mode[grado-8]+(octave*12)+tone-1
            return croma+alteration
