from collections import defaultdict
from functools import partial
import sys
from time import clock


from itertools import cycle
def mask1(mask, data):
    return bytes(a ^ b for a, b in zip(cycle(mask), data))


from wsaccel.xormask import XorMaskerSimple
def mask2(mask, data):
    return XorMaskerSimple(mask).process(data)


native_byteorder = sys.byteorder
def mask3(mask, data):
    datalen = len(data)
    data = int.from_bytes(data, native_byteorder)
    mask = int.from_bytes(mask * (datalen // 4) + mask[: datalen % 4], native_byteorder)
    return (data ^ mask).to_bytes(datalen, native_byteorder)


_XOR_TABLE = [bytes(a ^ b for a in range(256)) for b in range(256)]
def mask4(mask, data):
    data_bytes = bytearray(data)
    a, b, c, d = (_XOR_TABLE[n] for n in mask)
    data_bytes[::4] = data_bytes[::4].translate(a)
    data_bytes[1::4] = data_bytes[1::4].translate(b)
    data_bytes[2::4] = data_bytes[2::4].translate(c)
    data_bytes[3::4] = data_bytes[3::4].translate(d)
    return bytes(data)


def profile(mask_callable, max_time=0.5, max_iterations=1000):
    iterations = 0
    start_time = clock()
    while True:
        mask_callable()
        mask_callable()
        mask_callable()
        mask_callable()
        mask_callable()
        mask_callable()
        mask_callable()
        mask_callable()
        mask_callable()
        mask_callable()
        iterations += 10
        elapsed = clock() - start_time
        if elapsed > max_time or iterations > max_iterations:
            break
    time_per_loop = (elapsed / iterations) * 1000
    return time_per_loop


if __name__ == "__main__":

    mask_funcs = [
        #('simple', mask1),
        ('wsaccel', mask2),
        ('from_bytes', mask3),
        ('translate', mask4)
    ]
    results = defaultdict(list)

    mask = b'\0\1\2\3'
    for n in range(0, 32768 + 1, 256):
        data_size = max(1, n)
        print(data_size)
        data = b'\0' * data_size
        for name, masker in mask_funcs:
            results[name].append((
                data_size,
                profile(partial(masker, mask, data))
            ))

    import matplotlib.pyplot as plt
    names = sorted(results.keys())
    for name in names:
        plt.plot(
            [x for x, y in results[name]],
            [y for x, y in results[name]],
            label=name
        )
    plt.legend(names, loc='upper left')
    plt.show()

